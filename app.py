import streamlit as st
import scipy.stats as stats
from datetime import datetime, time

st.set_page_config(page_title="MatchPulse | Draftea Experience", page_icon="⚡", layout="centered")

# --- ESTILOS CSS AVANZADOS EXACTO ESTILO DRAFTEA ---
st.markdown("""
    <style>
    /* Fondo general oscuro estilo app móvil */
    .stApp {
        background-color: #121418;
        color: #ffffff;
    }
    
    /* Contenedor tipo tarjeta Draftea */
    .draftea-card {
        background: #1c2128;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    
    /* Encabezado de liga y hora */
    .league-header {
        font-size: 11px;
        font-weight: 700;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Nombres de los equipos */
    .team-title {
        font-size: 18px;
        font-weight: 800;
        color: #f0f6fc;
        margin: 8px 0;
    }
    
    /* Botones de selección de mercado estilo Draftea */
    .stButton>button {
        width: 100%;
        background-color: #21262d;
        color: #c9d1d9;
        font-weight: 700;
        border-radius: 10px;
        border: 1px solid #30363d;
        padding: 10px;
        font-size: 13px;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #238636;
        color: white;
        border-color: #2ea043;
    }
    
    /* Insignias de riesgo */
    .badge-low { background-color: #238636; color: white; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; }
    .badge-med { background-color: #9e6a03; color: white; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; }
    .badge-high { background-color: #da3633; color: white; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Título minimalista estilo app
st.markdown("<h2 style='text-align: center; font-weight: 900; color: #58a6ff;'>⚡ MATCHPULSE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 13px;'>Elige tu jugada, analiza el riesgo y gestiona tu bankroll</p>", unsafe_allow_html=True)

# --- CONFIGURACIÓN OCULTA ---
with st.expander("⚙️ Ajustes de Bankroll ($ MXN)"):
    fecha_input = st.date_input("Fecha a consultar", value=datetime.today())
    fecha_sel = fecha_input.strftime("%Y-%m-%d")
    bankroll = st.number_input("Presupuesto Total:", min_value=100.0, value=5000.0, step=500.0)

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
    if prob > 0.55: return '<span class="badge-low">🟢 BAJO</span>'
    elif prob > 0.38: return '<span class="badge-med">🟡 MEDIO</span>'
    else: return '<span class="badge-high">🔴 ALTO</span>'

# --- MOTOR DE CARTELERA ---
hora_actual = datetime.now().time()

partidos_totales = [
    {
        "league": "UEFA Nations League 🇪🇺", 
        "home": "Croacia", "away": "England", 
        "fecha": fecha_sel, "time": "17:00", 
        "cuota_l": 2.90, "cuota_e": 3.20, "cuota_v": 2.40,
        "goles_l": 1.20, "goles_v": 1.40
    },
    {
        "league": "Amistoso Internacional 🌍", 
        "home": "USA", "away": "Mexico", 
        "fecha": fecha_sel, "time": "19:07", 
        "cuota_l": 2.45, "cuota_e": 3.10, "cuota_v": 2.95,
        "goles_l": 1.35, "goles_v": 1.30
    },
    {
        "league": "Amistoso Internacional 🌍", 
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
    },
    {
        "league": "UEFA Nations League 🇪🇺", 
        "home": "Spain", "away": "Czechia", 
        "fecha": fecha_sel, "time": "20:45", 
        "cuota_l": 1.30, "cuota_e": 5.00, "cuota_v": 9.50,
        "goles_l": 2.80, "goles_v": 0.50
    }
]

# Filtrar partidos ya jugados
partidos_filtrados = []
for p in partidos_totales:
    h, m = map(int, p["time"].split(":"))
    if time(h, m) >= hora_actual:
        partidos_filtrados.append(p)

if not partidos_filtrados:
    st.warning("⏰ No hay más partidos pendientes por disputarse hoy. ¡Vuelve mañana para la nueva cartelera!")
else:
    for item in partidos_filtrados:
        liga = item["league"]
        local = item["home"]
        visitante = item["away"]
        horario = item["time"]
        c_l = item["cuota_l"]
        c_e = item["cuota_e"]
        c_v = item["cuota_v"]
        
        p_l, p_e, p_v = calcular_poisson(item["goles_l"], item["goles_v"])

        # Estructura visual exacta de tarjeta Draftea
        with st.container():
            st.markdown(f"""
                <div class="draftea-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="league-header">{liga}</span>
                        <span style="font-size: 11px; color: #58a6ff; font-weight: bold;">⏰ {horario} HRS</span>
                    </div>
                    <div class="team-title">🏠 {local} vs 🚌 {visitante}</div>
                </div>
            """, unsafe_allow_html=True)

            # Botones interactivos de selección rápida de cuotas estilo Draftea
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                inv_l = calcular_stake(p_l, c_l, bankroll)
                if st.button(f"1️⃣ {local}\n(Cuota {c_l})", key=f"l_{local}_{visitante}"):
                    st.success(f"Apuesta seleccionada: Gana {local} | Invertir: ${inv_l:,.2f} MXN ({obtener_semaforo(p_l)})")
            with col_b2:
                inv_e = calcular_stake(p_e, c_e, bankroll)
                if st.button(f"🤝 Empate\n(Cuota {c_e})", key=f"e_{local}_{visitante}"):
                    st.success(f"Apuesta seleccionada: Empate | Invertir: ${inv_e:,.2f} MXN ({obtener_semaforo(p_e)})")
            with col_b3:
                inv_v = calcular_stake(p_v, c_v, bankroll)
                if st.button(f"2️⃣ {visitante}\n(Cuota {c_v})", key=f"v_{local}_{visitante}"):
                    st.success(f"Apuesta seleccionada: Gana {visitante} | Invertir: ${inv_v:,.2f} MXN ({obtener_semaforo(p_v)})")
            
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
