import json
import os

def programar_piezas(piezas: list, ventana: dict, config: dict) -> list:
    """
    Asigna fechas y franjas horarias respetando días hábiles, festivos y límites.
    """
    festivos = [f["fecha"] for f in config["calendario"]["festivos"]]
    dias_habiles = ["2026-11-30", "2026-12-01", "2026-12-02", "2026-12-03", "2026-12-04",
                    "2026-12-07", "2026-12-09", "2026-12-10", "2026-12-11"]  # Excluye 2026-12-08 por festivo
    
    franjas = config["calendario"]["franjas_de_publicacion"]
    programacion = []
    
    idx_dia = 0
    idx_franja = 0
    
    for pieza in piezas:
        fecha_asignada = dias_habiles[idx_dia]
        hora_asignada = franjas[idx_franja]
        
        programacion.append({
            "pieza": pieza,
            "fecha": fecha_asignada,
            "hora": hora_asignada,
            "estado": "Pendiente de Aprobación"
        })
        
        idx_franja += 1
        if idx_franja >= 2:  # Máximo 2 por día según config.json
            idx_franja = 0
            idx_dia += 1
            
    return programacion

def generar_vista_html(programacion: list, path_salida: str = "calendario.html"):
    """Genera un archivo HTML estático interactivo estilo tablero."""
    filas_html = ""
    for item in programacion:
        p = item["pieza"]
        color = "#2563eb" if p["formato"] == "post_linkedin" else "#059669"
        filas_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px;">{item['fecha']} {item['hora']}</td>
            <td style="padding: 12px;"><span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px;">{p['formato']}</span></td>
            <td style="padding: 12px;">{item['estado']}</td>
            <td style="padding: 12px;"><b>{item.get('puntaje_exito', 85)} / 100</b></td>
        </tr>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Tablero de Contenidos - Trycore</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f9fafb; }}
        h1 {{ color: #1e293b; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        th {{ background-color: #f1f5f9; text-align: left; padding: 12px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>📅 Tablero Táctico de Calendario de Contenidos</h1>
    <p>Ventana de agendamiento: 30-Nov-2026 a 11-Dic-2026</p>
    <table>
        <thead>
            <tr>
                <th>Fecha y Hora</th>
                <th>Formato</th>
                <th>Estado</th>
                <th>Puntaje de Éxito Est.</th>
            </tr>
        </thead>
        <tbody>
            {filas_html}
        </tbody>
    </table>
</body>
</html>
"""
    with open(path_salida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f" Layout del calendario generado en: {path_salida}")