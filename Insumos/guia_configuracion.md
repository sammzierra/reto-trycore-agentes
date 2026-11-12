# Guía del archivo de configuración

> **Caso ficticio con fines de evaluación.** Las reglas, los nombres de clientes, las cifras y los ejemplos de este paquete son inventados para el reto.

El archivo `config.json` reúne las reglas de Mercadeo. Tu sistema debe leerlas de ahí: si mañana cambia una regla, solo debería cambiar el archivo, no tu código.

| Sección | Qué contiene | Para qué la usas |
| --- | --- | --- |
| `productos_vigentes` | Los productos que se pueden mencionar | Cualquier otro nombre de producto se marca para revisión |
| `terminos_prohibidos` | Términos y frases que no pueden aparecer, con su motivo | Validar cada pieza derivada |
| `nombres_confidenciales` | Nombres de clientes que no se pueden publicar | Validar cada pieza derivada |
| `utm` | La convención de parámetros para los enlaces | Construir el enlace de cada pieza |
| `matriz_formatos` | La ficha de cada formato: canal, longitud, estructura, técnicas de redacción, lo que necesita de la pieza madre y cuántos caben por semana | Decidir qué formatos aplican, redactar cada pieza con la estructura y las técnicas de su formato, y validarla |
| `calendario` | Días hábiles, franjas de publicación, capacidad por día y por semana, separación mínima entre piezas del mismo tema y festivos | Programar las piezas |

Algunas aclaraciones:

- La transformación a cada formato entrega contenido redactado y estructurado por partes (por ejemplo, de un carrusel: portada, láminas internas y cierre). No incluye diseño gráfico.
- El historial de publicaciones es ficticio: son datos simulados para el reto.
- Las fechas del historial siguen el formato colombiano: día, mes y año.
- En la matriz de formatos, el campo `ejemplo` muestra cómo se ha hecho ese formato antes. No es una plantilla aprobada.
- La separación mínima entre piezas del mismo tema se cuenta en horas de calendario, incluidos fines de semana y festivos.
- Las piezas que ya están en `calendario_ocupado.csv` cuentan para la capacidad y para la separación por tema.
- Tu ventana de calendario está en `ventana.json`. Tu programa debe recibirla como entrada, igual que la pieza madre, el historial y este archivo.
