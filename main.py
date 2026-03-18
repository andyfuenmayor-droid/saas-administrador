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

def seccion_planes():
    st.markdown("### ⚙️ Configuración Maestra de Planes (Base de Datos)")
    
    # 1. CARGAR PLANES DESDE SUPABASE
    try:
        res = supabase.table("config_planes").select("*").order("costo_base").execute()
        planes_db = res.data
        
        # 2. FORMULARIO PARA CREAR/EDITAR
        with st.expander("➕ Crear o Editar Plan en la Nube", expanded=True):
            col1, col2, col3 = st.columns(3)
            nombre = col1.text_input("Nombre del Plan")
            base = col2.number_input("Costo Base (USD)", min_value=0.0, step=10.0)
            punto = col3.number_input("Costo por Punto (USD)", min_value=0.0, step=1.0)
            desc = st.text_area("Descripción del servicio")
            
            if st.button("💾 Guardar en Base de Datos", use_container_width=True):
                if nombre:
                    data_plan = {
                        "nombre": nombre,
                        "costo_base": base,
                        "costo_por_punto": punto,
                        "descripcion": desc
                    }
                    # Upsert: Inserta si no existe, actualiza si el nombre coincide
                    supabase.table("config_planes").upsert(data_plan, on_conflict="nombre").execute()
                    st.success(f"¡Plan '{nombre}' sincronizado!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("El nombre del plan es obligatorio.")

        # 3. LISTADO DE PLANES
        if planes_db:
            st.markdown("#### Planes Activos en Sistema")
            df_p = pd.DataFrame(planes_db)
            # Reordenar para vista pro
            df_p = df_p[["nombre", "costo_base", "costo_por_punto", "descripcion"]]
            st.dataframe(df_p, use_container_width=True)
            
            # Opción para eliminar
            with st.expander("🗑️ Zona de Peligro"):
                plan_a_borrar = st.selectbox("Seleccione plan a eliminar:", [p['nombre'] for p in planes_db])
                if st.button(f"Eliminar {plan_a_borrar}"):
                    supabase.table("config_planes").delete().eq("nombre", plan_a_borrar).execute()
                    st.error(f"Plan {plan_a_borrar} eliminado.")
                    time.sleep(1)
                    st.rerun()

    except Exception as e:
        st.error(f"Error al conectar con la tabla config_planes: {e}")
        
# --- SECCIÓN DE SOLICITUDES ACTUALIZADA ---
def seccion_solicitudes():
    st.markdown("### 🚀 Gestión Estratégica de Leads")
    
    # Verificamos si hay planes creados
    if "lista_planes" not in st.session_state:
        st.warning("⚠️ Primero crea los planes en la sección de Planes.")
        return

    try:
        res = supabase.table("suscriptores_leads").select("*").execute()
        leads = res.data

        if not leads:
            st.info("💡 No hay solicitudes nuevas.")
        else:
            opciones = {f"{l['banca']} ({l['representante']})": l for l in leads}
            seleccion = st.selectbox("🎯 Seleccione un Prospecto:", options=opciones.keys())
            
            if seleccion:
                lead = opciones[seleccion]
                st.divider()
                
                col_info, col_planes = st.columns([1, 1.2])
                
                with col_info:
                    st.markdown("##### 📄 Datos del Expediente")
                    st.info(f"**Empresa:** {lead['banca']}\n\n**Titular:** {lead['representante']}\n\n**Puntos:** {lead['puntos_venta']}")
                    if st.button("✅ Marcar como Procesado"):
                        supabase.table("suscriptores_leads").delete().eq("id", lead['id']).execute()
                        st.rerun()

                with col_planes:
                    st.markdown("##### 💰 Cotizador basado en tus Planes")
                    
                    # SELECTOR BASADO EN TUS PLANES CREADOS
                    nombres_planes = [p['nombre'] for p in st.session_state.lista_planes]
                    plan_sel = st.selectbox("Usar Plan:", nombres_planes)
                    
                    # Buscar datos del plan seleccionado
                    datos_plan = next(item for item in st.session_state.lista_planes if item["nombre"] == plan_sel)
                    
                    pts = int(lead['puntos_venta'])
                    total = datos_plan['base'] + (pts * datos_plan['punto'])
                    
                    st.markdown(f"""
                    <div style='background: #f0f9ff; padding: 15px; border-radius: 10px; border-left: 5px solid #0369a1;'>
                        <strong style='color: #0369a1;'>{plan_sel}</strong><br>
                        <h3 style='margin: 10px 0;'>Total: ${total} USD</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    # --- WHATSAPP ---
                    tel_clean = "".join(filter(str.isdigit, str(lead['telefono'])))
                    msg_base = (
                        f"Hola *{lead['representante']}*. 👋\n"
                        f"Recibimos tu solicitud para *{lead['banca']}*.\n"
                        f"Propuesta para tus {pts} puntos:\n\n"
                        f"🏆 *Plan: {plan_sel}*\n"
                        f"💰 *Inversión Anual: ${total} USD*\n\n"
                        f"¿Te interesa activar el servicio?"
                    )
                    msg_url = msg_base.replace(' ', '%20').replace('\n', '%0A')
                    st.link_button("🟢 ENVIAR POR WHATSAPP", f"https://wa.me/{tel_clean}?text={msg_url}", use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# --- EN TU BLOQUE PRINCIPAL (Tabs) ---
# tab1, tab2, tab3 = st.tabs(["👥 Clientes", "🚀 Solicitudes", "⚙️ Config. Planes"])
# with tab1: ...
# with tab2: seccion_solicitudes()
# with tab3: seccion_planes()
            
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
