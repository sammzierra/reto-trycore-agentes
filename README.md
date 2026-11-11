# Sistema Táctico de Calendario y Transformación de Contenidos - Trycore

Este sistema automatiza la evaluación, transformación, puntuación y agendamiento de piezas de marketing a partir de una pieza madre (URL o texto base), cumpliendo estrictamente con las políticas de negocio y restricciones del equipo de Mercadeo de Trycore.

---

## Arquitectura y Módulos del Sistema

El núcleo está implementado en Python (`main.py`) y se divide en cuatro fases independientes:

1. **Diagnóstico Automatizado (`ejecutar_diagnostico`):**
   - Obtiene la pieza madre desde su origen (con soporte de respaldo local en HTML).
   - Calcula indicadores medibles clave (cantidad de caracteres, palabras, párrafos y cifras detectadas).
   - Valida reglas contra `config.json`: verifica productos vigentes (`Docfly`, `ORIUNO`), bloquea términos prohibidos y previene el uso de nombres confidenciales.

2. **Transformación Multi-formato (`generar_post_linkedin` / `generar_newsletter`):**
   - Genera piezas derivadas redactadas y estructuradas por secciones (gancho, cuerpo, llamado a la acción) sin requerir diseño gráfico.
   - Incorpora parámetros UTM obligatorios para trazabilidad según la convención definida.

3. **Puntuación de Éxito (`calcular_puntaje_exito`):**
   - Calcula una calificación estimada de **0 a 100** apoyada en criterios objetivos (estructura del gancho, presencia de enlaces trazables y peso histórico del formato).

4. **Calendario y Vista Web (`programar_piezas` / `generar_vista_html`):**
   - Distribuye las piezas aprobadas dentro de la ventana del **30-Nov-2026 al 11-Dic-2026**.
   - Respeta días hábiles, excluye festivos (ej. 08-Dic-2026) y limita la saturación a un máximo de 2 piezas por día.
   - Genera automáticamente el tablero web interactivo **`calendario.html`** para revisión y aprobación humana.

---

## Requisitos e Instalación

- **Python 3.10+**
- **Cero dependencias externas de pago:** El proyecto funciona únicamente utilizando librerías estándar de Python (`json`, `os`, `re`, `unittest`).

---

## Instrucciones de Ejecución

1. Clona o abre la carpeta del repositorio en tu terminal:
   ```bash
   cd reto-trycore-agentes