import csv
import html as html_lib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta


# ==========================================
# UTILIDAD: OBTENER Y LIMPIAR PIEZA MADRE
# ==========================================
def limpiar_html(contenido: str) -> str:
    sin_scripts = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", contenido, flags=re.DOTALL | re.IGNORECASE)
    sin_tags = re.sub(r"<[^>]+>", "\n", sin_scripts)
    texto = html_lib.unescape(sin_tags)
    lineas = [re.sub(r"\s+", " ", l).strip() for l in texto.splitlines() if l.strip()]
    return "\n\n".join(lineas)


def obtener_pieza_madre(ruta_entrada: str = None) -> tuple[str, str]:
    """
    Obtiene la pieza madre desde:
    1) Un archivo pasado por argumento (ideal para la sustentación con otra pieza madre).
    2) url.txt en insumos (con respaldo automático en guia_rpa_respaldo.html si falla la red).
    """
    if ruta_entrada and os.path.exists(ruta_entrada):
        with open(ruta_entrada, "r", encoding="utf-8") as f:
            raw = f.read()
        texto = limpiar_html(raw) if "<html" in raw.lower() or "<p>" in raw.lower() else raw.strip()
        return texto, f"Archivo local: {ruta_entrada}"

    # Buscar carpetas posibles de insumos
    bases = ["insumos", "02_insumos"]
    url_file = None
    respaldo_file = None
    for b in bases:
        for sub in ["", "pieza_madre"]:
            cand_url = os.path.join(b, sub, "url.txt") if sub else os.path.join(b, "url.txt")
            cand_resp = os.path.join(b, sub, "guia_rpa_respaldo.html") if sub else os.path.join(b, "guia_rpa_respaldo.html")
            if os.path.exists(cand_url):
                url_file = cand_url
            if os.path.exists(cand_resp):
                respaldo_file = cand_resp

    if url_file:
        with open(url_file, "r", encoding="utf-8") as f:
            url = f.read().strip()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                raw_html = resp.read().decode("utf-8", errors="ignore")
            texto = limpiar_html(raw_html)
            if len(texto) > 200:
                return texto, f"URL descargada en vivo: {url}"
        except Exception as e:
            print(f"[AVISO] No se pudo descargar desde URL ({e}). Usando respaldo local...")

    if respaldo_file and os.path.exists(respaldo_file):
        with open(respaldo_file, "r", encoding="utf-8") as f:
            raw_html = f.read()
        return limpiar_html(raw_html), f"Respaldo local HTML: {respaldo_file}"

    raise FileNotFoundError("No se encontró ni url.txt accesible ni archivo de respaldo de la pieza madre.")


def generar_slug(texto: str) -> str:
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    limpio = texto.lower()
    for k, v in reemplazos.items():
        limpio = limpio.replace(k, v)
    limpio = re.sub(r"[^a-z0-9\s-]", "", limpio)
    palabras = [p for p in limpio.split() if len(p) > 2][:4]
    return "-".join(palabras) or "campana-contenido"


# ==========================================
# MÓDULO 1: DIAGNÓSTICO
# ==========================================
def ejecutar_diagnostico(texto_pieza_madre: str, config: dict) -> dict:
    num_caracteres = len(texto_pieza_madre)
    num_palabras = len(re.findall(r"\b\w+\b", texto_pieza_madre))
    parrafos = [p.strip() for p in texto_pieza_madre.split("\n\n") if p.strip()]
    num_parrafos = len(parrafos)
    cifras_encontradas = re.findall(r"\b\d+(?:[\.,]\d+)?%?\b", texto_pieza_madre)

    alertas = []
    for item in config.get("terminos_prohibidos", []):
        termino = item["termino"] if isinstance(item, dict) else str(item)
        motivo = item.get("motivo", "Regla de marca") if isinstance(item, dict) else "Regla de marca"
        if re.search(r"\b" + re.escape(termino) + r"\b", texto_pieza_madre, re.IGNORECASE):
            alertas.append(f"Término prohibido hallado: '{termino}' ({motivo})")

    for nombre in config.get("nombres_confidenciales", []):
        if re.search(r"\b" + re.escape(nombre) + r"\b", texto_pieza_madre, re.IGNORECASE):
            alertas.append(f"Nombre confidencial hallado: '{nombre}'")

    productos_mencionados = [
        prod for prod in config.get("productos_vigentes", [])
        if re.search(r"\b" + re.escape(prod) + r"\b", texto_pieza_madre, re.IGNORECASE)
    ]

    if not productos_mencionados:
        alertas.append("Advertencia: No se detectó ningún producto vigente de Trycore en la pieza madre.")

    if cifras_encontradas:
        alertas.append(f"Revisión requerida: Se detectaron {len(cifras_encontradas)} cifras; verificar fuente exacta antes de publicar.")

    return {
        "indicadores": {
            "caracteres": num_caracteres,
            "palabras": num_palabras,
            "parrafos": num_parrafos,
            "total_cifras_detectadas": len(cifras_encontradas),
            "cifras_detalle": cifras_encontradas[:10],
            "productos_vigentes_detectados": productos_mencionados,
        },
        "alertas": alertas,
        "apto_para_transformacion": not any("prohibido" in a.lower() or "confidencial" in a.lower() for a in alertas),
    }


# ==========================================
# MÓDULO 2: TRANSFORMACIÓN DINÁMICA
# ==========================================
def extraer_bloques_texto(texto_pieza_madre: str) -> tuple[str, list[str]]:
    parrafos = [p.strip() for p in texto_pieza_madre.split("\n\n") if len(p.strip()) > 15]
    titulo = parrafos[0][:90] if parrafos else "Soluciones Empresariales Trycore"
    cuerpo = parrafos[1:] if len(parrafos) > 1 else parrafos
    return titulo, cuerpo


def construir_utm(canal: str, medio: str, slug_campana: str, contenido: str, config: dict) -> str:
    utm_cfg = config.get("utm", {})
    base_url = utm_cfg.get("url_base", "https://trycore.com/blog")
    return (
        f"{base_url}?utm_source={canal.lower()}&utm_medium={medio.lower()}"
        f"&utm_campaign={slug_campana}&utm_content={contenido.lower()}"
    )


def generar_post_linkedin(texto_pieza_madre: str, config: dict) -> dict:
    titulo, cuerpo = extraer_bloques_texto(texto_pieza_madre)
    slug = generar_slug(titulo)

    primera_idea = cuerpo[0] if cuerpo else titulo
    segunda_idea = cuerpo[1] if len(cuerpo) > 1 else ""

    gancho = f"¿Cómo abordar {titulo.rstrip('.')} sin frenar la operación de tu equipo?"[:140]
    desarrollo = f"{primera_idea[:260]} {segunda_idea[:220]}".strip()
    cta = "Conoce los detalles completos y evalúa cómo aplicarlo en tu organización aquí:"
    utm_link = construir_utm("linkedin", "social-organico", slug, "post-1", config)

    contenido_completo = f"{gancho}\n\n{desarrollo}\n\n{cta}\n{utm_link}"

    return {
        "formato": "post_linkedin",
        "tema": titulo,
        "gancho": gancho,
        "desarrollo": desarrollo,
        "cta": cta,
        "utm_link": utm_link,
        "contenido_completo": contenido_completo,
        "longitud_caracteres": len(contenido_completo),
    }


def generar_newsletter(texto_pieza_madre: str, config: dict) -> dict:
    titulo, cuerpo = extraer_bloques_texto(texto_pieza_madre)
    slug = generar_slug(titulo)

    asunto = f"Claves prácticas: {titulo[:55]}"
    introduccion = cuerpo[0][:240] if cuerpo else titulo

    secciones = []
    for idx in range(3):
        texto_sec = cuerpo[idx + 1][:220] if len(cuerpo) > idx + 1 else (cuerpo[-1][:220] if cuerpo else titulo)
        secciones.append({
            "subtitulo": f"{idx + 1}. Punto clave sobre {titulo[:35]}",
            "texto": texto_sec,
        })

    cta = "Agenda una sesión de diagnóstico con el equipo de Trycore."
    utm_link = construir_utm("newsletter", "email", slug, "newsletter-1", config)

    return {
        "formato": "newsletter",
        "tema": titulo,
        "asunto": asunto,
        "introduccion": introduccion,
        "secciones": secciones,
        "cta": cta,
        "utm_link": utm_link,
    }


# ==========================================
# MÓDULO 3: PUNTAJE DE ÉXITO BASADO EN DATOS
# ==========================================
def calcular_puntaje_exito(pieza: dict, historial: list = None) -> int:
    score = 50

    # 1. Apoyo en historial de publicaciones pasadas (si existe)
    if historial:
        formato_actual = pieza.get("formato", "").lower()
        coincidencias = [
            h for h in historial
            if formato_actual.split("_")[0] in str(h.get("formato", "")).lower()
        ]
        if coincidencias:
            tasas = []
            for h in coincidencias:
                for clave in ["tasa_interaccion", "engagement", "ctr", "interacciones"]:
                    if clave in h and str(h[clave]).replace(".", "", 1).isdigit():
                        tasas.append(float(h[clave]))
                        break
            if tasas:
                promedio = sum(tasas) / len(tasas)
                score += min(int(promedio * 4), 20)
            else:
                score += 10

    # 2. Criterios estructurales verificables
    if "gancho" in pieza and 20 < len(pieza["gancho"]) <= 140:
        score += 15
    if "utm_link" in pieza and "utm_source=" in pieza["utm_link"]:
        score += 15
    if pieza.get("formato") == "carrusel_linkedin":
        score += 10
    elif pieza.get("formato") == "post_linkedin":
        score += 5

    return max(0, min(score, 100))


# ==========================================
# MÓDULO 4: CALENDARIO Y VISTA HTML
# ==========================================
def obtener_dias_habiles(ventana: dict, config: dict) -> list[str]:
    inicio_str = ventana.get("fecha_inicio", "2026-11-30")
    fin_str = ventana.get("fecha_fin", "2026-12-11")
    festivos = set(config.get("calendario", {}).get("festivos", ["2026-12-08"]))

    actual = datetime.strptime(inicio_str, "%Y-%m-%d")
    fin = datetime.strptime(fin_str, "%Y-%m-%d")
    habiles = []

    while actual <= fin:
        fecha_iso = actual.strftime("%Y-%m-%d")
        if actual.weekday() < 5 and fecha_iso not in festivos:
            habiles.append(fecha_iso)
        actual += timedelta(days=1)

    return habiles


def programar_piezas(piezas: list, ventana: dict, config: dict, ocupados: list = None) -> list:
    dias_habiles = obtener_dias_habiles(ventana, config)
    cal_cfg = config.get("calendario", {})
    franjas = cal_cfg.get("franjas_de_publicacion", ["09:00", "15:00"])
    max_por_dia = cal_cfg.get("capacidad_max_por_dia", 2)
    sep_min_dias = cal_cfg.get("separacion_minima_dias_mismo_tema", 2)

    ocupados = ocupados or []
    slots_ocupados = {(o.get("fecha", "").strip(), o.get("hora", "").strip()) for o in ocupados}
    conteo_por_dia = {}
    for o in ocupados:
        f = o.get("fecha", "").strip()
        if f:
            conteo_por_dia[f] = conteo_por_dia.get(f, 0) + 1

    ultima_fecha_tema = {}
    programacion = []

    for pieza in piezas:
        tema = pieza.get("tema", "General")
        asignado = False

        for dia in dias_habiles:
            if conteo_por_dia.get(dia, 0) >= max_por_dia:
                continue

            if tema in ultima_fecha_tema:
                d_prev = datetime.strptime(ultima_fecha_tema[tema], "%Y-%m-%d")
                d_curr = datetime.strptime(dia, "%Y-%m-%d")
                if (d_curr - d_prev).days < sep_min_dias:
                    continue

            for hora in franjas:
                if (dia, hora) not in slots_ocupados:
                    slots_ocupados.add((dia, hora))
                    conteo_por_dia[dia] = conteo_por_dia.get(dia, 0) + 1
                    ultima_fecha_tema[tema] = dia
                    programacion.append({
                        "pieza": pieza,
                        "fecha": dia,
                        "hora": hora,
                        "estado": "Pendiente de Aprobación",
                        "conflicto": None,
                    })
                    asignado = True
                    break
            if asignado:
                break

        if not asignado:
            programacion.append({
                "pieza": pieza,
                "fecha": "SIN ASIGNAR",
                "hora": "--:--",
                "estado": "Conflicto / Sin Cupo",
                "conflicto": "No se encontró franja hábil cumpliendo separación mínima y capacidad diaria.",
            })

    return programacion


def generar_vista_html(programacion: list, diag: dict, origen: str, path_salida: str = "calendario.html"):
    filas_html = ""
    for item in programacion:
        p = item["pieza"]
        es_conflicto = item.get("conflicto") is not None
        color = "#dc2626" if es_conflicto else ("#2563eb" if p["formato"] == "post_linkedin" else "#059669")
        bg_fila = "#fef2f2" if es_conflicto else "#ffffff"
        nota_conflicto = f"<br><small style='color:#b91c1c;'>⚠ {item['conflicto']}</small>" if es_conflicto else ""

        filas_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb; background-color: {bg_fila};">
            <td style="padding: 12px;"><b>{item['fecha']}</b> {item['hora']}</td>
            <td style="padding: 12px;"><span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 13px;">{p['formato']}</span></td>
            <td style="padding: 12px;">{p.get('tema', 'N/A')}</td>
            <td style="padding: 12px;">{item['estado']}{nota_conflicto}</td>
            <td style="padding: 12px;"><b>{p.get('puntaje_exito', 0)} / 100</b></td>
        </tr>
        """

    alertas_html = "".join(f"<li>{a}</li>" for a in diag.get("alertas", [])) or "<li>Sin alertas críticas detectadas.</li>"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Tablero Táctico de Contenidos - Trycore</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 36px; background-color: #f8fafc; color: #1e293b; }}
        .card {{ background: white; padding: 18px 22px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.08); }}
        th {{ background-color: #e2e8f0; text-align: left; padding: 12px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Tablero Táctico de Calendario de Contenidos</h1>
    <div class="card">
        <p><b>Origen de pieza madre:</b> {origen}</p>
        <p><b>Ventana:</b> 30-Nov-2026 a 11-Dic-2026 (Excluye fines de semana y festivo 08-Dic-2026)</p>
        <p><b>Alertas de diagnóstico para revisión humana:</b></p>
        <ul>{alertas_html}</ul>
    </div>
    <table>
        <thead>
            <tr>
                <th>Fecha y Hora</th>
                <th>Formato</th>
                <th>Tema</th>
                <th>Estado</th>
                <th>Puntaje Est.</th>
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
    print(f"Vista del calendario generada en: {path_salida}")


# ==========================================
# CARGA DE INSUMOS E INICIO DEL SISTEMA
# ==========================================
def buscar_archivo(nombre_archivo: str) -> str | None:
    for raiz in ["insumos", "02_insumos", "."]:
        for sub in ["", "configuracion", "calendario", "historial", "pieza_madre"]:
            ruta = os.path.join(raiz, sub, nombre_archivo) if sub else os.path.join(raiz, nombre_archivo)
            if os.path.exists(ruta):
                return ruta
    return None


def cargar_csv_si_existe(ruta: str | None) -> list:
    if not ruta or not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        muestra = f.read(1024)
        f.seek(0)
        delimitador = ";" if muestra.count(";") > muestra.count(",") else ","
        return list(csv.DictReader(f, delimiter=delimitador))


def cargar_insumos():
    ruta_config = buscar_archivo("config.json")
    ruta_ventana = buscar_archivo("ventana.json")
    if not ruta_config or not ruta_ventana:
        raise FileNotFoundError("No se encontraron config.json o ventana.json en la carpeta de insumos.")

    with open(ruta_config, "r", encoding="utf-8") as f:
        config = json.load(f)
    with open(ruta_ventana, "r", encoding="utf-8") as f:
        ventana = json.load(f)

    ocupados = cargar_csv_si_existe(buscar_archivo("calendario_ocupado.csv"))

    # Buscar cualquier archivo de historial (csv o json)
    historial = []
    for carpeta in ["insumos", "02_insumos", os.path.join("insumos", "historial"), os.path.join("02_insumos", "historial")]:
        if os.path.isdir(carpeta):
            for archivo in os.listdir(carpeta):
                if "historial" in archivo.lower():
                    full = os.path.join(carpeta, archivo)
                    if archivo.endswith(".csv"):
                        historial = cargar_csv_si_existe(full)
                    elif archivo.endswith(".json"):
                        with open(full, "r", encoding="utf-8") as fh:
                            historial = json.load(fh)

    return config, ventana, ocupados, historial

def cargar_configuracion():
    """Función puente para compatibilidad con test_sistema.py"""
    config, ventana, _, _ = cargar_insumos()
    return config, ventana

if __name__ == "__main__":
    print("Ejecutando Sistema Táctico de Contenidos Trycore...\n")
    ruta_arg = sys.argv[1] if len(sys.argv) > 1 else None

    config, ventana, ocupados, historial = cargar_insumos()
    texto_madre, origen = obtener_pieza_madre(ruta_arg)

    print(f"Fuente cargada: {origen}\n")
    print("--- 1. DIAGNÓSTICO DE PIEZA MADRE ---")
    diag = ejecutar_diagnostico(texto_madre, config)
    print(f"Indicadores: {diag['indicadores']}")
    print(f"Alertas encontradas: {diag['alertas']}\n")

    print("--- 2. TRANSFORMACIÓN DE FORMATOS ---")
    post = generar_post_linkedin(texto_madre, config)
    newsletter = generar_newsletter(texto_madre, config)
    piezas = [post, newsletter]

    print("--- 3. CÁLCULO DE PUNTAJE DE ÉXITO ---")
    for p in piezas:
        p["puntaje_exito"] = calcular_puntaje_exito(p, historial)
        print(f"Pieza [{p['formato']}]: Puntaje = {p['puntaje_exito']}/100")
    print()

    print("--- 4. PROGRAMACIÓN Y VISTA WEB ---")
    programacion = programar_piezas(piezas, ventana, config, ocupados)
    generar_vista_html(programacion, diag, origen)

    print("\nProceso completado con éxito. Abre 'calendario.html' en tu navegador.")