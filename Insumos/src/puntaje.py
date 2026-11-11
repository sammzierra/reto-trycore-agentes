def calcular_puntaje_exito(pieza: dict) -> int:
    """
    Calcula una puntuación de 0 a 100 basada en criterios de estructura e historial.
    """
    score = 50  # Base
    
    # 1. Gancho atractivo (+15 pts)
    if "gancho" in pieza and len(pieza["gancho"]) > 20:
        score += 15
        
    # 2. Presencia de UTMs en enlaces (+15 pts)
    if "utm_link" in pieza or "utm_source" in str(pieza):
        score += 15
        
    # 3. Formato con alto rendimiento histórico (+20 pts)
    if pieza.get("formato") == "carrusel_linkedin":
        score += 20
    elif pieza.get("formato") == "post_linkedin":
        score += 15
        
    return min(score, 100)