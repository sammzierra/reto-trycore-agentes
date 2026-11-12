import json
import re

def ejecutar_diagnostico(texto_pieza_madre: str, config: dict) -> dict:
    """
    Evalúa la pieza madre midiendo al menos 4 indicadores y buscando alertas según config.json.
    """
    # 1. Indicadores medibles
    num_caracteres = len(texto_pieza_madre)
    num_palabras = len(re.findall(r'\b\w+\b', texto_pieza_madre))
    num_parrafos = len([p for p in texto_pieza_madre.split('\n\n') if p.strip()])
    cifras_encontradas = re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', texto_pieza_madre)
    
    # 2. Búsqueda de alertas / Reglas de config.json
    alertas = []
    
    # Términos prohibidos
    for item in config.get("terminos_prohibidos", []):
        termino = item["termino"]
        if re.search(r'\b' + re.escape(termino) + r'\b', texto_pieza_madre, re.IGNORECASE):
            alertas.append(f"Término prohibido hallado: '{termino}' ({item.get('motivo')})")
            
    # Nombres confidenciales
    for nombre in config.get("nombres_confidenciales", []):
        if re.search(r'\b' + re.escape(nombre) + r'\b', texto_pieza_madre, re.IGNORECASE):
            alertas.append(f"Nombre confidencial hallado: '{nombre}'")
            
    # Productos vigentes mencionados
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