import streamlit as st
import json
from supabase import create_client, Client

st.set_page_config(page_title="Nuestro Pasaporte Gastronómico", page_icon="🥂", layout="centered")

# ==========================================
# CSS ALTA COSTURA — Pasaporte con zonas táctiles 100% invisibles
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600&display=swap');

    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNav"],
    div[data-testid="stSidebarCollapsedControl"],
    a[href*="streamlit.io"] {
        display: none !important;
        visibility: hidden !important;
    }

    html, body { margin: 0; padding: 0; }

    .stApp {
        background-color: #F9F8F6;
    }

    .block-container {
        max-width: 480px !important;
        padding: 1.6rem 1rem 2.4rem 1rem !important;
        margin: 0 auto !important;
    }

    h1, h2, h3, p { text-align: center !important; }

    /* ---------- Evitar que Streamlit apile las columnas en móvil ---------- */
    /* Streamlit tiene su propia media query interna que, por debajo de ~640px
       de ancho de ventana, pasa TODAS las filas de columnas a flex-direction:
       column (apiladas). Eso es lo que hacía que las 3 fotos (y también las
       flechas laterales) se vieran enormes y en vertical en el móvil aunque en
       el ordenador se vieran bien. Aquí forzamos que sigan en fila, pero SIN
       tocar flex-grow/flex-basis, para no romper las proporciones [1, 8, 1]
       de la fila principal (si se fuerza "flex: 1" en todas las columnas por
       igual, esa fila pasaría a ser 33/33/33 y el contenido central se
       encogería muchísimo). */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
        }
        [data-testid="column"] {
            min-width: 0 !important;
        }
    }

    /* ---------- CONTENEDOR MAESTRO: el Pasaporte burdeos ---------- */
    div[class*="st-key-pasaporte"] {
        background-color: #7F182B;
        border-radius: 15px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        min-height: 85vh;
        padding: 3rem 1.6rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* ---------- Flechitas laterales: discretas, sin fondo, tamaño natural ---------- */
    /* Nada de min-height artificial: eso era lo que inflaba la fila entera del
       pasaporte y dejaba la portada pegada arriba con un hueco enorme debajo,
       y además hacía el botón tan alto que en móvil el toque no siempre caía
       dentro de su área real. Ahora es un botón pequeño de verdad. */
    div[class*="st-key-zona_izq"],
    div[class*="st-key-zona_der"] {
        display: flex;
        align-items: center;
        height: 100%;
    }
    div[class*="st-key-zona_izq"] div.stButton > button,
    div[class*="st-key-zona_der"] div.stButton > button {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        color: rgba(232, 195, 124, 0.55) !important;
        font-size: 1.7rem !important;
        font-weight: 300 !important;
        width: 100% !important;
        padding: 0.6rem 0 !important;
        margin: 0 !important;
    }
    div[class*="st-key-zona_izq"] div.stButton > button:hover,
    div[class*="st-key-zona_der"] div.stButton > button:hover,
    div[class*="st-key-zona_izq"] div.stButton > button:active,
    div[class*="st-key-zona_der"] div.stButton > button:active,
    div[class*="st-key-zona_izq"] div.stButton > button:focus,
    div[class*="st-key-zona_der"] div.stButton > button:focus {
        background: transparent !important;
        color: rgba(232, 195, 124, 1) !important;
        box-shadow: none !important;
    }

    /* ---------- Portada (dentro del pasaporte) ---------- */
    .cover-union {
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        text-align: center;
        color: #E8C37C !important;
        margin-bottom: 2.6rem;
    }
    .cover-titulo {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 2.2rem !important;
        letter-spacing: 6px !important;
        white-space: nowrap;
        text-align: center;
        color: #E8C37C !important;
        margin-bottom: 2.8rem;
    }
    .cover-escudo-aro {
        width: 148px;
        height: 148px;
        border-radius: 50%;
        border: 1.5px solid #E8C37C;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 2.8rem auto;
    }
    .cover-escudo-aro svg {
        width: 76px;
        height: 76px;
        color: #E8C37C;
    }
    .cover-reserva {
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        font-style: italic;
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-align: center;
        color: #E8C37C !important;
    }

    /* ---------- Contraportada ---------- */
    div[class*="st-key-recuerdo_foto"] [data-testid="stImage"] img {
        display: block;
        margin: 0 auto;
        max-width: 230px;
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(232, 195, 124, 0.4);
        box-shadow: 0 16px 34px rgba(0,0,0,0.32);
    }
    .contraportada-texto {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 500;
        font-size: 1.02rem;
        line-height: 1.85;
        color: #E8C37C !important;
        padding: 0 1.2rem;
        margin-bottom: 2.2rem;
    }

    /* ---------- Folio interior (páginas 1, 2, 3) ---------- */
    div[class*="st-key-folio"] {
        background-color: #FFFDF9;
        border-radius: 16px;
        padding: 1.8rem 1.4rem 1.5rem 1.4rem;
        margin: 0 0 1.6rem 0;
        box-shadow: 0 12px 32px rgba(0,0,0,0.18);
    }
    .capitulo-titulo {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.75rem;
        color: #111111 !important;
        margin: 1.1rem 0 0.8rem 0;
    }
    .capitulo-invitacion {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 500;
        font-size: 1rem;
        color: #8a774f !important;
        margin-bottom: 1rem;
    }
    .capitulo-texto {
        font-family: 'Montserrat', sans-serif;
        font-weight: 300;
        font-size: 0.96rem;
        line-height: 1.85;
        color: #45433E !important;
        margin-bottom: 1.4rem;
    }
    div[class*="st-key-folio"] [data-testid="stImage"] img {
        display: block;
        width: 100%;
        border-radius: 4px;
        box-shadow: 0 12px 26px rgba(17,17,17,0.18);
    }

    /* ---------- Estados: guardada / bloqueada ---------- */
    .estado-guardado {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 1px;
        color: #4B7A4B !important;
        margin-top: 0.4rem;
    }
    .estado-bloqueado {
        font-family: 'Montserrat', sans-serif;
        font-weight: 400;
        font-style: italic;
        font-size: 0.85rem;
        color: #9A9689 !important;
        margin-top: 0.4rem;
        line-height: 1.7;
    }

    /* ---------- Botón CANJEAR: negro, dentro del folio ---------- */
    div.stButton > button {
        background-color: #111111 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 1rem 1.3rem !important;
        width: 100% !important;
        box-shadow: 0 10px 26px rgba(17,17,17,0.22) !important;
        transition: all 0.25s ease !important;
    }
    div.stButton > button:hover {
        background-color: #000000 !important;
        box-shadow: 0 14px 30px rgba(17,17,17,0.3) !important;
        transform: translateY(-1px);
    }
    div.stButton > button * {
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 2px !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
    }

    /* ---------- Sorpresa final (fuera del pasaporte) ---------- */
    .pasaporte-titulo {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 2.2rem;
        color: #111111;
        margin: 1rem 0 0.6rem 0;
        line-height: 1.25;
    }
    .icono-grande-aro {
        width: 190px;
        height: 190px;
        border-radius: 50%;
        border: 1px solid #D8D2C2;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.6rem auto 1.8rem auto;
    }
    .icono-grande-aro svg {
        width: 92px;
        height: 92px;
        color: #111111;
    }
    .eyebrow {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-align: center;
        color: #A0A0A0;
        margin-bottom: 0.4rem;
    }

    /* ---------- Celebración a pantalla completa (al canjear) ---------- */
    @keyframes celebracionFade {
        0%   { opacity: 0; transform: scale(0.94); }
        12%  { opacity: 1; transform: scale(1); }
        80%  { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(1.03); }
    }
    .overlay-celebracion {
        position: fixed;
        inset: 0;
        z-index: 9999;
        background: rgba(15,15,15,0.93);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        pointer-events: none;
        animation: celebracionFade 2.6s ease forwards;
    }
    .overlay-check {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        border: 1.5px solid #F9F8F6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        color: #F9F8F6;
        margin-bottom: 1.4rem;
    }
    .overlay-titulo {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.7rem;
        color: #F9F8F6 !important;
        margin-bottom: 0.5rem;
    }
    .overlay-subtitulo {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #C9C2B4 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONEXIÓN A SUPABASE
# ==========================================
@st.cache_resource
def iniciar_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = iniciar_supabase()

def obtener_estado():
    try:
        respuesta = supabase.storage.from_('galeria_fotos').download('estado_cenas.json')
        return json.loads(respuesta)
    except Exception:
        return {"hamburguesa": False, "tapas": False, "pizza": False}

def guardar_estado(estado):
    datos_json = json.dumps(estado).encode('utf-8')
    try:
        supabase.storage.from_('galeria_fotos').upload('estado_cenas.json', datos_json, file_options={"upsert": "true"})
    except Exception:
        pass

# ==========================================
# ICONOS SVG
# ==========================================
ICONO_AVION = """
<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M58 6L27 37"/>
    <path d="M58 6L38 58l-11-21L6 26z"/>
</svg>
"""

ICONO_CUBIERTOS_CRUZADOS = """
<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <g transform="rotate(-45 32 32)">
        <path d="M32 6c4 0 6 4 6 9v14h-12v-14c0-5 2-9 6-9z"/>
        <line x1="32" y1="29" x2="32" y2="58"/>
    </g>
    <g transform="rotate(45 32 32)">
        <line x1="25" y1="6" x2="25" y2="20"/>
        <line x1="32" y1="6" x2="32" y2="20"/>
        <line x1="39" y1="6" x2="39" y2="20"/>
        <path d="M25 20c0 6 4 9 7 9s7-3 7-9"/>
        <line x1="32" y1="29" x2="32" y2="58"/>
    </g>
</svg>
"""

# ==========================================
# DATOS DE LOS 3 CAPÍTULOS
# ==========================================
CAPITULOS = [
    {
        "clave": "hamburguesa",
        "titulo": "The Burger Era",
        "imagen": "assets/hamburguesa.png",
        "invitacion": "Te invito a que revivamos juntos nuestra primera era.",
        "texto": "Nuestro primer año juntos fue, sin lugar a dudas, la era de las hamburguesas. Entre carne jugosa, quesos fundidos y salsas caseras, descubrimos que la felicidad también cabe entre dos panes brioche: los cimientos de todo lo que vendría después.",
    },
    {
        "clave": "tapas",
        "titulo": "La Época del Tapeo",
        "imagen": "assets/tapas.png",
        "invitacion": "Te invito a que volvamos a llenar la mesa de raciones.",
        "texto": "El segundo año nos volvimos expertos en el arte de compartir. Croquetas, bravas y raciones al centro de la mesa. Aprendimos que compartir plato es, en realidad, compartir vida.",
    },
    {
        "clave": "pizza",
        "titulo": "La Dolce Vita",
        "imagen": "assets/pizza.png",
        "invitacion": "Te invito a que volvamos a sentir esa dolce vita.",
        "texto": "El tercer año nos llevó a Italia: pasta al dente y pizza recién salida del horno de leña. Entendimos lo que significa la dolce vita: disfrutar de lo simple, a tu lado y sin prisa.",
    },
]

# ==========================================
# COMPONENTES REUTILIZABLES
# ==========================================
def boton_centrado(etiqueta, key=None):
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        return st.button(etiqueta, key=key, use_container_width=True)

def mostrar_celebracion_si_procede():
    if st.session_state.pop("celebrar", False):
        st.balloons()
        st.markdown(
            """
            <div class="overlay-celebracion">
                <div class="overlay-check">✓</div>
                <div class="overlay-titulo">Invitación aceptada</div>
                <div class="overlay-subtitulo">Nos vemos pronto para vivirlo juntos</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def mostrar_portada():
    st.markdown('<div class="cover-union">Unión Gastronómica</div>', unsafe_allow_html=True)
    st.markdown('<div class="cover-titulo">PASAPORTE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cover-escudo-aro">{ICONO_CUBIERTOS_CRUZADOS}</div>', unsafe_allow_html=True)
    st.markdown('<div class="cover-reserva">Reserva Exclusiva</div>', unsafe_allow_html=True)

def mostrar_contraportada():
    st.markdown('<div class="cover-union" style="margin-bottom: 1rem;">Nuestras Memorias</div>', unsafe_allow_html=True)

    with st.container(key="recuerdo_foto"):
        st.image("assets/foto_comiendo.jpg", use_container_width=True)

    st.markdown('<div class="cover-titulo" style="margin: 1.4rem 0 0.8rem 0;">GRACIAS</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="contraportada-texto">Por cada cena compartida, cada risa y cada capítulo de esta historia que seguimos escribiendo juntos. Gracias por todo.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="cover-escudo-aro">{ICONO_CUBIERTOS_CRUZADOS}</div>', unsafe_allow_html=True)

def mostrar_folio(capitulo, estado, tarjeta_url):
    clave = capitulo["clave"]
    ya_canjeada = estado[clave]
    llave_coincide = (tarjeta_url == clave)

    with st.container(key="folio"):
        st.image(capitulo["imagen"], use_container_width=True)
        st.markdown(f'<h2 class="capitulo-titulo">{capitulo["titulo"]}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p class="capitulo-invitacion">{capitulo["invitacion"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="capitulo-texto">{capitulo["texto"]}</p>', unsafe_allow_html=True)

        if ya_canjeada:
            st.markdown(
                '<p class="estado-guardado">✓ Cena guardada en nuestro historial</p>',
                unsafe_allow_html=True,
            )
        elif llave_coincide:
            if boton_centrado("🔓 CANJEAR ESTA CENA", key=f"btn_{clave}"):
                estado[clave] = True
                guardar_estado(estado)
                st.session_state.celebrar = True
                st.rerun()
        else:
            st.markdown(
                '<p class="estado-bloqueado">🔒 Bloqueado. Escanea la tarjeta física para desbloquear.</p>',
                unsafe_allow_html=True,
            )

def mostrar_sorpresa_final():
    st.balloons()
    st.snow()

    st.markdown(f'<div class="icono-grande-aro">{ICONO_AVION}</div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">EL GRAN VIAJE ✈️</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="pasaporte-titulo">¡Nos vamos de Escapada!</h1>', unsafe_allow_html=True)
    st.markdown(
        """
        <p class="capitulo-texto">Como este año por fin tenemos los viernes libres, te has ganado un fin de semana fuera. Este es tu Billete Dorado: tú eliges el destino en el mapa, y yo me encargo del transporte y del alojamiento.</p>
        <p class="capitulo-invitacion">Vete preparando la maleta.</p>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# RUTAS
# ==========================================
estado = obtener_estado()
cenas_desbloqueadas = sum(estado.values())
tarjeta_url = st.query_params.get("tarjeta", "")

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = 0

if cenas_desbloqueadas == 3:
    mostrar_sorpresa_final()
else:
    pagina = st.session_state.pagina_actual

    with st.container(key="pasaporte"):
        col_izq, col_centro, col_der = st.columns([1, 8, 1])

        with col_izq:
            if pagina > 0:
                with st.container(key="zona_izq"):
                    if st.button("‹", key="btn_zona_izq"):
                        st.session_state.pagina_actual = pagina - 1
                        st.rerun()

        with col_centro:
            if pagina == 0:
                mostrar_portada()
            elif pagina == 4:
                mostrar_contraportada()
            else:
                capitulo = CAPITULOS[pagina - 1]
                mostrar_folio(capitulo, estado, tarjeta_url)

        with col_der:
            if pagina < 4:
                with st.container(key="zona_der"):
                    if st.button("›", key="btn_zona_der"):
                        st.session_state.pagina_actual = pagina + 1
                        st.rerun()

mostrar_celebracion_si_procede()