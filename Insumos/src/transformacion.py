def generar_post_linkedin(tema: str, config: dict) -> dict:
    """Genera una pieza redactada para LinkedIn cumpliendo las reglas del formato."""
    gancho = f"¿Sabías que automatizar tus procesos de negocio con ORIUNO puede optimizar hasta un 40% del tiempo operativo?"
    desarrollo = (
        "Muchas empresas invierten cientos de horas en tareas repetitivas manuales. "
        "Con una estrategia clara de automatización de procesos, tu equipo puede enfocarse en lo que realmente genera valor comercial."
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
    """Genera una pieza estructurada para Newsletter cumpliendo las reglas del formato."""
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