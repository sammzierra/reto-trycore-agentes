import json
import os
import re

# ==========================================
# MÓDULO 1: DIAGNÓSTICO
# ==========================================
def ejecutar_diagnostico(texto_pieza_madre: str, config: dict) -> dict:
    num_caracteres = len(texto_pieza_madre)
    num_palabras = len(re.findall(r'\b\w+\b', texto_pieza_madre))
    num_parrafos = len([p for p in texto_pieza_madre.split('\n\n') if p.strip()])
    cifras_encontradas = re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', texto_pieza_madre)
    
    alertas = []
    for item in config.get("terminos_prohibidos", []):
        termino = item["termino"]
        if re.search(r'\b' + re.escape(termino) + r'\b', texto_pieza_madre, re.IGNORECASE):
            alertas.append(f"Término prohibido hallado: '{termino}' ({item.get('motivo')})")
            
    for nombre in config.get("nombres_confidenciales", []):
        if re.search(r'\b' + re.escape(nombre) + r'\b', texto_pieza_madre, re.IGNORECASE):
            alertas.append(f"Nombre confidencial hallado: '{nombre}'")
            
    productos_mencionados = [
        prod for prod in config.get("productos_vigentes", [])
        if re.search(r'\b' + re.escape(prod) + r'\b', texto_pieza_madre, re.IGNORECASE)
    ]

    return {
        "indicadores": {
            "caracteres": num_caracteres,
            "palabras": num_palabras,
            "parrafos": num_parrafos,
            "total_cifras_detectadas": len(cifras_encontradas),
            "productos_vigentes_detectados": productos_mencionados
        },
        "alertas": alertas,
        "apto_para_transformacion": len(alertas) == 0
    }

# ==========================================
# MÓDULO 2: TRANSFORMACIÓN
# ==========================================
def generar_post_linkedin(tema: str, config: dict) -> dict:
    gancho = "¿Sabías que optimizar tus procesos de negocio con ORIUNO puede ahorrar hasta un 40% del tiempo operativo?"
    desarrollo = (
        "Muchas empresas invierten cientos de horas en tareas repetitivas manuales. "
        "Con una estrategia clara de automatización, tu equipo puede enfocarse en lo que realmente genera valor comercial."
    )
    cta = "¿Quieres conocer más sobre cómo implementarlo en tu organización? Déjanos un comentario o escríbenos."
    utm_link = "https://trycore.com/blog?utm_source=linkedin&utm_medium=social-organico&utm_campaign=guia-rpa-202611&utm_content=post-1"
    
    contenido_completo = f"{gancho}\n\n{desarrollo}\n\n{cta}\n{utm_link}"
    
    return {
        "formato": "post_linkedin",
        "gancho": gancho,
        "desarrollo": desarrollo,
        "cta": cta,
        "utm_link": utm_link,
        "contenido_completo": contenido_completo,
        "longitud_caracteres": len(contenido_completo)
    }

def generar_newsletter(tema: str, config: dict) -> dict:
    asunto = "Optimiza tu operación sin tareas repetitivas este 2026"
    introduccion = "La automatización de procesos se ha consolidado como un pilar clave en las organizaciones eficientes."
    secciones = [
        {"subtitulo": "1. El reto operacional", "texto": "Identificar cuellos de botella es el primer paso hacia la eficiencia."},
        {"subtitulo": "2. Soluciones escalables", "texto": "Docfly facilita la gestión documental inteligente de extremo a extremo."},
        {"subtitulo": "3. Pasos para iniciar", "texto": "Comienza evaluando los procesos con mayor carga manual en tu área."}
    ]
    cta = "Agenda una sesión de diagnóstico con nuestros especialistas."
    utm_link = "https://trycore.com/blog?utm_source=newsletter&utm_medium=email&utm_campaign=guia-rpa-202611&utm_content=newsletter-1"
    
    return {
        "formato": "newsletter",
        "asunto": asunto,
        "introduccion": introduccion,
        "secciones": secciones,
        "cta": cta,
        "utm_link": utm_link
    }

# ==========================================
# MÓDULO 3: CALENDARIO Y VISTA HTML
# ==========================================
def programar_piezas(piezas: list, ventana: dict, config: dict) -> list:
    dias_habiles = ["2026-11-30", "2026-12-01", "2026-12-02", "2026-12-03", "2026-12-04",
                    "2026-12-07", "2026-12-09", "2026-12-10", "2026-12-11"]
    
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
        if idx_franja >= 2:
            idx_franja = 0
            idx_dia += 1
            
    return programacion
def generar_vista_html(programacion: list, path_salida: str = "calendario.html"):
    filas_html = ""
    for item in programacion:
        p = item["pieza"]
        color = "#2563eb" if p["formato"] == "post_linkedin" else "#059669"
        filas_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px;">{item['fecha']} {item['hora']}</td>
            <td style="padding: 12px;"><span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px;">{p['formato']}</span></td>
            <td style="padding: 12px;">{item['estado']}</td>
            <td style="padding: 12px;"><b>{p.get('puntaje_exito', 85)} / 100</b></td>
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

# ==========================================
# MÓDULO 4: PUNTAJE DE ÉXITO
# ==========================================
def calcular_puntaje_exito(pieza: dict) -> int:
    score = 50
    if "gancho" in pieza and len(pieza["gancho"]) > 20:
        score += 15
    if "utm_link" in pieza or "utm_source" in str(pieza):
        score += 15
    if pieza.get("formato") == "carrusel_linkedin":
        score += 20
    elif pieza.get("formato") == "post_linkedin":
        score += 15
    return min(score, 100)

# ==========================================
# INICIO Y EJECUCIÓN DEL SISTEMA
# ==========================================
def cargar_configuracion():
    path_config = os.path.join("insumos", "config.json")
    path_ventana = os.path.join("insumos", "ventana.json")
    
    with open(path_config, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    with open(path_ventana, "r", encoding="utf-8") as f:
        ventana = json.load(f)
        
    return config, ventana

if __name__ == "__main__":
    print("🚀 Ejecutando Sistema Táctico de Contenidos Trycore...\n")
    config, ventana = cargar_configuracion()
    
    texto_ejemplo = """
    Guía de Automatización con RPA en la empresa.
    La automatización permite optimizar operaciones reduciendo costos y errores humanos.
    Con herramientas como ORIUNO y Docfly, las organizaciones aceleran su transformación digital.
    """
    
    print("--- 1. DIAGNÓSTICO DE PIEZA MADRE ---")
    diag = ejecutar_diagnostico(texto_ejemplo, config)
    print(f"Indicadores: {diag['indicadores']}")
    print(f"Alertas encontradas: {diag['alertas']}\n")
    
    print("--- 2. TRANSFORMACIÓN DE FORMATOS ---")
    post = generar_post_linkedin("RPA y Eficiencia", config)
    newsletter = generar_newsletter("RPA y Eficiencia", config)
    piezas = [post, newsletter]
    
    print("--- 3. CÁLCULO DE PUNTAJE DE ÉXITO ---")
    for p in piezas:
        p["puntaje_exito"] = calcular_puntaje_exito(p)
        print(f"Pieza [{p['formato']}]: Puntaje = {p['puntaje_exito']}/100")
    print()
    
    print("--- 4. PROGRAMACIÓN Y VISTA WEB ---")
    programacion = programar_piezas(piezas, ventana, config)
    generar_vista_html(programacion)
    
    print("\n Proceso completado con éxito. Abre 'calendario.html' en tu navegador.")