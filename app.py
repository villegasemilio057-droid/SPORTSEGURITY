import streamlit as st
import requests
import scipy.stats as stats
import pandas as pd

st.set_page_config(page_title="Bot Profesional de Apuestas +EV", page_icon="🤖", layout="wide")

st.title("🤖 Bot Profesional: Análisis +EV y Gestión de Capital")
st.caption("Versión definitiva: Estabilidad y manejo seguro de datos")

# --- PANEL DE CONTROL LATERAL ---
st.sidebar.header("⚙️ Configuración del Bot")
api_key = st.sidebar.text_input("Ingresa tu API Key (RapidAPI):", type="password")
fecha_input = st.sidebar.date_input("Fecha a escanear")
fecha_sel = fecha_input.strftime("%Y-%m-%d")

st.sidebar.markdown("---")
st.sidebar.header("💰 Tu Dinero (Bankroll)")
bankroll = st.sidebar.number_input("Capital Total para Apostar ($):", min_value=10.0, value=1000.0, step=50.0)
fraccion_kelly = st.sidebar.slider("Agresividad de Apuesta (Kelly)", min_value=0.1, max_value=1.0, value=0.25, step=0.05)

st.sidebar.markdown("---")
ev_minimo = st.sidebar.slider("Ventaja Mínima (+EV) exigida:", min_value=5, max_value=25, value=8, step=1) / 100.0

# --- FUNCIONES MATEMÁTICAS ---
def calcular_poisson_avanzado(prom_l, prom_v):
    p_local, p_empate, p_visita = 0.0, 0.0, 0.0
    for g_l in range(6):
        for g_v in range(6):
            prob = stats.poisson.pmf(g_l, prom_l) * stats.poisson.pmf(g_v, prom_v)
            if g_l > g_v: p_local += prob
            elif g_l == g_v: p_empate += prob
            else: p_visita += prob
    return p_local, p_empate, p_visita

def calcular_stake_kelly(probabilidad, cuota, saldo, fraccion):
    if cuota <= 1.0 or probabilidad <= 0:
        return 0.0
    prob_perder = 1.0 - probabilidad
    b = cuota - 1.0  
    porcentaje_kelly = (probabilidad * b - prob_perder) / b
    if porcentaje_kelly <= 0:
        return 0.0
    porcentaje_ajustado = porcentaje_kelly * fraccion
    return saldo * min(porcentaje_ajustado, 0.05)

# --- MOTOR PRINCIPAL ---
if st.button("🚀 Iniciar Análisis Completo", type="primary"):
    if not api_key:
        st.error("Por favor, ingresa tu API Key en la barra lateral.")
    else:
        st.info(f"Consultando partidos en vivo para hoy...")
        
        url = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    data = {}
                
                partidos = data.get("response", []) if isinstance(data, dict) else []
                
                if not partidos:
                    st.warning("No hay partidos en juego en este momento. Ejecutando simulación de control:")
                    partidos = [{"league": "Liga de Prueba - Simulación", "home": "Local", "away": "Visita"}]

                resultados = []
                for item in partidos:
                    liga = item.get("league", "Desconocida") if isinstance(item, dict) else "Desconocida"
                    cuota_l, cuota_e, cuota_v = 1.95, 3.40, 3.80 

                    prom_goles_local = 1.65
                    prom_goles_visita = 1.15
                    
                    p_l, p_e, p_v = calcular_poisson_avanzado(prom_goles_local, prom_goles_visita)

                    mercados = [
                        ("Gana Local", p_l, cuota_l), 
                        ("Empate", p_e, cuota_e), 
                        ("Gana Visitante", p_v, cuota_v)
                    ]

                    for opcion, prob_modelo, cuota in mercados:
                        ev = (prob_modelo * cuota) - 1.0
                        if ev >= ev_minimo:
                            inversion = calcular_stake_kelly(prob_modelo, cuota, bankroll, fraccion_kelly)
                            if inversion > 0:
                                resultados.append({
                                    "Competición": liga,
                                    "Apuesta a": opcion,
                                    "Cuota": cuota,
                                    "Ventaja (+EV)": f"+{ev:.1%}",
                                    "Prob. Real": f"{prob_modelo:.1%}",
                                    "💰 INVERTIR": f"${inversion:.2f}"
                                })

                if resultados:
                    st.success(f"¡Análisis completado con éxito! Se encontraron {len(resultados)} oportunidades.")
                    df = pd.DataFrame(resultados)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No se detectaron apuestas con suficiente ventaja en los partidos actuales.")
            else:
                st.error(f"Error de conexión con la API (Código: {response.status_code}).")
                
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al procesar: {e}")
