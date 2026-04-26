import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import kurtosis, skew, norm

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
# ESTILO
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

    .section-card {
        background-color: #151C26;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #263241;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 32px;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 10px;
    }

    .section-text {
        color: #CBD5E1;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# FUNCIONES
# =============================
@st.cache_data
def descargar_datos(ticker):
    df_5y = yf.download(ticker, period="5y", auto_adjust=True, progress=False)
    df_1d = yf.download(ticker, period="1d", interval="5m", auto_adjust=True, progress=False)

    if hasattr(df_5y.columns, "nlevels") and df_5y.columns.nlevels > 1:
        df_5y.columns = df_5y.columns.get_level_values(0)

    if hasattr(df_1d.columns, "nlevels") and df_1d.columns.nlevels > 1:
        df_1d.columns = df_1d.columns.get_level_values(0)

    precios = df_5y["Close"].dropna()
    rendimientos = precios.pct_change().dropna()

    return df_5y, df_1d, precios, rendimientos


def crear_figura_base():
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#11161C")
    ax.set_facecolor("#11161C")
    ax.tick_params(colors="#CBD5E1")
    ax.spines["bottom"].set_color("#334155")
    ax.spines["left"].set_color("#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.15)
    return fig, ax


# =============================
# SIDEBAR
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
# DATOS
# =============================
df, df_dia, precios, returns = descargar_datos(ticker)

precio_actual = float(precios.iloc[-1])
precio_anterior = float(precios.iloc[-2])
cambio = precio_actual - precio_anterior
cambio_pct = cambio / precio_anterior

media_rend = returns.mean()
desviacion_rend = returns.std()
kurtosis_rend = kurtosis(returns)
skewness_rend = skew(returns)

# =============================
# RESUMEN
# =============================
if seccion == "Resumen":

    st.markdown('<div class="market-text">NYSE · Delayed Quote · USD</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="company-title">{accion_nombre} ({ticker})</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        st.markdown(f'<span class="price-main">{precio_actual:.2f}</span>', unsafe_allow_html=True)

    with col2:
        clase = "price-red" if cambio < 0 else "price-blue"
        signo = "+" if cambio > 0 else ""
        st.markdown(
            f'<span class="{clase}">{signo}{cambio:.2f} ({signo}{cambio_pct:.2%})</span>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="section-text">Último precio disponible</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown('<div class="section-title">Precio del día</div>', unsafe_allow_html=True)

    precios_dia = df_dia["Close"].dropna()

    fig, ax = crear_figura_base()

    color_linea = "#FF4D57" if precios_dia.iloc[-1] < precios_dia.iloc[0] else "#8ECDF8"

    ax.plot(precios_dia.index, precios_dia.values, color=color_linea, linewidth=2)
    ax.axhline(precios_dia.iloc[-1], color="#8ECDF8", linestyle="--", linewidth=1, alpha=0.7)

    ax.set_title(f"{accion_nombre} - Precio intradía", color="#F8FAFC", fontsize=16, fontweight="bold")
    ax.set_xlabel("Hora", color="#CBD5E1")
    ax.set_ylabel("Precio", color="#CBD5E1")

    st.pyplot(fig)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Precio actual", f"${precio_actual:.2f}")
    c2.metric("Cambio diario", f"{cambio:.2f}", f"{cambio_pct:.2%}")
    c3.metric("Media rend.", f"{media_rend:.4%}")
    c4.metric("Volatilidad", f"{desviacion_rend:.4%}")

# =============================
# RENDIMIENTOS 5 DÍAS
# =============================
elif seccion == "Rendimientos últimos 5 días":

    st.markdown('<div class="section-title">Rendimientos de los últimos 5 días</div>', unsafe_allow_html=True)

    tabla_5d = pd.DataFrame({
        "Precio": precios.tail(6),
        "Rendimiento": returns.tail(5)
    }).dropna()

    tabla_5d["Rendimiento (%)"] = tabla_5d["Rendimiento"] * 100

    st.dataframe(tabla_5d[["Precio", "Rendimiento (%)"]], use_container_width=True)

    fig, ax = crear_figura_base()
    ax.bar(tabla_5d.index, tabla_5d["Rendimiento (%)"])
    ax.set_title("Rendimientos diarios recientes", color="#F8FAFC", fontsize=16, fontweight="bold")
    ax.set_xlabel("Fecha", color="#CBD5E1")
    ax.set_ylabel("Rendimiento (%)", color="#CBD5E1")
    st.pyplot(fig)

# =============================
# MEDIDAS DE RIESGO
# =============================
elif seccion == "Medidas de riesgo":

    st.markdown('<div class="section-title">Medidas de riesgo</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Media", f"{media_rend:.6f}")
    c2.metric("Desviación estándar", f"{desviacion_rend:.6f}")
    c3.metric("Kurtosis", f"{kurtosis_rend:.6f}")
    c4.metric("Sesgo", f"{skewness_rend:.6f}")

    tabla_medidas = pd.DataFrame({
        "Medida": ["Media", "Desviación estándar", "Kurtosis", "Sesgo"],
        "Valor": [media_rend, desviacion_rend, kurtosis_rend, skewness_rend]
    })

    st.dataframe(tabla_medidas, use_container_width=True)

# =============================
# VaR Y CVaR - MÉTODOS GENERALES
# =============================
elif seccion == "VaR y CVaR - Métodos Generales":

    st.markdown('<div class="section-title">VaR y CVaR - Métodos Generales</div>', unsafe_allow_html=True)

    gl = len(returns) - 1

    var_par_n_95 = norm.ppf(1 - 0.95, loc=media_rend, scale=desviacion_rend)
    var_par_n_99 = norm.ppf(1 - 0.99, loc=media_rend, scale=desviacion_rend)
    var_par_n_995 = norm.ppf(1 - 0.995, loc=media_rend, scale=desviacion_rend)

    var_par_t_95 = stats.t.ppf(1 - 0.95, gl, loc=media_rend, scale=desviacion_rend)
    var_par_t_99 = stats.t.ppf(1 - 0.99, gl, loc=media_rend, scale=desviacion_rend)
    var_par_t_995 = stats.t.ppf(1 - 0.995, gl, loc=media_rend, scale=desviacion_rend)

    tabla_var_general = pd.DataFrame({
        "Método": [
            "Normal",
            "Normal",
            "Normal",
            "T-Student",
            "T-Student",
            "T-Student"
        ],
        "Nivel de confianza": [
            "95%",
            "99%",
            "99.5%",
            "95%",
            "99%",
            "99.5%"
        ],
        "VaR": [
            var_par_n_95,
            var_par_n_99,
            var_par_n_995,
            var_par_t_95,
            var_par_t_99,
            var_par_t_995
        ],
        "VaR (%)": [
            var_par_n_95 * 100,
            var_par_n_99 * 100,
            var_par_n_995 * 100,
            var_par_t_95 * 100,
            var_par_t_99 * 100,
            var_par_t_995 * 100
        ]
    })

    st.dataframe(tabla_var_general, use_container_width=True)

# =============================
# VaR Y CVaR - ROLLING WINDOWS
# =============================
elif seccion == "VaR y CVaR - Rolling Windows":

    st.markdown('<div class="section-title">VaR y CVaR - Rolling Windows</div>', unsafe_allow_html=True)

    window = 252

    media_movil = returns.rolling(window=window).mean()
    desviacion_movil = returns.rolling(window=window).std()

    var_95_movil = norm.ppf(1 - 0.95, media_movil, desviacion_movil)
    var_99_movil = norm.ppf(1 - 0.99, media_movil, desviacion_movil)

    var_95_hist_movil = returns.rolling(window=window).quantile(1 - 0.95)
    var_99_hist_movil = returns.rolling(window=window).quantile(1 - 0.99)

    z_95 = norm.ppf(1 - 0.95)
    z_99 = norm.ppf(1 - 0.99)

    es_95_param_movil = media_movil - desviacion_movil * (norm.pdf(z_95) / (1 - 0.95))
    es_99_param_movil = media_movil - desviacion_movil * (norm.pdf(z_99) / (1 - 0.99))

    es_95_hist_movil = returns.rolling(window=window).apply(
        lambda x: x[x <= x.quantile(1 - 0.95)].mean(),
        raw=False
    )

    es_99_hist_movil = returns.rolling(window=window).apply(
        lambda x: x[x <= x.quantile(1 - 0.99)].mean(),
        raw=False
    )

    tabla_rolling = pd.DataFrame({
        "Rendimientos": returns * 100,
        "VaR 95% paramétrico": var_95_movil * 100,
        "VaR 99% paramétrico": var_99_movil * 100,
        "VaR 95% histórico": var_95_hist_movil * 100,
        "VaR 99% histórico": var_99_hist_movil * 100,
        "ES/CVaR 95% paramétrico": es_95_param_movil * 100,
        "ES/CVaR 99% paramétrico": es_99_param_movil * 100,
        "ES/CVaR 95% histórico": es_95_hist_movil * 100,
        "ES/CVaR 99% histórico": es_99_hist_movil * 100
    }).dropna()

    st.dataframe(tabla_rolling.tail(), use_container_width=True)

    fig, ax = crear_figura_base()

    ax.plot(tabla_rolling.index, tabla_rolling["Rendimientos"], label="Rendimientos", alpha=0.35)
    ax.plot(tabla_rolling.index, tabla_rolling["VaR 95% paramétrico"], label="VaR 95% paramétrico")
    ax.plot(tabla_rolling.index, tabla_rolling["VaR 99% paramétrico"], label="VaR 99% paramétrico")
    ax.plot(tabla_rolling.index, tabla_rolling["VaR 95% histórico"], label="VaR 95% histórico")
    ax.plot(tabla_rolling.index, tabla_rolling["VaR 99% histórico"], label="VaR 99% histórico")
    ax.plot(tabla_rolling.index, tabla_rolling["ES/CVaR 95% paramétrico"], label="ES/CVaR 95% paramétrico")
    ax.plot(tabla_rolling.index, tabla_rolling["ES/CVaR 99% paramétrico"], label="ES/CVaR 99% paramétrico")
    ax.plot(tabla_rolling.index, tabla_rolling["ES/CVaR 95% histórico"], label="ES/CVaR 95% histórico")
    ax.plot(tabla_rolling.index, tabla_rolling["ES/CVaR 99% histórico"], label="ES/CVaR 99% histórico")

    ax.set_title("Rendimientos, VaR y ES/CVaR móvil", color="#F8FAFC", fontsize=16, fontweight="bold")
    ax.set_xlabel("Fecha", color="#CBD5E1")
    ax.set_ylabel("Porcentaje", color="#CBD5E1")

    legend = ax.legend(loc="best")
    for text in legend.get_texts():
        text.set_color("#E5E7EB")

    st.pyplot(fig)

# =============================
# COMPARACIÓN
# =============================
elif seccion == "Comparación":

    st.markdown('<div class="section-title">Comparación</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <div class="section-text">
                Esta sección queda pendiente para el inciso e).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================
# VOLATILIDAD MÓVIL
# =============================
elif seccion == "Volatilidad Móvil":

    st.markdown('<div class="section-title">Volatilidad Móvil</div>', unsafe_allow_html=True)

    window = 252
    alpha_95 = 0.05
    alpha_99 = 0.01

    q_95 = norm.ppf(alpha_95)
    q_99 = norm.ppf(alpha_99)

    df_var = pd.DataFrame(index=returns.index)
    df_var["Returns"] = returns
    df_var["Sigma_252"] = df_var["Returns"].rolling(window=window).std()
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
            num_viol_95 / total_obs,
            num_viol_99 / total_obs
        ]
    })

    st.dataframe(tabla_resumen, use_container_width=True)

    fig, ax = crear_figura_base()

    ax.plot(df_results.index, df_results["Returns"], label="Retornos diarios", color="lightgray", alpha=0.6)
    ax.plot(df_results.index, df_results["VaR_95"], label="VaR 95%", color="#8ECDF8", linewidth=1.5)
    ax.plot(df_results.index, df_results["VaR_99"], label="VaR 99%", color="#FF4D57", linewidth=1.5)

    ax.scatter(
        df_results.index[df_results["Violation_95"]],
        df_results["Returns"][df_results["Violation_95"]],
        label="Violaciones 95%",
        color="#8ECDF8",
        s=20
    )

    ax.scatter(
        df_results.index[df_results["Violation_99"]],
        df_results["Returns"][df_results["Violation_99"]],
        label="Violaciones 99%",
        color="#FF4D57",
        s=25
    )

    ax.set_title(
        f"Análisis de Riesgo: VaR móvil 252 días - {accion_nombre} ({ticker})",
        color="#F8FAFC",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlabel("Fecha", color="#CBD5E1")
    ax.set_ylabel("Retornos / Umbral de riesgo", color="#CBD5E1")

    legend = ax.legend(loc="upper right")
    for text in legend.get_texts():
        text.set_color("#E5E7EB")

    st.pyplot(fig)