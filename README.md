# Osanai Build para Claude Code

El Asistente de Osanai Build: trae tu producto a Build desde tu Claude Code.

## Qué hace

- Se conecta con tu proyecto en Osanai Build usando el código que te da la consola.
- Lee tu carpeta en modo solo lectura (nunca abre ficheros con secretos), te hace en la terminal las preguntas que tu código no responde y te enseña los textos de la entrevista para que los aceptes.
- Con tu permiso, arranca tu app en local y sube capturas de sus pantallas.
- Las preguntas y los textos los decide Osanai Build; el plugin solo hace de puente.

## Instalación

```bash
claude plugin marketplace add OsanaiCloud/build-plugin
claude plugin install osanai@osanai
```

Después, abre una sesión nueva de Claude Code en la carpeta de tu producto y pega el comando que te da Build: `/osanai:asistente <código>`.
