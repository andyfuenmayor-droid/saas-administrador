import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import time

# 1. CONFIGURACIÓN DE PÁGINA (Modo Ancho y Profesional)
st.set_page_config(
    page_title="ME - Panel de Control SaaS",
    page_icon="💎",
    layout="wide"
)

# 2. CONEXIÓN A SUPABASE (Usa tus mismas credenciales)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

def main():
    # Título Principal
    st.title("💎 Multibanca Express - Control Maestro")
    st.info("Bienvenido Andy. Desde aquí gestionas todas las suscripciones de tu software.")

    # 3. MÉTRICAS EN TIEMPO REAL
    try:
        res_perfiles = supabase.table("perfiles").select("*").execute()
        df_p = pd.DataFrame(res_perfiles.data)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clientes Totales", len(df_p))
        c2.metric("Planes Premium", len(df_p[df_p['plan'] == 'Premium']))
        c3.metric("Bancas Activas", len(df_p[df_p['status'] == 'activo']))
        c4.metric("Vencimientos Mes", "3", "Pendientes") # Lógica a calcular
    except:
        st.error("Error al cargar métricas de Supabase.")

    st.divider()

    # 4. TABS DE GESTIÓN
    tab1, tab2, tab3 = st.tabs(["👥 Suscriptores", "📝 Solicitudes (Leads)", "🛠️ Configuración"])

    with tab1:
        st.subheader("Base de Datos de Clientes")
        if not df_p.empty:
            # Mostramos la tabla filtrada para que sea legible
            st.dataframe(df_p[["email", "nombre_banca", "plan", "status", "fecha_vencimiento"]], use_container_width=True)
            
            st.markdown("### ✏️ Editar Suscripción")
            with st.expander("Abrir Editor de Cliente"):
                with st.form("editor_cliente"):
                    user_email = st.selectbox("Seleccionar Email", df_p["email"].tolist())
                    col_p, col_s, col_f = st.columns(3)
                    
                    nuevo_plan = col_p.selectbox("Nuevo Plan", ["Básico", "Premium", "Ilimitado"])
                    nuevo_status = col_s.selectbox("Estado", ["activo", "suspendido", "vencido"])
                    nueva_fecha = col_f.date_input("Extender Vencimiento")
                    
                    if st.form_submit_button("ACTUALIZAR LICENCIA"):
                        supabase.table("perfiles").update({
                            "plan": nuevo_plan,
                            "status": nuevo_status,
                            "fecha_vencimiento": str(nueva_fecha)
                        }).eq("email", user_email).execute()
                        st.success(f"✅ ¡Licencia de {user_email} actualizada!")
                        time.sleep(1)
                        st.rerun()
        else:
            st.warning("No hay suscriptores registrados.")

    with tab2:
        st.subheader("Interesados desde la Web")
        # Aquí cargarías tu tabla de leads
        st.info("Aquí aparecerán los correos de las personas que se registran en tu página principal.")

    with tab3:
        st.subheader("Ajustes del Sistema")
        if st.button("🔄 Refrescar Conexión con Supabase"):
            st.cache_resource.clear()
            st.rerun()

if __name__ == "__main__":
    main()
