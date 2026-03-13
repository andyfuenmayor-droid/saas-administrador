import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="ME - Control Maestro", page_icon="💎", layout="wide")

# 2. CONEXIÓN A SUPABASE
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- FUNCIONES DE SEGURIDAD ---
def check_password():
    """Retorna True si el usuario ingresó la clave correcta."""
    def password_entered():
        if st.session_state["password"] == st.secrets["MASTER_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/6195/6195700.png", width=100)
            st.title("Acceso Restringido")
            st.text_input("Ingresa la Clave Maestra", type="password", on_change=password_entered, key="password")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Clave incorrecta")
        return False
    return True

# --- INICIO DE LA APP ---
if check_password():
    
    st.title("💎 Multibanca Express - Control Maestro")
    
    # 3. CARGA DE DATOS
    try:
        res = supabase.table("perfiles").select("*").execute()
        df = pd.DataFrame(res.data)
        
        # Métricas rápidas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clientes", len(df))
        c2.metric("Activos", len(df[df['status'] == 'activo']))
        c3.metric("Premium", len(df[df['plan'] == 'Premium']))
        c4.metric("Sistema", "Online", delta="OK")

        tab1, tab2 = st.tabs(["👥 Gestión de Clientes", "🚀 Solicitudes"])

        with tab1:
            st.subheader("Listado de Suscriptores")
            st.dataframe(df[["email", "nombre_banca", "plan", "status", "fecha_vencimiento"]], use_container_width=True)

            st.divider()
            st.subheader("✏️ Editor Maestro de Licencias")
            
            # Buscador/Selector de cliente
            cliente_sel = st.selectbox("Selecciona un cliente para gestionar:", df["email"].tolist())
            datos_cliente = df[df["email"] == cliente_sel].iloc[0]

            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown(f"**Cliente:** {cliente_sel}")
                st.markdown(f"**Banca:** {datos_cliente['nombre_banca']}")
                nuevo_status = st.radio("Estado de la cuenta:", ["activo", "suspendido", "vencido"], 
                                      index=["activo", "suspendido", "vencido"].index(datos_cliente['status']), horizontal=True)

            with col_b:
                st.markdown("**Gestión de Tiempo**")
                fecha_actual = datetime.strptime(datos_cliente['fecha_vencimiento'], '%Y-%m-%d')
                opcion_tiempo = st.selectbox("Extender por:", ["No cambiar", "1 Mes", "3 Meses", "6 Meses", "1 Año"])
                
                nueva_fecha = fecha_actual
                if opcion_tiempo == "1 Mes": nueva_fecha += timedelta(days=30)
                elif opcion_tiempo == "3 Meses": nueva_fecha += timedelta(days=90)
                elif opcion_tiempo == "6 Meses": nueva_fecha += timedelta(days=180)
                elif opcion_tiempo == "1 Año": nueva_fecha += timedelta(days=365)
                
                st.info(f"Nueva fecha sugerida: {nueva_fecha.strftime('%Y-%m-%d')}")

            if st.button("💾 APLICAR CAMBIOS EN SUPABASE", use_container_width=True, type="primary"):
                with st.spinner("Actualizando..."):
                    supabase.table("perfiles").update({
                        "status": nuevo_status,
                        "fecha_vencimiento": nueva_fecha.strftime('%Y-%m-%d')
                    }).eq("email", cliente_sel).execute()
                    st.success(f"¡Cambios aplicados a {cliente_sel} con éxito!")
                    time.sleep(1)
                    st.rerun()

        with tab2:
            st.info("Aquí aparecerán los leads de tu página web pronto.")

    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")

    # Botón de cerrar sesión al final del sidebar
    with st.sidebar:
        if st.button("🚪 Cerrar Sesión Admin"):
            del st.session_state["password_correct"]
            st.rerun()
