import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import kurtosis, skew, norm

# ============================================================
# CONFIGURACIÓN GENERAL DE LA APP
# ============================================================
st.set_page_config(
    page_title="Análisis de la Acción",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILO VISUAL
# ============================================================
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
        font-size: 46px;
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
        font-size: 52px;
        font-weight: 800;
        color: #F8FAFC;
    }

    .price-red {
        font-size: 30px;
        font-weight: 750;
        color: #FF4D57;
    }

    .price-blue {
        font-size: 30px;
        font-weight: 750;
        color: #8ECDF8;
    }

    .section-title {
        font-size: 32px;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 14px;
    }

    .section-card {
        background-color: #151C26;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #263241;
        margin-top: 16px;
        margin-bottom: 22px;
    }

    .section-text {
        color: #CBD5E1;
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        background-color: #151C26;
        border: 1px solid #263241;
        padding: 18px;
        border-radius: 16px;
    }

    div[data-testid="stMetricLabel"] {
        color: #94A3B8;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FUNCIONES DE DESCARGA Y FORMATO
# ============================================================

@st.cache_data
def descargar_datos(ticker):
    """
    Descarga datos históricos desde 2010 y datos intradía para la vista inicial.
    Los rendimientos se calculan como rendimientos diarios porcentuales simples.
    """

    df_historico = yf.download(
        ticker,
        start="2010-01-01",
        auto_adjust=True,
        progress=False
    )

    df_1d = yf.download(
        ticker,
        period="1d",
        interval="5m",
        auto_adjust=True,
        progress=False
    )

    # Si Yahoo no devuelve datos intradía, usamos datos recientes como respaldo.
    if df_1d.empty:
        df_1d = yf.download(
            ticker,
            period="5d",
            interval="30m",
            auto_adjust=True,
            progress=False
        )

    # A veces yfinance entrega columnas con doble índice; esto las deja planas.
    if hasattr(df_historico.columns, "nlevels") and df_historico.columns.nlevels > 1:
        df_historico.columns = df_historico.columns.get_level_values(0)

    if hasattr(df_1d.columns, "nlevels") and df_1d.columns.nlevels > 1:
        df_1d.columns = df_1d.columns.get_level_values(0)

    precios = df_historico["Close"].dropna()
    rendimientos = precios.pct_change().dropna()

    return df_historico, df_1d, precios, rendimientos


def crear_figura_base(figsize=(14, 6)):
    """
    Crea una figura con el estilo oscuro de la app.
    Así todas las gráficas mantienen la misma apariencia.
    """

    fig, ax = plt.subplots(figsize=figsize)

    fig.patch.set_facecolor("#11161C")
    ax.set_facecolor("#11161C")

    ax.tick_params(colors="#CBD5E1", labelsize=10)

    ax.spines["bottom"].set_color("#334155")
    ax.spines["left"].set_color("#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(
        True,
        color="#334155",
        linestyle="--",
        linewidth=0.6,
        alpha=0.35
    )

    return fig, ax


def mostrar_tabla(df):
    """
    Muestra tablas con un formato más limpio dentro de Streamlit.
    """

    st.dataframe(
        df.style.format(precision=6),
        use_container_width=True
    )


def formatear_leyenda(ax, ncol=3):
    """
    Coloca la leyenda debajo de la gráfica para que no tape los datos.
    """

    legend = ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=ncol,
        frameon=False,
        fontsize=9
    )

    for text in legend.get_texts():
        text.set_color("#E5E7EB")


# ============================================================
# FUNCIONES DE RIESGO
# ============================================================

def calcular_var_es_generales(returns):
    """
    Calcula VaR y ES para la serie completa de datos.

    Se incluyen:
    - Paramétrico Normal
    - Paramétrico T-Student
    - Histórico
    - Monte Carlo Normal
    - Monte Carlo T-Student

    Los niveles usados son 95%, 97.5% y 99%, como pide el proyecto.
    """

    niveles = [0.95, 0.975, 0.99]
    media = returns.mean()
    desviacion = returns.std()

    # Grados de libertad para la aproximación t-student paramétrica.
    gl_t = len(returns) - 1

    # Simulación Monte Carlo.
    # Se fija una semilla para que los resultados no cambien en cada recarga.
    np.random.seed(42)
    n = 1_000_000

    simulacion_normal = np.random.normal(media, desviacion, n)

    # Se usa gl = 5 para generar colas más pesadas, como en el código base.
    gl_mc = 5
    simulacion_t = media + desviacion * np.random.standard_t(gl_mc, n)

    resultados = []

    for nivel in niveles:

        p = 1 - nivel

        # --------------------------
        # Paramétrico Normal
        # --------------------------
        var_normal = norm.ppf(p, loc=media, scale=desviacion)
        z = norm.ppf(p)
        es_normal = media - desviacion * (norm.pdf(z) / p)

        resultados.append({
            "Método": "Paramétrico Normal",
            "Nivel de confianza": f"{nivel:.1%}",
            "VaR": var_normal,
            "ES/CVaR": es_normal,
            "VaR (%)": var_normal * 100,
            "ES/CVaR (%)": es_normal * 100
        })

        # --------------------------
        # Paramétrico T-Student
        # --------------------------
        q_t = stats.t.ppf(p, gl_t)
        var_t = stats.t.ppf(p, gl_t, loc=media, scale=desviacion)

        # Fórmula de ES para t-student en cola izquierda.
        es_t = media - desviacion * (
            stats.t.pdf(q_t, gl_t) * (gl_t + q_t**2) / ((gl_t - 1) * p)
        )

        resultados.append({
            "Método": "Paramétrico T-Student",
            "Nivel de confianza": f"{nivel:.1%}",
            "VaR": var_t,
            "ES/CVaR": es_t,
            "VaR (%)": var_t * 100,
            "ES/CVaR (%)": es_t * 100
        })

        # --------------------------
        # Histórico
        # --------------------------
        var_historico = returns.quantile(p)
        es_historico = returns[returns <= var_historico].mean()

        resultados.append({
            "Método": "Histórico",
            "Nivel de confianza": f"{nivel:.1%}",
            "VaR": var_historico,
            "ES/CVaR": es_historico,
            "VaR (%)": var_historico * 100,
            "ES/CVaR (%)": es_historico * 100
        })

        # --------------------------
        # Monte Carlo Normal
        # --------------------------
        var_mc_normal = np.percentile(simulacion_normal, p * 100)
        es_mc_normal = simulacion_normal[simulacion_normal <= var_mc_normal].mean()

        resultados.append({
            "Método": "Monte Carlo Normal",
            "Nivel de confianza": f"{nivel:.1%}",
            "VaR": var_mc_normal,
            "ES/CVaR": es_mc_normal,
            "VaR (%)": var_mc_normal * 100,
            "ES/CVaR (%)": es_mc_normal * 100
        })

        # --------------------------
        # Monte Carlo T-Student
        # --------------------------
        var_mc_t = np.percentile(simulacion_t, p * 100)
        es_mc_t = simulacion_t[simulacion_t <= var_mc_t].mean()

        resultados.append({
            "Método": "Monte Carlo T-Student",
            "Nivel de confianza": f"{nivel:.1%}",
            "VaR": var_mc_t,
            "ES/CVaR": es_mc_t,
            "VaR (%)": var_mc_t * 100,
            "ES/CVaR (%)": es_mc_t * 100
        })

    return pd.DataFrame(resultados)


def calcular_medidas_rolling(returns, window=252):
    """
    Calcula VaR y ES con rolling window de 252 rendimientos.

    Importante:
    Se usa shift(1) para que la medida del día t se calcule con los 252 días anteriores,
    y no con el rendimiento del mismo día t.
    """

    media_movil = returns.rolling(window=window).mean().shift(1)
    desviacion_movil = returns.rolling(window=window).std().shift(1)

    # VaR paramétrico normal móvil.
    var_95_movil = norm.ppf(1 - 0.95, media_movil, desviacion_movil)
    var_99_movil = norm.ppf(1 - 0.99, media_movil, desviacion_movil)

    # VaR histórico móvil.
    var_95_hist_movil = returns.rolling(window=window).quantile(1 - 0.95).shift(1)
    var_99_hist_movil = returns.rolling(window=window).quantile(1 - 0.99).shift(1)

    # ES paramétrico normal móvil.
    z_95 = norm.ppf(1 - 0.95)
    z_99 = norm.ppf(1 - 0.99)

    es_95_param_movil = media_movil - desviacion_movil * (norm.pdf(z_95) / (1 - 0.95))
    es_99_param_movil = media_movil - desviacion_movil * (norm.pdf(z_99) / (1 - 0.99))

    # ES histórico móvil.
    # El shift se aplica después porque cada ventana debe predecir el siguiente rendimiento.
    es_95_hist_movil = returns.rolling(window=window).apply(
        lambda x: x[x <= x.quantile(1 - 0.95)].mean(),
        raw=False
    ).shift(1)

    es_99_hist_movil = returns.rolling(window=window).apply(
        lambda x: x[x <= x.quantile(1 - 0.99)].mean(),
        raw=False
    ).shift(1)

    tabla_rolling = pd.DataFrame({
        "Rendimientos": returns * 100,
        "VaR 95% paramétrico": var_95_movil * 100,
        "VaR 99% paramétrico": var_99_movil * 100,
        "VaR 95% histórico": var_95_hist_movil * 100,
        "VaR 99% histórico": var_99_hist_movil * 100,
        "ES 95% paramétrico": es_95_param_movil * 100,
        "ES 99% paramétrico": es_99_param_movil * 100,
        "ES 95% histórico": es_95_hist_movil * 100,
        "ES 99% histórico": es_99_hist_movil * 100
    }).dropna()

    return tabla_rolling


# ============================================================
# SIDEBAR
# ============================================================

acciones = {
    "Chubb Limited": "CB",
    "Corporación Actinver": "ACTINVRB.MX",
    "BBVA": "BBVA.MX"
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

# ============================================================
# DESCARGA Y CÁLCULOS BASE
# ============================================================

df, df_dia, precios, returns = descargar_datos(ticker)

precio_actual = float(precios.iloc[-1])
precio_anterior = float(precios.iloc[-2])
cambio = precio_actual - precio_anterior
cambio_pct = cambio / precio_anterior

media_rend = returns.mean()
desviacion_rend = returns.std()
kurtosis_rend = kurtosis(returns)
skewness_rend = skew(returns)

# ============================================================
# RESUMEN
# ============================================================

if seccion == "Resumen":

    st.markdown('<div class="market-text">Mercado · Delayed Quote · Fuente: Yahoo Finance</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="company-title">{accion_nombre} ({ticker})</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        st.markdown('<div class="section-text">Precio actual</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="price-main">{precio_actual:.2f}</span>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-text">Cambio diario</div>', unsafe_allow_html=True)

        clase = "price-red" if cambio < 0 else "price-blue"
        signo = "+" if cambio > 0 else ""

        st.markdown(
            f'<span class="{clase}">{signo}{cambio:.2f} ({signo}{cambio_pct:.2%})</span>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown('<div class="section-text">Estado del dato</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-text" style="font-size: 22px; font-weight: 700;">Último precio disponible</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-text">
                <b>Activo seleccionado:</b> {accion_nombre}<br>
                <b>Ticker:</b> {ticker}<br>
                <b>Periodo histórico:</b> datos diarios descargados desde 2010.<br>
                <b>Uso:</b> análisis de rendimientos, VaR, ES/CVaR, rolling windows y violaciones.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title">Precio del día</div>', unsafe_allow_html=True)

    precios_dia = df_dia["Close"].dropna()

    fig, ax = crear_figura_base(figsize=(15, 6))

    color_linea = "#FF4D57" if precios_dia.iloc[-1] < precios_dia.iloc[0] else "#8ECDF8"

    ax.plot(precios_dia.index, precios_dia.values, color=color_linea, linewidth=2.3)
    ax.axhline(precios_dia.iloc[-1], color="#8ECDF8", linestyle="--", linewidth=1, alpha=0.75)

    ax.set_title(f"{accion_nombre} - Precio intradía", color="#F8FAFC", fontsize=17, fontweight="bold")
    ax.set_xlabel("Hora", color="#CBD5E1")
    ax.set_ylabel("Precio", color="#CBD5E1")

    st.pyplot(fig)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Precio actual", f"{precio_actual:.2f}")
    c2.metric("Cambio diario", f"{cambio:.2f}", f"{cambio_pct:.2%}")
    c3.metric("Media rend.", f"{media_rend:.4%}")
    c4.metric("Volatilidad", f"{desviacion_rend:.4%}")

# ============================================================
# RENDIMIENTOS ÚLTIMOS 5 DÍAS
# ============================================================

elif seccion == "Rendimientos últimos 5 días":

    st.markdown('<div class="section-title">Rendimientos de los últimos 5 días</div>', unsafe_allow_html=True)

    tabla_5d = pd.DataFrame({
        "Precio": precios.tail(6),
        "Rendimiento": returns.tail(5)
    }).dropna()

    tabla_5d["Rendimiento (%)"] = tabla_5d["Rendimiento"] * 100

    mostrar_tabla(tabla_5d[["Precio", "Rendimiento (%)"]])

    fig, ax = crear_figura_base(figsize=(13, 5))
    colores = ["#8ECDF8" if x >= 0 else "#FF4D57" for x in tabla_5d["Rendimiento (%)"]]

    ax.bar(tabla_5d.index, tabla_5d["Rendimiento (%)"], color=colores, alpha=0.9)
    ax.axhline(0, color="#CBD5E1", linewidth=1, alpha=0.6)

    ax.set_title("Rendimientos diarios recientes", color="#F8FAFC", fontsize=16, fontweight="bold")
    ax.set_xlabel("Fecha", color="#CBD5E1")
    ax.set_ylabel("Rendimiento (%)", color="#CBD5E1")

    st.pyplot(fig)

# ============================================================
# MEDIDAS DE RIESGO
# ============================================================

elif seccion == "Medidas de riesgo":

    st.markdown('<div class="section-title">Medidas de riesgo</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Media", f"{media_rend:.6f}")
    c2.metric("Desviación estándar", f"{desviacion_rend:.6f}")
    c3.metric("Exceso de curtosis", f"{kurtosis_rend:.6f}")
    c4.metric("Sesgo", f"{skewness_rend:.6f}")

    tabla_medidas = pd.DataFrame({
        "Medida": ["Media", "Desviación estándar", "Exceso de curtosis", "Sesgo"],
        "Valor": [media_rend, desviacion_rend, kurtosis_rend, skewness_rend]
    })

    mostrar_tabla(tabla_medidas)

# ============================================================
# MÉTODOS GENERALES: VaR Y ES
# ============================================================

elif seccion == "VaR y CVaR - Métodos Generales":

    st.markdown('<div class="section-title">VaR y CVaR - Métodos Generales</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                En esta sección se calcula el VaR y el ES/CVaR usando la serie completa de rendimientos.
                Se consideran los niveles de confianza 95%, 97.5% y 99%, bajo aproximaciones paramétricas,
                históricas y Monte Carlo.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tabla_var_es_general = calcular_var_es_generales(returns)

    st.markdown("### Tabla completa de VaR y ES/CVaR")
    mostrar_tabla(tabla_var_es_general)

    st.markdown("### Resumen visual por método")

    for metodo in tabla_var_es_general["Método"].unique():
        st.markdown(f"#### {metodo}")

        tabla_metodo = tabla_var_es_general[tabla_var_es_general["Método"] == metodo]

        col1, col2, col3 = st.columns(3)

        for col, (_, fila) in zip([col1, col2, col3], tabla_metodo.iterrows()):
            col.metric(
                f"VaR {fila['Nivel de confianza']}",
                f"{fila['VaR (%)']:.4f}%",
                f"ES {fila['ES/CVaR (%)']:.4f}%"
            )

# ============================================================
# ROLLING WINDOWS
# ============================================================

elif seccion == "VaR y CVaR - Rolling Windows":

    st.markdown('<div class="section-title">VaR y CVaR - Rolling Windows</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                Aquí se calcula el VaR y el ES/CVaR con una ventana móvil de 252 rendimientos.
                Cada estimación se desfasa un día para que se compare contra el rendimiento siguiente.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tabla_rolling = calcular_medidas_rolling(returns, window=252)

    st.markdown("### Últimos valores calculados")
    mostrar_tabla(tabla_rolling.tail())

    fig, ax = crear_figura_base(figsize=(15, 7))

    ax.plot(tabla_rolling.index, tabla_rolling["Rendimientos"], label="Rendimientos", color="#94A3B8", alpha=0.20, linewidth=0.8)

    ax.plot(tabla_rolling.index, tabla_rolling["VaR 95% paramétrico"], label="VaR 95% paramétrico", color="#8ECDF8", linewidth=1.8)
    ax.plot(tabla_rolling.index, tabla_rolling["VaR 99% paramétrico"], label="VaR 99% paramétrico", color="#2563EB", linewidth=1.8)

    ax.plot(tabla_rolling.index, tabla_rolling["VaR 95% histórico"], label="VaR 95% histórico", color="#FF4D57", linewidth=1.8)
    ax.plot(tabla_rolling.index, tabla_rolling["VaR 99% histórico"], label="VaR 99% histórico", color="#991B1B", linewidth=1.8)

    ax.plot(tabla_rolling.index, tabla_rolling["ES 95% paramétrico"], label="ES/CVaR 95% paramétrico", color="#F59E0B", linewidth=1.8)
    ax.plot(tabla_rolling.index, tabla_rolling["ES 99% paramétrico"], label="ES/CVaR 99% paramétrico", color="#D97706", linewidth=1.8)

    ax.plot(tabla_rolling.index, tabla_rolling["ES 95% histórico"], label="ES/CVaR 95% histórico", color="#A78BFA", linewidth=1.8)
    ax.plot(tabla_rolling.index, tabla_rolling["ES 99% histórico"], label="ES/CVaR 99% histórico", color="#7C3AED", linewidth=1.8)

    ax.set_title("Rendimientos, VaR y ES/CVaR móvil", color="#F8FAFC", fontsize=17, fontweight="bold")
    ax.set_xlabel("Fecha", color="#CBD5E1")
    ax.set_ylabel("Porcentaje", color="#CBD5E1")

    formatear_leyenda(ax, ncol=3)

    st.pyplot(fig)

# ============================================================
# COMPARACIÓN: VIOLACIONES
# ============================================================

elif seccion == "Comparación":

    st.markdown('<div class="section-title">Comparación</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                En esta sección se cuentan las violaciones de cada medida de riesgo.
                Una violación ocurre cuando el rendimiento diario observado es menor que el VaR o el ES estimado.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tabla_rolling = calcular_medidas_rolling(returns, window=252)

    columnas_riesgo = [
        "VaR 95% paramétrico",
        "VaR 99% paramétrico",
        "VaR 95% histórico",
        "VaR 99% histórico",
        "ES 95% paramétrico",
        "ES 99% paramétrico",
        "ES 95% histórico",
        "ES 99% histórico"
    ]

    df_violaciones = tabla_rolling.copy()

    resumen = []

    for columna in columnas_riesgo:

        nombre_violacion = "Violación " + columna

        df_violaciones[nombre_violacion] = (
            df_violaciones["Rendimientos"] < df_violaciones[columna]
        )

        numero_violaciones = df_violaciones[nombre_violacion].sum()
        total_dias = len(df_violaciones)
        porcentaje = numero_violaciones / total_dias * 100

        resumen.append({
            "Medida": columna,
            "Violaciones": int(numero_violaciones),
            "Total de días": total_dias,
            "Porcentaje": round(porcentaje, 4),
            "Menor a 2.5%": "Sí" if porcentaje < 2.5 else "No"
        })

    tabla_resumen_violaciones = pd.DataFrame(resumen)

    st.markdown("### Tabla de violaciones")
    mostrar_tabla(tabla_resumen_violaciones)

    c1, c2, c3 = st.columns(3)

    c1.metric("Menor porcentaje", f"{tabla_resumen_violaciones['Porcentaje'].min():.4f}%")
    c2.metric("Mayor porcentaje", f"{tabla_resumen_violaciones['Porcentaje'].max():.4f}%")
    c3.metric("Total de días", int(tabla_resumen_violaciones["Total de días"].iloc[0]))

    st.markdown("### Días donde hubo violaciones")

    fig, ax = crear_figura_base(figsize=(15, 6))

    ax.plot(
        df_violaciones.index,
        df_violaciones["Rendimientos"],
        color="#94A3B8",
        alpha=0.35,
        linewidth=0.8,
        label="Rendimientos diarios"
    )

    violaciones_95 = df_violaciones[df_violaciones["Violación VaR 95% paramétrico"]]
    violaciones_99 = df_violaciones[df_violaciones["Violación VaR 99% paramétrico"]]

    ax.scatter(
        violaciones_95.index,
        violaciones_95["Rendimientos"],
        color="#FF4D57",
        s=30,
        label="Violaciones VaR 95%"
    )

    ax.scatter(
        violaciones_99.index,
        violaciones_99["Rendimientos"],
        color="#8ECDF8",
        s=35,
        label="Violaciones VaR 99%"
    )

    ax.set_title("Días donde hubo violaciones", color="#F8FAFC", fontsize=17, fontweight="bold")
    ax.set_xlabel("Fecha", color="#CBD5E1")
    ax.set_ylabel("Rendimiento diario (%)", color="#CBD5E1")

    formatear_leyenda(ax, ncol=3)

    st.pyplot(fig)

# ============================================================
# VOLATILIDAD MÓVIL
# ============================================================

elif seccion == "Volatilidad Móvil":

    st.markdown('<div class="section-title">Volatilidad Móvil</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                Esta sección calcula el VaR usando únicamente la volatilidad móvil de 252 días,
                bajo una distribución normal estándar.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    window = 252
    alpha_95 = 0.05
    alpha_99 = 0.01

    q_95 = norm.ppf(alpha_95)
    q_99 = norm.ppf(alpha_99)

    df_var = pd.DataFrame(index=returns.index)
    df_var["Returns"] = returns

    # Se usa shift(1) para que la volatilidad del día t use solo información pasada.
    df_var["Sigma_252"] = df_var["Returns"].rolling(window=window).std().shift(1)

    df_var["VaR_95"] = q_95 * df_var["Sigma_252"]
    df_var["VaR_99"] = q_99 * df_var["Sigma_252"]

    df_results = df_var.dropna().copy()

    df_results["Violation_95"] = df_results["Returns"] < df_results["VaR_95"]
    df_results["Violation_99"] = df_results["Returns"] < df_results["VaR_99"]

    num_viol_95 = int(df_results["Violation_95"].sum())
    num_viol_99 = int(df_results["Violation_99"].sum())
    total_obs = len(df_results)

    c1, c2, c3 = st.columns(3)

    c1.metric("Total de días analizados", total_obs)
    c2.metric("Violaciones 95%", num_viol_95, f"{num_viol_95 / total_obs:.2%}")
    c3.metric("Violaciones 99%", num_viol_99, f"{num_viol_99 / total_obs:.2%}")

    tabla_resumen = pd.DataFrame({
        "Nivel": ["95%", "99%"],
        "Violaciones esperadas": [
            round(total_obs * 0.05),
            round(total_obs * 0.01)
        ],
        "Violaciones reales": [
            num_viol_95,
            num_viol_99
        ],
        "Porcentaje real": [
            num_viol_95 / total_obs * 100,
            num_viol_99 / total_obs * 100
        ]
    })

    mostrar_tabla(tabla_resumen)

    fig, ax = crear_figura_base(figsize=(15, 6))

    ax.plot(
        df_results.index,
        df_results["Returns"] * 100,
        label="Retornos diarios",
        color="#94A3B8",
        alpha=0.28,
        linewidth=0.8
    )

    ax.plot(df_results.index, df_results["VaR_95"] * 100, label="VaR 95%", color="#8ECDF8", linewidth=1.8)
    ax.plot(df_results.index, df_results["VaR_99"] * 100, label="VaR 99%", color="#FF4D57", linewidth=1.8)

    ax.scatter(
        df_results.index[df_results["Violation_95"]],
        df_results["Returns"][df_results["Violation_95"]] * 100,
        label="Violaciones 95%",
        color="#8ECDF8",
        s=22
    )

    ax.scatter(
        df_results.index[df_results["Violation_99"]],
        df_results["Returns"][df_results["Violation_99"]] * 100,
        label="Violaciones 99%",
        color="#FF4D57",
        s=28
    )

    ax.set_title(
        f"Análisis de Riesgo: VaR con volatilidad móvil 252 días - {accion_nombre} ({ticker})",
        color="#F8FAFC",
        fontsize=17,
        fontweight="bold"
    )

    ax.set_xlabel("Fecha", color="#CBD5E1")
    ax.set_ylabel("Retornos / Umbral de riesgo (%)", color="#CBD5E1")

    formatear_leyenda(ax, ncol=4)

    st.pyplot(fig)