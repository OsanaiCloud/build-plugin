#!/usr/bin/env python3
"""Send the context the founder's Claude wrote to Build.

Usage: python3 enviar.py OSN-XXXX-XXXX  < context.json

stdin is `{"source": {"tool", "repo"}, "context": {...sections}}`; the code
travels as an argument and is added here. Standard library only: this runs
with whatever python3 the founder has (macOS ships 3.9).

Exit codes: 0 sent; 1 not sent, the JSON is saved in the system temp folder
for the manual upload; 2 unusable input, nothing sent and nothing saved.
"""
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request

ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # same as Build's codes
DEFAULT_URL = "https://build.osanai.cloud"
TIMEOUT = 30


def normalize(raw):
    """The canonical code, or None. Mirrors Build's check so a bad code never
    reaches the network nor a file name."""
    code = raw.strip().upper()
    parts = code.split("-")
    if (len(code) != 13 or len(parts) != 3 or parts[0] != "OSN"
            or any(len(p) != 4 or any(c not in ALPHABET for c in p) for p in parts[1:])):
        return None
    return code


def read_payload(text):
    """The body to send minus the code, or None if it cannot be one."""
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("context"), dict):
        return None
    if not isinstance(data.get("source"), dict):
        data["source"] = {"tool": "Claude Code",
                          "repo": os.path.basename(os.getcwd()) or "desconocido"}
    return {"source": data["source"], "context": data["context"]}


def save(code, payload):
    """The fallback file, private to the user, never in the founder's folder."""
    path = os.path.join(tempfile.gettempdir(), "osanai-contexto-%s.json" % code)
    # O_NOFOLLOW: a symlink planted at this name in a shared temp folder is refused.
    # Not every platform has it (Windows): there the plain open is the best we have.
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    if hasattr(os, "fchmod"):
        os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def build_message(error):
    """Build's Spanish message from an error response, if it sent one."""
    try:
        body = json.loads(error.read().decode("utf-8"))
        if isinstance(body, dict) and isinstance(body.get("message"), str):
            return body["message"]
    except (ValueError, UnicodeDecodeError, OSError):
        pass
    return "Build ha respondido con un error (%s)." % error.code


def project_name(raw):
    try:
        body = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    name = body.get("project_name") if isinstance(body, dict) else None
    return name if isinstance(name, str) and name.strip() else None


def fail(code, payload, reason):
    try:
        path = save(code, payload)
    except OSError as exc:
        print("No se ha enviado: %s\nTampoco he podido guardar el fichero (%s)." % (reason, exc),
              file=sys.stderr)
        return 1
    print("No se ha enviado: %s\nHe guardado el contexto en %s\n"
          "Súbelo en Build con «Subir el fichero a mano»." % (reason, path), file=sys.stderr)
    return 1


def main(argv):
    code = normalize(argv[1]) if len(argv) == 2 else None
    if code is None:
        print("El código no tiene la forma OSN-XXXX-XXXX. Cópialo de Build.", file=sys.stderr)
        return 2
    try:
        text = sys.stdin.buffer.read().decode("utf-8")
    except UnicodeDecodeError:
        text = None
    payload = read_payload(text) if text is not None else None
    if payload is None:
        print("El contexto no es un JSON con la sección «context». No se ha enviado nada.",
              file=sys.stderr)
        return 2
    url = os.environ.get("OSANAI_BUILD_URL", DEFAULT_URL).rstrip("/") + "/api/context"
    data = json.dumps(dict(payload, code=code), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        return fail(code, payload, build_message(exc))
    except (urllib.error.URLError, OSError) as exc:
        return fail(code, payload, "No he podido conectar con Build en %s (%s)." % (url, exc))
    # A 2xx means Build took it and spent the code: never fall back from here.
    name = project_name(raw)
    if name:
        print("Contexto enviado a Osanai Build, proyecto «%s». Vuelve a Build para seguir." % name)
    else:
        print("Enviado; Build no devolvió el nombre del proyecto. Vuelve a Build para seguir.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
