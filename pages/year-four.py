import io
from datetime import date

import streamlit as st
from PIL import Image
from supabase import create_client, Client

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

st.set_page_config(page_title="Year Four", page_icon="📷", layout="centered")

BUCKET = "year_four_fotos"
TABLA = "year_four_fotos"

DIAS_ES = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
MESES_ES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
]

# Ritmo de la galería: grupos de tamaño variable en vez de una rejilla fija.
# En móvil, Streamlit apila cualquier fila de columnas por debajo de ~768px,
# así que un grupo de 3 o 4 no "rompe" nada en el teléfono (se convierte en
# una sola columna igualmente) — pero en iPad/pantallas anchas sí aprovecha
# el espacio extra y se ve como un collage de verdad, no solo dos variantes.
PATRON_GRUPOS = [1, 2, 3, 1, 2, 4, 2]

# Ángulos de inclinación (grados) para el efecto "collage/polaroid disperso".
ANGULOS = [-2.2, 1.6, -1.2, 2.0, -0.7, 1.1]

# Icono de polaroid con "+", según la referencia que se pasó para el estado
# vacío del álbum.
ICONO_POLAROID = """
<svg viewBox="0 0 100 130" fill="none" stroke="#ABA398" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">
    <rect x="6" y="6" width="88" height="118" rx="8"/>
    <rect x="16" y="16" width="68" height="68" rx="2"/>
    <line x1="50" y1="96" x2="50" y2="112"/>
    <line x1="42" y1="104" x2="58" y2="104"/>
</svg>
"""

# ==========================================
# CSS — editorial de fotografía / papelería vintage
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600&display=swap');

    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNav"],
    div[data-testid="stSidebarCollapsedControl"],
    a[href*="streamlit.io"],
    .header-anchor {
        display: none !important;
        visibility: hidden !important;
    }

    html, body { margin: 0; padding: 0; }

    .stApp { background-color: #F7F3EC; }

    .block-container {
        max-width: 480px !important;
        padding: 2.2rem 1.4rem 2.6rem 1.4rem !important;
        margin: 0 auto !important;
    }

    /* En iPad/tablet en horizontal (ancho real, no solo "pantalla grande"
       de escritorio) aprovechamos el espacio: el mismo código de Python
       (mismos grupos de fotos) reparte más aire por foto en vez de quedar
       apretado en una columna de 480px. */
    @media (min-width: 900px) {
        .block-container {
            max-width: 1000px !important;
        }
    }

    h1, h2, h3, p { text-align: center !important; }

    /* ---------- Portada: tarjeta con marco, centrada de verdad ---------- */
    div[class*="st-key-y4_portada"] {
        min-height: 100vh;
        min-height: calc(100svh - 4.8rem);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        border: 1.4px solid #111111;
        padding: 2.6rem 1.6rem;
    }

    /* Modo compacto para pantallas bajas (iPhone SE, iPhone X y similares):
       se reduce tamaño/espaciado para que quepa todo, incluido el botón,
       sin necesidad de hacer scroll. Se activa solo por ALTURA de pantalla,
       así que se adapta solo a cualquier móvil pequeño futuro, no hace
       falta tocar esto otra vez para un modelo nuevo. */
    @media (max-height: 830px) {
        div[class*="st-key-y4_portada"] {
            padding: 1.4rem 1.6rem;
        }
        .y4-divisor-estrella {
            margin-bottom: 0.8rem;
        }
        .y4-titulo-grande {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .y4-eyebrow {
            margin-bottom: 0.4rem;
        }
        .y4-espacio {
            height: 0.5rem;
        }
        div[class*="st-key-y4_portada"] [data-testid="stImage"] img {
            max-height: 34vh;
            width: auto;
            margin: 0 auto;
        }
        .y4-cita {
            font-size: 0.92rem;
            line-height: 1.55;
            margin-bottom: 0.6rem;
        }
    }
    .y4-divisor-estrella {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.7rem;
        margin-bottom: 1.6rem;
        color: #7F182B;
        width: 100%;
    }
    .y4-divisor-estrella .linea {
        width: 34px;
        height: 1px;
        background-color: #111111;
        opacity: 0.5;
    }
    .y4-divisor-estrella .estrella { font-size: 1rem; }
    .y4-icono-vacio {
        display: flex;
        justify-content: center;
        width: 100%;
        margin-bottom: 1.4rem;
    }
    .y4-icono-vacio svg {
        width: 84px;
        height: auto;
    }
    .y4-eyebrow {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.72rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        text-align: center !important;
        color: #B7807D;
        margin-bottom: 0.8rem;
        width: 100%;
    }
    .y4-centro-flex {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        text-align: center;
    }
    .y4-titulo-grande {
        font-family: 'Playfair Display', serif;
        font-weight: 400;
        font-size: 2.7rem;
        line-height: 1.05;
        text-align: center !important;
        color: #111111 !important;
        margin: 0 0 1.4rem 0;
        width: 100%;
        align-self: center;
    }
    .y4-espacio {
        height: 1.3rem;
    }
    .y4-cita {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 500;
        font-size: 1.08rem;
        line-height: 1.85;
        color: #2b2b2b;
        margin-bottom: 1.6rem;
        padding: 0 0.4rem;
        text-align: center;
        width: 100%;
    }
    .y4-film-divider {
        display: flex;
        justify-content: center;
        gap: 7px;
        margin: 0 auto 1.8rem auto;
        width: 100%;
    }
    .y4-film-divider span {
        width: 5px;
        height: 5px;
        border-radius: 50%;
    }
    .y4-film-divider span:nth-child(1) { background-color: #7F182B; opacity: 0.55; }
    .y4-film-divider span:nth-child(2) { background-color: #B7807D; opacity: 0.7; }
    .y4-film-divider span:nth-child(3) { background-color: #8A8F6B; opacity: 0.6; }
    .y4-film-divider span:nth-child(4) { background-color: #B7807D; opacity: 0.7; }
    .y4-film-divider span:nth-child(5) { background-color: #7F182B; opacity: 0.55; }

    .y4-photo-label {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.74rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #7F182B;
        margin-bottom: 0.5rem;
    }
    .y4-photo-label-sm {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.62rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7F182B;
        margin-bottom: 0.4rem;
    }
    .y4-photo-date {
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        font-size: 0.72rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #8a8378;
        margin-bottom: 0.7rem;
    }
    .y4-photo-date-sm {
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        font-size: 0.6rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #8a8378;
        margin-bottom: 0.5rem;
    }
    .y4-photo-caption {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1rem;
        color: #2b2b2b;
        margin-top: 0.6rem;
        padding: 0 0.4rem;
    }
    .y4-photo-caption-sm {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 0.85rem;
        color: #2b2b2b;
        margin-top: 0.4rem;
        padding: 0 0.1rem;
    }
    [data-testid="stImage"] img {
        display: block;
        width: 100%;
        margin: 0 auto;
    }
    .y4-separador {
        border: none;
        border-top: 1px solid rgba(183, 128, 125, 0.3);
        margin: 1.6rem 0 2rem 0;
    }
    .y4-vacio-texto {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.05rem;
        color: #2b2b2b;
        line-height: 1.8;
        margin: 0.2rem 0;
        text-align: center;
        width: 100%;
    }
    .y4-candado-texto {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.85rem;
        color: #8a8378;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* ---------- Estado vacío del journal: centrado de verdad ---------- */
    div[class*="st-key-y4_vacio_centro"] {
        min-height: 100vh;
        min-height: calc(100svh - 4.8rem);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    /* Botones: minimalistas, borde fino burdeos (papelería editorial) */
    div.stButton > button {
        background-color: transparent !important;
        color: #7F182B !important;
        border: 1.4px solid #7F182B !important;
        border-radius: 0 !important;
        padding: 0.9rem 1.2rem !important;
        width: 100% !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 2px !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #7F182B !important;
        color: #F7F3EC !important;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# SUPABASE (reutiliza los mismos secrets del proyecto)
# ==========================================
@st.cache_resource
def iniciar_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase: Client = iniciar_supabase()


def obtener_fotos():
    try:
        respuesta = supabase.table(TABLA).select("*").order("photo_number", desc=False).execute()
        return respuesta.data or []
    except Exception:
        return []


def siguiente_numero_foto(fotos):
    if not fotos:
        return 1
    return max(f["photo_number"] for f in fotos) + 1


def descargar_imagen(ruta):
    return supabase.storage.from_(BUCKET).download(ruta)


def formatear_fecha(fecha_iso):
    fecha = date.fromisoformat(fecha_iso)
    dia_semana = DIAS_ES[fecha.weekday()]
    mes = MESES_ES[fecha.month - 1]
    return f"{dia_semana} · {fecha.day} {mes} {fecha.year}"


# ==========================================
# COMPRESIÓN / REDIMENSIONADO (server-side con Pillow)
# ==========================================
def procesar_imagen(archivo_subido, dimension_maxima=1600, calidad=82):
    imagen = Image.open(archivo_subido)
    imagen = imagen.convert("RGB")
    imagen.thumbnail((dimension_maxima, dimension_maxima))
    buffer = io.BytesIO()
    imagen.save(buffer, format="JPEG", quality=calidad, optimize=True)
    return buffer.getvalue()


def guardar_foto(archivo_subido, fecha, caption):
    numero = siguiente_numero_foto(obtener_fotos())
    datos_jpg = procesar_imagen(archivo_subido)
    ruta = f"{numero:03d}.jpg"

    supabase.storage.from_(BUCKET).upload(
        path=ruta,
        file=datos_jpg,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )
    supabase.table(TABLA).insert({
        "photo_number": numero,
        "image_path": ruta,
        "caption": caption or None,
        "date": fecha.isoformat(),
    }).execute()


def eliminar_foto(foto):
    try:
        supabase.storage.from_(BUCKET).remove([foto["image_path"]])
    except Exception:
        pass  
    supabase.table(TABLA).delete().eq("id", foto["id"]).execute()

    posteriores = [f for f in obtener_fotos() if f["photo_number"] > foto["photo_number"]]
    for siguiente in posteriores:
        nuevo_numero = siguiente["photo_number"] - 1
        nueva_ruta = f"{nuevo_numero:03d}.jpg"
        try:
            supabase.storage.from_(BUCKET).move(siguiente["image_path"], nueva_ruta)
        except Exception:
            nueva_ruta = siguiente["image_path"]  
        supabase.table(TABLA).update({
            "photo_number": nuevo_numero,
            "image_path": nueva_ruta,
        }).eq("id", siguiente["id"]).execute()


# ==========================================
# CANDADO (PIN)
# ==========================================
def desbloqueado():
    return st.session_state.get("y4_desbloqueado", False)


def mostrar_candado():
    st.markdown('<p class="y4-candado-texto">Solo para nosotros dos.</p>', unsafe_allow_html=True)
    with st.form("y4_pin_form", clear_on_submit=True):
        pin = st.text_input("PIN", type="password", label_visibility="collapsed", placeholder="PIN")
        enviado = st.form_submit_button("DESBLOQUEAR")
    if enviado:
        pin_correcto = st.secrets.get("YEAR_FOUR_PIN")
        if pin_correcto and pin == pin_correcto:
            st.session_state.y4_desbloqueado = True
            st.rerun()
        else:
            st.error("PIN incorrecto.")


def mostrar_formulario_subida():
    with st.form("y4_subida_form", clear_on_submit=True):
        archivo = st.file_uploader(
            "Foto", type=["jpg", "jpeg", "png", "heic", "heif"], label_visibility="collapsed"
        )
        fecha = st.date_input("Fecha", value=date.today(), label_visibility="collapsed")
        caption = st.text_input(
            "Caption", placeholder="Un pequeño recuerdo de este momento (opcional)", label_visibility="collapsed"
        )
        enviado = st.form_submit_button("ADD PHOTO")

    if enviado:
        if archivo is None:
            st.warning("Elige una foto primero.")
        else:
            try:
                with st.spinner("Revelando..."):
                    guardar_foto(archivo, fecha, caption.strip())
            except Exception as e:
                st.error(f"No se pudo subir la foto todavía: {e}")
            else:
                st.session_state.y4_mostrar_subida = False
                st.session_state.y4_celebrar = True
                st.rerun()


def boton_anadir_foto():
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if st.button("+ ADD PHOTO", key="y4_add_photo_btn", use_container_width=True):
            st.session_state.y4_mostrar_subida = True
            st.rerun()


# ==========================================
# PANTALLAS
# ==========================================
def mostrar_portada():
    with st.container(key="y4_portada"):
        st.markdown(
            '<div class="y4-divisor-estrella"><span class="linea"></span>'
            '<span class="estrella">✦</span><span class="linea"></span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="y4-centro-flex"><div class="y4-titulo-grande">YEAR<br>FOUR</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="y4-eyebrow">The Next Chapter</div>', unsafe_allow_html=True)
        st.markdown('<div class="y4-espacio"></div>', unsafe_allow_html=True)

        st.image("assets/year_four_camara.png", use_container_width=True)

        st.markdown('<div class="y4-espacio"></div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="y4-cita">"Los tres primeros años son recuerdos.<br>El cuarto todavía está por escribir."</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="y4-espacio"></div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            if st.button("OPEN JOURNAL", key="y4_open_journal", use_container_width=True):
                st.session_state.y4_entrado = True
                st.rerun()


def inyectar_estilo_tarjeta(key, angulo):
    st.markdown(
        f"""
        <style>
        div[class*="st-key-{key}"] {{
            transform: rotate({angulo}deg);
            background-color: #FFFFFF;
            padding: 10px 10px 6px 10px;
            box-shadow: 0 10px 22px rgba(17, 17, 17, 0.16);
            margin-bottom: 0.6rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_tarjeta_foto(foto, indice, grande):
    angulo = ANGULOS[indice % len(ANGULOS)]
    key = f"y4card{foto['id']}"

    clase_label = "y4-photo-label" if grande else "y4-photo-label-sm"
    clase_fecha = "y4-photo-date" if grande else "y4-photo-date-sm"
    clase_caption = "y4-photo-caption" if grande else "y4-photo-caption-sm"

    inyectar_estilo_tarjeta(key, angulo)
    with st.container(key=key):
        st.markdown(f'<div class="{clase_label}">Photo #{foto["photo_number"]:03d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{clase_fecha}">{formatear_fecha(foto["date"])}</div>', unsafe_allow_html=True)
        try:
            st.image(descargar_imagen(foto["image_path"]), use_container_width=True)
        except Exception:
            st.warning("No se pudo cargar esta foto.")
        if foto.get("caption"):
            st.markdown(f'<p class="{clase_caption}">"{foto["caption"]}"</p>', unsafe_allow_html=True)


def mostrar_galeria(fotos):
    i = 0
    indice_patron = 0
    total = len(fotos)
    while i < total:
        tamano_grupo = min(PATRON_GRUPOS[indice_patron % len(PATRON_GRUPOS)], total - i)
        grupo = fotos[i:i + tamano_grupo]

        if tamano_grupo == 1:
            mostrar_tarjeta_foto(grupo[0], i, grande=True)
        else:
            columnas = st.columns(tamano_grupo)
            for offset, (columna, foto) in enumerate(zip(columnas, grupo)):
                with columna:
                    mostrar_tarjeta_foto(foto, i + offset, grande=False)

        i += tamano_grupo
        indice_patron += 1
        st.markdown('<hr class="y4-separador">', unsafe_allow_html=True)


def mostrar_cabecera_journal():
    st.markdown('<div class="y4-eyebrow">Year Four</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="y4-centro-flex"><div class="y4-titulo-grande" style="font-size: 2rem;">PHOTO JOURNAL</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="y4-film-divider"><span></span><span></span><span></span><span></span><span></span></div>',
        unsafe_allow_html=True,
    )


def mostrar_controles_subida():
    if st.session_state.pop("y4_celebrar", False):
        st.balloons()

    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    if not st.session_state.get("y4_mostrar_subida", False):
        boton_anadir_foto()
    elif desbloqueado():
        mostrar_formulario_subida()
    else:
        mostrar_candado()


def mostrar_journal():
    fotos = obtener_fotos()

    if not fotos:
        with st.container(key="y4_vacio_centro"):
            mostrar_cabecera_journal()
            st.markdown(f'<div class="y4-icono-vacio">{ICONO_POLAROID}</div>', unsafe_allow_html=True)
            st.markdown('<p class="y4-vacio-texto">Este álbum todavía está vacío.</p>', unsafe_allow_html=True)
            st.markdown('<p class="y4-vacio-texto">El primer recuerdo está esperando.</p>', unsafe_allow_html=True)
            mostrar_controles_subida()
        return

    mostrar_cabecera_journal()
    mostrar_galeria(fotos)
    mostrar_controles_subida()


# ==========================================
# RUTA
# ==========================================
if "y4_entrado" not in st.session_state:
    st.session_state.y4_entrado = False

if not st.session_state.y4_entrado:
    mostrar_portada()
else:
    mostrar_journal()