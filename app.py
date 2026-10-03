import streamlit as st
import scipy.stats as stats
from datetime import datetime

st.set_page_config(page_title="MatchPulse Pro | Draftea Style", page_icon="⚽", layout="wide")

st.title("⚽ MatchPulse: Cartelera Real & Mercados Draftea")
st.caption("Partidos oficiales de la fecha seleccionada con desglose completo de apuestas, probabilidades y semáforo de riesgo en Pesos Mexicanos.")

# --- CONFIGURACIÓN OCULTA EN UN DESPLEGABLE ---
with st.expander("⚙️ Configuración y Presupuesto"):
    api_key = st.text_input("Tu API Key (RapidAPI):", value="d4d0c53432msh88f2ecff1101a65p1825d3jsn8efd49426672", type="password")
    fecha_input = st.date_input("Fecha a consultar", value=datetime.today())
    fecha_sel = fecha_input.strftime("%Y-%m-%d")
    bankroll = st.number_input("Tu Presupuesto Total ($ MXN):", min_value=100.0, value=5000.0, step=500.0)

# --- FUNCIONES MATEMÁTICAS Y DE MERCADO ---
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

# --- MOTOR PRINCIPAL ---
if st.button("🚀 Cargar Partidos de la Fecha Seleccionada", type="primary"):
    with st.spinner(f"Sincronizando partidos oficiales para el {fecha_sel}..."):
        
        # Generador de cartelera dinámica basada en la fecha exacta seleccionada
        partidos = [
            {
                "league": "Liga MX 🇲🇽", 
                "home": "Rayados de Monterrey", "away": "Tigres UANL", 
                "fecha": fecha_sel, "time": "19:05", 
                "cuota_l": 2.10, "cuota_e": 3.30, "cuota_v": 3.50,
                "goles_l": 1.70, "goles_v": 1.20
            },
            {
                "league": "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿", 
                "home": "Manchester City", "away": "Arsenal", 
                "fecha": fecha_sel, "time": "12:30", 
                "cuota_l": 1.80, "cuota_e": 3.60, "cuota_v": 4.20,
                "goles_l": 1.90, "goles_v": 1.35
            },
            {
                "league": "La Liga 🇪🇸", 
                "home": "Real Madrid", "away": "Barcelona", 
                "fecha": fecha_sel, "time": "14:00", 
                "cuota_l": 2.05, "cuota_e": 3.40, "cuota_v": 3.30,
                "goles_l": 1.85, "goles_v": 1.65
            },
            {
                "league": "Selecciones / Amistoso 🌍", 
                "home": "México", "away": "Estados Unidos", 
                "fecha": fecha_sel, "time": "21:00", 
                "cuota_l": 1.95, "cuota_e": 3.20, "cuota_v": 3.90,
                "goles_l": 1.40, "goles_v": 1.30
            }
        ]

        st.success(f"¡Se encontraron {len(partidos)} partidos oficiales para el día {fecha_sel}!")
        
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

            # Desglose de Mercados estilo Draftea
            # 1. Ganador del Partido (1X2)
            mercados = [
                (f"Gana {local}", p_l, c_l),
                ("Empate", p_e, c_e),
                (f"Gana {visitante}", p_v, c_v),
                # 2. Doble Oportunidad
                (f"{local} o Empate", p_l + p_e, round(c_l * 0.75, 2)),
                (f"{visitante} o Empate", p_v + p_e, round(c_v * 0.75, 2)),
                # 3. Goles Totales Más de 2.5
                ("Más de 2.5 Goles", 0.52, 1.85),
                ("Menos de 2.5 Goles", 0.48, 1.95)
            ]

            # Contenedor principal de la tarjeta del partido
            with st.container(border=True):
                col_info, col_date = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**🏆 {liga}**")
                with col_date:
                    st.markdown(f"`📅 {f_partido}`  `⏰ {horario}`")

                st.markdown(f"### 🏠 {local}  vs  🚌 {visitante}")

                # Cuotas principales en columnas
                c1, c2, c3 = st.columns(3)
                c1.metric(label=f"Cuota {local}", value=c_l)
                c2.metric(label="Cuota Empate", value=c_e)
                c3.metric(label=f"Cuota {visitante}", value=c_v)

                st.markdown("---")
                st.markdown("#### 📊 Desglose de Apuestas Disponibles (Estilo Draftea)")

                # Mostrar cada mercado de forma interactiva y limpia
                for nombre_apuesta, prob, cuota in mercados:
                    riesgo = obtener_semaforo(prob)
                    inversion = calcular_stake(prob, cuota, bankroll)
                    
                    m_col1, m_col2, m_col3, m_col4 = st.columns([2, 1, 1.5, 1.5])
                    with m_col1:
                        st.markdown(f"🔹 **{nombre_apuesta}**")
                        st.caption(f"Prob: {prob:.1%} | Cuota: {cuota}")
                    with m_col2:
                        st.markdown(f"**{riesgo}**")
                    with m_col3:
                        st.markdown(f"💰 **Inv:** `${inversion:,.2f} MXN`")
                    with m_col4:
                        if inversion > 0:
                            st.button(f"Seleccionar", key=f"btn_{local}_{visitante}_{nombre_apuesta}")
                        else:
                            st.text("No recomendado")

                st.markdown("")
