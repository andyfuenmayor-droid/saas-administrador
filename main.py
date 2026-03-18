import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import time

# =============================================================
# 1. CONFIGURACIÓN DE PÁGINA (ESTILO SAAS)
# =============================================================
st.set_page_config(
    page_title="ME - Control Maestro", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS para el look SaaS Profesional
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    [data-testid="stHeader"] { background: #1e293b; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; }
    .stTabs [aria-selected="true"] { border-bottom: 2px solid #02ab21 !important; color: #02ab21 !important; }
    </style>
""", unsafe_allow_html=True)

# 2. CONEXIÓN A SUPABASE (MODO ADMIN SEGURO)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    # Intentamos usar la Service Key para saltar el RLS del admin. 
    # Si no existe en secrets, usa la key normal.
    key = st.secrets.get("SUPABASE_SERVICE_KEY", st.secrets["SUPABASE_KEY"])
    return create_client(url, key)

supabase = init_connection()
# =============================================================
# 3. SEGURIDAD DE ACCESO
# =============================================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["MASTER_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 30px; background: white; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);'>
                    <h1 style='color: #1e293b; font-size: 24px;'>🛡️ Panel Administrador</h1>
                    <p style='color: #64748b;'>Ingresa la clave maestra para continuar</p>
                </div>
            """, unsafe_allow_html=True)
            st.text_input("", type="password", on_change=password_entered, key="password", placeholder="Clave Maestra")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Clave incorrecta")
        return False
    return True

# =============================================================
# 4. COMPONENTES DEL DASHBOARD
# =============================================================

def mostrar_metricas(df):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Clientes", len(df), help="Total de suscriptores en la base de datos")
    with c2:
        activos = len(df[df['status'] == 'activo'])
        st.metric("Cuentas Activas", activos, delta=f"{(activos/len(df)*100):.1f}%")
    with c3:
        premium = len(df[df['plan'] == 'Premium'])
        st.metric("Cuentas Premium", premium)
    with c4:
        st.metric("Estatus Sistema", "Online", delta="OK", delta_color="normal")

# --- 2. SECCIÓN DE SOLICITUDES (BLINDADA) ---
def seccion_solicitudes():
    st.markdown("### 🚀 Solicitudes de Afiliación Recientes")
    
    # Botón de refresco total
    if st.button("🔄 Forzar Sincronización Real", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # CONSULTA DIRECTA SIN FILTROS
        res = supabase.table("suscriptores_leads").select("*").execute()
        leads = res.data

        if not leads or len(leads) == 0:
            st.markdown("""
                <div style='text-align: center; padding: 40px; background: white; border-radius: 15px; border: 1px dashed #cbd5e1;'>
                    <p style='color: #64748b; font-size: 18px;'>No hay solicitudes nuevas en este momento.</p>
                    <p style='color: #94a3b8; font-size: 14px;'>Si ya enviaste una, verifica que estás usando la <b>Service Role Key</b> en los secrets.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            df_leads = pd.DataFrame(leads)
            
            # Limpieza y ordenamiento
            df_leads.columns = [c.strip() for c in df_leads.columns]
            if 'fecha' in df_leads.columns:
                df_leads['fecha'] = pd.to_datetime(df_leads['fecha'], errors='coerce')
                df_leads = df_leads.sort_values(by='fecha', ascending=False)
                df_leads['fecha'] = df_leads['fecha'].dt.strftime('%d/%m/%Y %H:%M')

            st.success(f"✅ Se encontraron {len(df_leads)} solicitudes registradas.")
            
            # Vista Tabla SaaS Pro
            st.dataframe(
                df_leads, 
                use_container_width=True,
                height=450,
                column_config={
                    "fecha": "📅 Recibido",
                    "banca": "🏦 Agencia",
                    "representante": "👤 Titular",
                    "email": "📧 Correo",
                    "telefono": "📲 WhatsApp",
                    "puntos_venta": "📍 Puntos"
                }
            )
            
            st.divider()
            if st.button("🗑️ Vaciar Historial de Leads", type="secondary"):
                # Borrado seguro
                supabase.table("suscriptores_leads").delete().neq("banca", "BORRADO_MAESTRO").execute()
                st.success("Registros eliminados.")
                st.rerun()

    except Exception as e:
        st.error(f"🚨 Fallo crítico en la consulta")
        st.code(str(e))
            
# =============================================================
# 5. LÓGICA PRINCIPAL
# =============================================================

if check_password():
    # Barra lateral SaaS
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/6195/6195700.png", width=50)
        st.title("ME Admin")
        st.write("---")
        if st.button("🚪 Cerrar Sesión"):
            del st.session_state["password_correct"]
            st.rerun()

    # Contenido principal
    try:
        # Cargar datos de clientes
        res_p = supabase.table("perfiles").select("*").execute()
        df_clientes = pd.DataFrame(res_p.data)

        st.title("💎 Multibanca Express - Control Maestro")
        mostrar_metricas(df_clientes)
        
        tab1, tab2 = st.tabs(["👥 Gestión de Clientes", "🚀 Solicitudes (Leads)"])

        with tab1:
            st.markdown("### Listado de Suscriptores")
            st.dataframe(
                df_clientes[["email", "nombre_banca", "plan", "status", "fecha_vencimiento"]], 
                use_container_width=True
            )

            with st.expander("✏️ Herramienta de Modificación de Licencias", expanded=True):
                cliente_sel = st.selectbox("Buscar cliente por Email:", df_clientes["email"].tolist())
                datos_cliente = df_clientes[df_clientes["email"] == cliente_sel].iloc[0]

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Banca:** {datos_cliente['nombre_banca']}")
                    nuevo_status = st.segmented_control(
                        "Estatus de Cuenta:", 
                        ["activo", "suspendido", "vencido"], 
                        default=datos_cliente['status']
                    )
                with col_b:
                    fecha_orig = datetime.strptime(datos_cliente['fecha_vencimiento'], '%Y-%m-%d')
                    opcion_t = st.selectbox("Extender suscripción por:", ["No cambiar", "1 Mes", "3 Meses", "6 Meses", "1 Año"])
                    
                    nueva_f = fecha_orig
                    if opcion_t == "1 Mes": nueva_f += timedelta(days=30)
                    elif opcion_t == "3 Meses": nueva_f += timedelta(days=90)
                    elif opcion_t == "6 Meses": nueva_f += timedelta(days=180)
                    elif opcion_t == "1 Año": nueva_f += timedelta(days=365)
                    
                    st.info(f"Nueva fecha: **{nueva_f.strftime('%Y-%m-%d')}**")

                if st.button("💾 GUARDAR CAMBIOS EN LA NUBE", type="primary", use_container_width=True):
                    supabase.table("perfiles").update({
                        "status": nuevo_status,
                        "fecha_vencimiento": nueva_f.strftime('%Y-%m-%d')
                    }).eq("email", cliente_sel).execute()
                    st.success("✅ Base de datos actualizada con éxito.")
                    time.sleep(1)
                    st.rerun()

        with tab2:
            # AQUÍ ES DONDE SE LLAMA A LA FUNCIÓN QUE CARGA LOS LEADS
            seccion_solicitudes()

    except Exception as e:
        st.error(f"🚨 Error crítico de conexión: {e}")
