import streamlit as st
import yfinance as yf

# =============================
# CONFIGURACIÓN DE LA PÁGINA
# =============================
st.set_page_config(
    page_title="Análisis de Riesgo Financiero",
    page_icon="📉",
    layout="wide"
)

# =============================
# ESTILOS CSS
# =============================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0B0F14 0%, #111827 50%, #0F172A 100%);
        color: #E5E7EB;
    }

    h1, h2, h3 {
        color: #F8FAFC;
        font-family: 'Segoe UI', sans-serif;
    }

    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #94A3B8;
        margin-bottom: 35px;
    }

    .company-title {
        text-align: center;
        font-size: 46px;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 20px;
        margin-bottom: 35px;
    }

    .section-card {
        background-color: #111827;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #1F2937;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.35);
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 10px;
    }

    .section-text {
        color: #CBD5E1;
        font-size: 16px;
    }

    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1E293B;
    }

    [data-testid="stSidebar"] * {
        color: #E5E7EB;
    }

    .streamlit-expanderHeader {
        font-size: 22px;
        font-weight: 600;
        color: #F8FAFC;
        background-color: #111827;
        border-radius: 12px;
    }

    div[data-testid="stExpander"] {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 18px;
        margin-bottom: 25px;
    }

    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 22px;
        font-weight: 700;
        color: #F8FAFC;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# ENCABEZADO
# =============================
st.markdown(
    '<div class="main-title">Análisis de Riesgo Financiero</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Aplicación para analizar rendimientos, medidas de riesgo, VaR, CVaR y volatilidad móvil.</div>',
    unsafe_allow_html=True
)

# =============================
# SIDEBAR
# =============================
st.sidebar.title("Panel de selección")

acciones = {
    "Chubb Limited": "CB"
}

accion_nombre = st.sidebar.selectbox(
    "Selecciona una acción:",
    list(acciones.keys())
)

ticker = acciones[accion_nombre]

st.sidebar.markdown("---")
st.sidebar.write(f"Ticker seleccionado: **{ticker}**")

# =============================
# DESCARGA DE DATOS
# =============================
@st.cache_data
def descargar_datos(ticker):
    df = yf.download(ticker, period="5y", auto_adjust=True)
    return df

df = descargar_datos(ticker)

# =============================
# TÍTULO DE LA COMPAÑÍA
# =============================
st.markdown(
    f'<div class="company-title">{accion_nombre} ({ticker})</div>',
    unsafe_allow_html=True
)

# =============================
# SECCIONES DESPLEGABLES
# =============================

with st.expander("Rendimientos de los últimos 5 días", expanded=True):
    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                Aquí se mostrarán los rendimientos diarios más recientes de la acción seleccionada.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.expander("Medidas de riesgo", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                Aquí se presentarán estadísticas como media, volatilidad, sesgo, curtosis y otras medidas descriptivas.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.expander("VaR y CVaR", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                En esta sección se organizarán los distintos métodos para estimar VaR y CVaR.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["Métodos Generales", "Rolling Windows"])

    with tab1:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Métodos Generales</div>
                <div class="section-text">
                    Aquí irán los cálculos generales de VaR y CVaR: histórico, paramétrico y simulación.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab2:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Rolling Windows</div>
                <div class="section-text">
                    Aquí se mostrarán los cálculos de VaR y CVaR usando ventanas móviles.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with st.expander("Comparación", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                Aquí se compararán los distintos métodos de estimación de riesgo.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.expander("Volatilidad Móvil", expanded=False):
    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                Aquí se mostrará la evolución de la volatilidad usando ventanas móviles.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )