import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

# =============================
# CONFIGURACIÓN
# =============================
st.set_page_config(
    page_title="Análisis de la Acción",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# CSS
# =============================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #11161C;
        color: #E5E7EB;
    }

    [data-testid="stSidebar"] {
        background-color: #0B0F19;
        border-right: 1px solid #1F2937;
    }

    [data-testid="stSidebar"] * {
        color: #E5E7EB;
    }

    .company-title {
        font-size: 44px;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 5px;
    }

    .market-text {
        color: #A1A1AA;
        font-size: 16px;
        margin-bottom: 10px;
    }

    .price-main {
        font-size: 48px;
        font-weight: 800;
        color: #F8FAFC;
    }

    .price-red {
        font-size: 28px;
        font-weight: 700;
        color: #FF4D57;
    }

    .price-blue {
        color: #8ECDF8;
        font-weight: 700;
    }

    .section-card {
        background-color: #151C26;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #263241;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 30px;
        font-weight: 750;
        color: #F8FAFC;
        margin-bottom: 10px;
    }

    .section-text {
        color: #CBD5E1;
        font-size: 16px;
    }

    div[data-testid="stRadio"] label {
        font-size: 17px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# DATOS BASE
# =============================
acciones = {
    "Chubb Limited": "CB"
}

st.sidebar.title("Panel de selección")

accion_nombre = st.sidebar.selectbox(
    "Selecciona una acción:",
    list(acciones.keys())
)

ticker = acciones[accion_nombre]

st.sidebar.markdown("---")

seccion = st.sidebar.radio(
    "Secciones",
    [
        "Resumen",
        "Rendimientos últimos 5 días",
        "Medidas de riesgo",
        "VaR y CVaR - Métodos Generales",
        "VaR y CVaR - Rolling Windows",
        "Comparación",
        "Volatilidad Móvil"
    ]
)

st.sidebar.markdown("---")
st.sidebar.write(f"Ticker seleccionado: **{ticker}**")

# =============================
# DESCARGA DE DATOS
# =============================
@st.cache_data
def descargar_precios(ticker):
    precios_5y = yf.download(ticker, period="5y", auto_adjust=True, progress=False)
    precios_1d = yf.download(ticker, period="1d", interval="5m", auto_adjust=True, progress=False)
    return precios_5y, precios_1d

df, df_dia = descargar_precios(ticker)

# Arreglar posible MultiIndex
if isinstance(df.columns, tuple):
    df.columns = df.columns.get_level_values(0)

if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
    df.columns = df.columns.get_level_values(0)

if hasattr(df_dia.columns, "nlevels") and df_dia.columns.nlevels > 1:
    df_dia.columns = df_dia.columns.get_level_values(0)

precio_actual = float(df["Close"].dropna().iloc[-1])
precio_anterior = float(df["Close"].dropna().iloc[-2])
cambio = precio_actual - precio_anterior
cambio_pct = cambio / precio_anterior

# =============================
# RESUMEN PRINCIPAL
# =============================
if seccion == "Resumen":

    st.markdown(
        """
        <div class="market-text">
            NYSE · Delayed Quote · USD
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="company-title">
            {accion_nombre} ({ticker})
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        st.markdown(
            f"""
            <span class="price-main">{precio_actual:.2f}</span>
            """,
            unsafe_allow_html=True
        )

    with col2:
        color_clase = "price-red" if cambio < 0 else "price-blue"
        signo = "+" if cambio > 0 else ""

        st.markdown(
            f"""
            <span class="{color_clase}">
                {signo}{cambio:.2f} ({signo}{cambio_pct:.2%})
            </span>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="section-text">
                Último precio disponible
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Precio del día</div>
            <div class="section-text">
                Evolución intradía del precio de la acción seleccionada.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#11161C")
    ax.set_facecolor("#11161C")

    precios_dia = df_dia["Close"].dropna()

    color_linea = "#FF4D57" if precios_dia.iloc[-1] < precios_dia.iloc[0] else "#8ECDF8"

    ax.plot(
        precios_dia.index,
        precios_dia.values,
        color=color_linea,
        linewidth=2
    )

    ax.axhline(
        precios_dia.iloc[-1],
        color="#8ECDF8",
        linestyle="--",
        linewidth=1,
        alpha=0.7
    )

    ax.grid(alpha=0.15)
    ax.tick_params(colors="#CBD5E1")
    ax.spines["bottom"].set_color("#334155")
    ax.spines["left"].set_color("#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(
        f"{accion_nombre} - Precio intradía",
        color="#F8FAFC",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Hora", color="#CBD5E1")
    ax.set_ylabel("Precio", color="#CBD5E1")

    st.pyplot(fig)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Precio actual", f"${precio_actual:.2f}")

    with c2:
        st.metric("Cambio diario", f"{cambio:.2f}", f"{cambio_pct:.2%}")

    with c3:
        st.metric("Ticker", ticker)

# =============================
# OTRAS SECCIONES
# =============================
elif seccion == "Rendimientos últimos 5 días":
    st.markdown('<div class="section-title">Rendimientos de los últimos 5 días</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">Aquí se mostrarán los rendimientos diarios más recientes.</div>', unsafe_allow_html=True)

elif seccion == "Medidas de riesgo":
    st.markdown('<div class="section-title">Medidas de riesgo</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">Aquí irán media, volatilidad, sesgo, curtosis y otras medidas descriptivas.</div>', unsafe_allow_html=True)

elif seccion == "VaR y CVaR - Métodos Generales":
    st.markdown('<div class="section-title">VaR y CVaR</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-card">
            <h3>Métodos Generales</h3>
            Aquí irán los métodos histórico, paramétrico y simulación.
        </div>
        """,
        unsafe_allow_html=True
    )

elif seccion == "VaR y CVaR - Rolling Windows":
    st.markdown('<div class="section-title">VaR y CVaR</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-card">
            <h3>Rolling Windows</h3>
            Aquí se mostrarán los cálculos de VaR y CVaR con ventanas móviles.
        </div>
        """,
        unsafe_allow_html=True
    )

elif seccion == "Comparación":
    st.markdown('<div class="section-title">Comparación</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">Aquí se compararán los distintos métodos de estimación de riesgo.</div>', unsafe_allow_html=True)

elif seccion == "Volatilidad Móvil":
    st.markdown('<div class="section-title">Volatilidad Móvil</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">Aquí se mostrará la evolución de la volatilidad usando ventanas móviles.</div>', unsafe_allow_html=True)