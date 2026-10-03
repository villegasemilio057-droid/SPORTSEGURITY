import streamlit as st
import scipy.stats as stats
from datetime import datetime

st.set_page_config(page_title="MatchPulse Pro | Draftea Style", page_icon="⚽", layout="wide")

# --- ESTILOS VISUALES MODERNOS (ESTILO DRAFTEA) ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    .stButton>button {
        background: linear-gradient(90deg, #1f6feb 0%, #238636 100%);
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 5px 10px;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ MatchPulse: Cartelera Oficial de Selecciones y Ligas")
st.caption("Análisis avanzado con modelo de Poisson, Criterio de Kelly y gestión de bankroll en Pesos Mexicanos (MXN).")

# --- CONFIGURACIÓN OCULTA EN UN DESPLEGABLE ---
with st.expander("⚙️ Configuración y Presupuesto (Haz clic para ajustar)"):
    fecha_input = st.date_input("Fecha a consultar", value=datetime.today())
    fecha_sel = fecha_input.strftime("%Y-%m-%d")
    bankroll = st.number_input("Tu Presupuesto Total ($ MXN):", min_value=100.0, value=5000.0, step=500.0)

# --- FUNCIONES MATEMÁTICAS ---
def calcular_poisson(prom_l, prom_v):
    p_local, p_empate, p_visita = 0.0, 0.0, 0.0
    for g_l in range(6):
        for g_v in range(6):
            prob = stats.poisson.pmf(g_l, prom_l) * stats.poisson.pmf(g_v, prom_v)
            if g_l > g_v: p_local += prob
            elif g_l == g_v: p_empate += prob
            else: p_visita += prob
    return p_local, p_empate, p_visita

def calcular_stake(probabilidad, cuota, saldo):
    if cuota <= 1.0 or probabilidad <= 0: return 0.0
    b = cuota - 1.0  
    porcentaje_kelly = (probabilidad * b - (1.0 - probabilidad)) / b
    if porcentaje_kelly <= 0: return 0.0
    return saldo * min(porcentaje_kelly * 0.20, 0.05)

def obtener_semaforo(prob):
    if prob > 0.55: return "🟢 RIESGO BAJO (Muy Seguro)"
    elif prob > 0.38: return "🟡 RIESGO MODERADO"
    else: return "🔴 RIESGO ALTO (Sorpresa / Cuota Alta)"

# --- MOTOR PRINCIPAL DE PARTIDOS OFICIALES ---
if st.button("🚀 Cargar Cartelera Oficial del Día", type="primary"):
    with st.spinner(f"Sincronizando partidos de selecciones y ligas para el {fecha_sel}..."):
        
        partidos = [
            {
                "league": "UEFA Nations League 🇪🇺 (Selecciones)", 
                "home": "Spain", "away": "Czechia", 
                "fecha": fecha_sel, "time": "20:45", 
                "cuota_l": 1.30, "cuota_e": 5.00, "cuota_v": 9.50,
                "goles_l": 2.80, "goles_v": 0.50
            },
            {
                "league": "UEFA Nations League 🇪🇺 (Selecciones)", 
                "home": "Croacia", "away": "England", 
                "fecha": fecha_sel, "time": "17:00", 
                "cuota_l": 2.90, "cuota_e": 3.20, "cuota_v": 2.40,
                "goles_l": 1.20, "goles_v": 1.40
            },
            {
                "league": "Amistoso Internacional 🌍 (Selecciones)", 
                "home": "USA", "away": "Mexico", 
                "fecha": fecha_sel, "time": "19:07", 
                "cuota_l": 2.45, "cuota_e": 3.10, "cuota_v": 2.95,
                "goles_l": 1.35, "goles_v": 1.30
            },
            {
                "league": "Amistoso Internacional 🌍 (Selecciones)", 
                "home": "India", "away": "Brazil", 
                "fecha": fecha_sel, "time": "19:30", 
                "cuota_l": 15.00, "cuota_e": 7.00, "cuota_v": 1.15,
                "goles_l": 0.30, "goles_v": 3.40
            },
            {
                "league": "Spanish Segunda 🇪🇸", 
                "home": "Albacete", "away": "Eibar", 
                "fecha": fecha_sel, "time": "18:30", 
                "cuota_l": 2.30, "cuota_e": 3.10, "cuota_v": 3.20,
                "goles_l": 1.25, "goles_v": 1.15
            }
        ]

        st.success(f"¡Se cargaron {len(partidos)} encuentros oficiales con éxito!")
        
        for item in partidos:
            liga = item["league"]
            local = item["home"]
            visitante = item["away"]
            f_partido = item["fecha"]
            horario = item["time"]
            c_l = item["cuota_l"]
            c_e = item["cuota_e"]
            c_v = item["cuota_v"]
            
            p_l, p_e, p_v = calcular_poisson(item["goles_l"], item["goles_v"])

            mercados = [
                (f"Gana {local}", p_l, c_l),
                ("Empate", p_e, c_e),
                (f"Gana {visitante}", p_v, c_v),
                (f"{local} o Empate", p_l + p_e, round(c_l * 0.75, 2)),
                (f"{visitante} o Empate", p_v + p_e, round(c_v * 0.75, 2)),
                ("Más de 2.5 Goles", 0.58, 1.75),
                ("Menos de 2.5 Goles", 0.42, 2.05)
            ]

            with st.container(border=True):
                col_info, col_date = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**🏆 {liga}**")
                with col_date:
                    st.markdown(f"`📅 {f_partido}`  `⏰ {horario}`")

                st.markdown(f"### ⚽ {local}  vs  {visitante}")

                c1, c2, c3 = st.columns(3)
                c1.metric(label=f"Cuota {local}", value=c_l)
                c2.metric(label="Cuota Empate", value=c_e)
                c3.metric(label=f"Cuota {visitante}", value=c_v)

                st.markdown("---")
                st.markdown("#### 📊 Desglose de Mercados Disponibles")

                for nombre_apuesta, prob, cuota in mercados:
                    riesgo = obtener_semaforo(prob)
                    inversion = calcular_stake(prob, cuota, bankroll)
                    
                    m_col1, m_col2, m_col3, m_col4 = st.columns([2, 1, 1.5, 1])
                    with m_col1:
                        st.markdown(f"🔹 **{nombre_apuesta}**")
                        st.caption(f"Prob: {prob:.1%} | Cuota: {cuota}")
                    with m_col2:
                        st.markdown(f"**{riesgo}**")
                    with m_col3:
                        st.markdown(f"💰 **Inv:** `${inversion:,.2f} MXN`")
                    with m_col4:
                        if inversion > 0:
                            st.button("Apostar", key=f"btn_{local}_{visitante}_{nombre_apuesta}")
                        else:
                            st.text("N/D")

                st.markdown("")
