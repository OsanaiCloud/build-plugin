# Osanai Build para Claude Code

Plugin que lleva a Osanai Build el contexto de tu producto desde tu Claude Code.

## Qué hace

- Lee tu carpeta en modo solo lectura y nunca abre ficheros con secretos.
- Te hace como máximo cinco preguntas.
- Te enseña el resumen y solo lo envía a Osanai Build si dices que sí de forma explícita, con el código OSN de un solo uso que te da la consola.

## Instalación

Necesitas acceso de lectura a este repositorio con tu cuenta de GitHub; Osanai te invita.

```bash
claude plugin marketplace add OsanaiCloud/build-plugin
claude plugin install osanai@osanai
```

Después, dentro de tu carpeta de producto: `/osanai:contexto <código>`.

## Otro servidor

Por defecto envía a `https://build.osanai.cloud`. Para apuntar a otro, lanza Claude Code con `OSANAI_BUILD_URL=<url>`.
