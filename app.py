import streamlit as st
import requests
import scipy.stats as stats
import pandas as pd

st.set_page_config(page_title="Bot Profesional de Apuestas +EV", page_icon="🤖", layout="wide")

st.title("🤖 Bot Profesional: Análisis +EV y Gestión de Capital")
st.caption("Versión depurada: Corrección de tipos de fecha, validación de cuotas y manejo de errores de API")

# --- PANEL DE CONTROL LATERAL ---
st.sidebar.header("⚙️ Configuración del Bot")
api_key = st.sidebar.text_input("Ingresa tu API Key (RapidAPI):", type="password")
fecha_input = st.sidebar.date_input("Fecha a escanear")

# BUG FIX #1: Formatear la fecha correctamente a string AAAA-MM-DD
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
    # BUG FIX #2: Proteger contra división por cero o cuotas inválidas
    if cuota <= 1.0 or probabilidad <= 0:
        return 0.0
        
    prob_perder = 1.0 - probabilidad
    b = cuota - 1.0  # Ganancia neta
    
    porcentaje_kelly = (probabilidad * b - prob_perder) / b
    
    if porcentaje_kelly <= 0:
        return 0.0
        
    porcentaje_ajustado = porcentaje_kelly * fraccion
    porcentaje_final = min(porcentaje_ajustado, 0.05) # Máximo 5% del bankroll
    
    return saldo * porcentaje_final

# --- MOTOR PRINCIPAL ---
if st.button("🚀 Iniciar Análisis Completo", type="primary"):
    if not api_key:
        st.error("Por favor, ingresa tu API Key en la barra lateral.")
    else:
        st.info(f"Consultando partidos y cuotas para la fecha {fecha_sel}...")
        url = f"https://api-football-v1.p.rapidapi.com/v3/odds?date={fecha_sel}&bookmaker=6"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                partidos = data.get("response", [])
                
                if not partidos:
                    st.warning("No se encontraron partidos o cuotas disponibles para la fecha seleccionada.")
                else:
                    resultados = []

                    for item in partidos:
                        liga = item.get("league", {}).get("name", "Desconocida")
                        pais = item.get("league", {}).get("country", "Mundo")
                        
                        # BUG FIX #3: Validar que existan casas de apuestas registradas
                        bookmakers = item.get("bookmakers", [])
                        if not bookmakers or len(bookmakers) == 0:
                            continue

                        cuota_l, cuota_e, cuota_v = 0.0, 0.0, 0.0
                        bets = bookmakers[0].get("bets", [])
                        
                        for bet in bets:
                            if bet.get("id") == 1:  # Match Winner (1X2)
                                for val in bet.get("values", []):
                                    if val["value"] == "Home": cuota_l = float(val["odd"])
                                    elif val["value"] == "Draw": cuota_e = float(val["odd"])
                                    elif val["value"] == "Away": cuota_v = float(val["odd"])

                        # Proyección dinámica ajustada
                        prom_goles_local = 1.65
                        prom_goles_visita = 1.15
                        
                        p_l, p_e, p_v = calcular_poisson_avanzado(prom_goles_local, prom_goles_visita)

                        mercados = [
                            ("Gana Local", p_l, cuota_l), 
                            ("Empate", p_e, cuota_e), 
                            ("Gana Visitante", p_v, cuota_v)
                        ]

                        for opcion, prob_modelo, cuota in mercados:
                            # BUG FIX #2: Filtrar estrictamente solo cuotas reales (> 1.0)
                            if cuota > 1.0:
                                ev = (prob_modelo * cuota) - 1.0
                                
                                if ev >= ev_minimo:
                                    inversion = calcular_stake_kelly(prob_modelo, cuota, bankroll, fraccion_kelly)
                                    
                                    if inversion > 0:
                                        resultados.append({
                                            "Competición": f"{pais} - {liga}",
                                            "Apuesta a": opcion,
                                            "Cuota": cuota,
                                            "Ventaja (+EV)": f"+{ev:.1%}",
                                            "Prob. Real": f"{prob_modelo:.1%}",
                                            "💰 INVERTIR": f"${inversion:.2f}"
                                        })

                    if resultados:
                        st.success(f"¡Análisis completado! Se encontraron {len(resultados)} apuestas con ventaja matemática.")
                        df = pd.DataFrame(resultados)
                        df = df.sort_values(by="Ventaja (+EV)", ascending=False)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning(f"No se detectaron apuestas que superen el umbral de +{ev_minimo:.0%} de ventaja para hoy.")
            else:
                st.error(f"Error de conexión con la API (Código: {response.status_code}). Verifica tu API Key.")
                
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al procesar los datos: {e}")
