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
        
# --- SECCIÓN DE SOLICITUDES ACTUALIZADA Y REPARADA ---
def seccion_solicitudes():
    st.markdown("### 🚀 Gestión Estratégica de Leads")
    
    # 1. VALIDACIÓN DE PLANES (Corregida para ser más flexible)
    # Verificamos tanto en session_state como si la lista tiene contenido
    planes_disponibles = st.session_state.get("lista_planes", [])
    
    if not planes_disponibles:
        st.warning("⚠️ No se encontraron planes configurados. Ve a la pestaña 'Configuración' o 'Planes' para crearlos primero.")
        # Agregamos un botón de acceso rápido para mejorar la navegación
        if st.button("Ir a Configurar Planes"):
            # Aquí podrías forzar el cambio de tab si manejas el índice en session_state
            st.info("Por favor, selecciona la pestaña ⚙️ Planes arriba.")
        return

    try:
        # 2. CARGA DE DATOS DESDE SUPABASE
        res = supabase.table("suscriptores_leads").select("*").execute()
        leads = res.data

        if not leads:
            st.info("💡 No hay solicitudes nuevas de prospectos en este momento.")
        else:
            # Creamos el diccionario para el selector
            # Usamos .get() para evitar errores si alguna columna falta
            opciones = {
                f"{l.get('banca', 'Sin Nombre')} ({l.get('representante', 'Sin Titular')})": l 
                for l in leads
            }
            
            seleccion = st.selectbox("🎯 Seleccione un Prospecto para gestionar:", options=opciones.keys())
            
            if seleccion:
                lead = opciones[seleccion]
                st.divider()
                
                col_info, col_planes = st.columns([1, 1.2])
                
                with col_info:
                    st.markdown("##### 📄 Datos del Expediente")
                    # Diseño de tarjeta para el lead
                    st.markdown(f"""
                        <div style='background: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;'>
                            <strong>Empresa:</strong> {lead.get('banca', 'N/A')}<br>
                            <strong>Titular:</strong> {lead.get('representante', 'N/A')}<br>
                            <strong>Puntos de Venta:</strong> {lead.get('puntos_venta', 0)}<br>
                            <strong>Teléfono:</strong> {lead.get('telefono', 'N/A')}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("") # Espaciador
                    if st.button("✅ Marcar como Procesado (Eliminar)", use_container_width=True):
                        supabase.table("suscriptores_leads").delete().eq("id", lead['id']).execute()
                        st.success("Lead procesado correctamente.")
                        st.rerun()

                with col_planes:
                    st.markdown("##### 💰 Cotizador Inteligente")
                    
                    # SELECTOR DINÁMICO DE TUS PLANES
                    nombres_planes = [p['nombre'] for p in planes_disponibles]
                    plan_sel = st.selectbox("Seleccionar Propuesta:", nombres_planes)
                    
                    # Buscar datos del plan seleccionado
                    datos_plan = next(item for item in planes_disponibles if item["nombre"] == plan_sel)
                    
                    # Cálculo seguro de total
                    try:
                        pts = int(lead.get('puntos_venta', 0))
                        costo_base = float(datos_plan.get('base', 0))
                        costo_punto = float(datos_plan.get('punto', 0))
                        total = costo_base + (pts * costo_punto)
                    except:
                        total = 0
                        st.error("Error en el formato de precios de los planes.")
                    
                    st.markdown(f"""
                        <div style='background: #f0f9ff; padding: 15px; border-radius: 10px; border-left: 5px solid #0369a1;'>
                            <small style='color: #0369a1;'>Propuesta Comercial</small><br>
                            <strong style='font-size: 18px;'>{plan_sel}</strong><br>
                            <h2 style='margin: 10px 0; color: #0369a1;'>${total:,.2f} USD</h2>
                            <small>Base: ${costo_base} + ({pts} pts x ${costo_punto})</small>
                        </div>
                    """, unsafe_allow_html=True)

                    # --- WHATSAPP OPTIMIZADO ---
                    tel_raw = str(lead.get('telefono', ''))
                    tel_clean = "".join(filter(str.isdigit, tel_raw))
                    
                    # Mensaje con mejor formato
                    msg_base = (
                        f"Hola *{lead.get('representante', '')}*! 👋\n\n"
                        f"Soy de *Control Maestro*. Recibimos tu solicitud para *{lead.get('banca', '')}*.\n\n"
                        f"Basado en tus {pts} puntos, esta es nuestra propuesta:\n"
                        f"🏆 *Plan: {plan_sel}*\n"
                        f"💰 *Inversión Total: ${total:,.2f} USD*\n\n"
                        f"¿Te gustaría que agendemos la activación? 😊"
                    )
                    
                    import urllib.parse
                    msg_url = urllib.parse.quote(msg_base)
                    
                    st.write("")
                    st.link_button("🟢 ENVIAR COTIZACIÓN POR WHATSAPP", 
                                  f"https://wa.me/{tel_clean}?text={msg_url}", 
                                  use_container_width=True)

    except Exception as e:
        st.error(f"🚨 Error al cargar Leads: {e}")
  

# --- EN TU BLOQUE PRINCIPAL (Tabs) ---
# tab1, tab2, tab3 = st.tabs(["👥 Clientes", "🚀 Solicitudes", "⚙️ Config. Planes"])
# with tab1: ...
# with tab2: seccion_solicitudes()
# with tab3: seccion_planes()
            
def check_password():
    """Verifica credenciales contra la tabla admin_users en Supabase."""
    def login_form():
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 25px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;'>
                    <h2 style='color: #1e3a8a; margin-bottom: 5px;'>🛡️ Acceso Multi-Usuario</h2>
                    <p style='color: #64748b; font-size: 14px;'>Identifíquese para entrar al Control Maestro</p>
                </div>
            """, unsafe_allow_html=True)
            
            user_in = st.text_input("Usuario", key="input_user")
            pass_in = st.text_input("Contraseña", type="password", key="input_pass")
            
            if st.button("INICIAR SESIÓN", use_container_width=True, type="primary"):
                # CONSULTA A SUPABASE
                try:
                    res = supabase.table("admin_users").select("*").eq("usuario", user_in).eq("password_text", pass_in).execute()
                    
                    if res.data and len(res.data) > 0:
                        st.session_state["password_correct"] = True
                        st.session_state["admin_name"] = res.data[0]['nombre']
                        st.success(f"✅ Bienvenido, {res.data[0]['nombre']}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    if "password_correct" not in st.session_state:
        login_form()
        return False
    return True
    
# =============================================================
# 5. LÓGICA PRINCIPAL (RESPONSIVA + MULTI-USUARIO + HEADER)
# =============================================================

if check_password():
    # Inyectar CSS Responsivo Pro y ocultar Sidebar
    st.markdown("""
        <style>
        /* Ocultar sidebar por completo */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
        
        /* Ajustar contenedor principal */
        .block-container { padding-top: 1rem !important; max-width: 95% !important; }

        /* Ajustes para móviles */
        @media (max-width: 640px) {
            .main-title { font-size: 18px !important; }
            [data-testid="column"] { 
                width: 100% !important; 
                flex: 1 1 100% !important; 
                margin-bottom: 0.5rem !important; 
            }
            .stButton button { height: 45px !important; }
        }
        </style>
    """, unsafe_allow_html=True)

    # --- HEADER DINÁMICO (Nombre de Usuario + Botón Salir) ---
    col_t, col_l = st.columns([4, 1])
    
    with col_t:
        # Obtenemos el nombre del administrador que inició sesión
        nombre_admin = st.session_state.get("admin_name", "Administrador")
        st.markdown(f"<h1 class='main-title' style='margin:0;'>💎 {nombre_admin}</h1>", unsafe_allow_html=True)
    
    with col_l:
        # Botón de salida único en el header
        if st.button("🚪 Salir", use_container_width=True):
            if "password_correct" in st.session_state:
                del st.session_state["password_correct"]
            st.rerun()

    st.write("---")

    # --- CONTENIDO DEL DASHBOARD ---
    try:
        # 1. Cargar datos de clientes desde Supabase
        res_p = supabase.table("perfiles").select("*").execute()
        df_clientes = pd.DataFrame(res_p.data)

        # 2. Mostrar métricas (Asegúrate de tener definida esta función)
        mostrar_metricas(df_clientes)
        
        # 3. Tabs con nombres cortos para mejor visualización en móvil
        tab1, tab2, tab3 = st.tabs(["👥 Clientes", "🚀 Leads", "⚙️ Planes"])

        with tab1:
            st.markdown("#### 📋 Suscriptores")
            # Tabla optimizada con scroll horizontal automático
            st.dataframe(
                df_clientes[["email", "nombre_banca", "status", "fecha_vencimiento"]], 
                use_container_width=True,
                height=300
            )

            with st.expander("✏️ Editar Licencia", expanded=True):
                # Buscador de cliente
                emails_list = df_clientes["email"].tolist()
                cliente_sel = st.selectbox("Buscar por Email:", emails_list)
                datos_cliente = df_clientes[df_clientes["email"] == cliente_sel].iloc[0]

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Banca:** {datos_cliente['nombre_banca']}")
                    nuevo_status = st.segmented_control(
                        "Estatus:", 
                        ["activo", "suspendido", "vencido"], 
                        default=datos_cliente['status']
                    )
                with col_b:
                    # Lógica de fecha de vencimiento
                    fecha_orig = datetime.strptime(datos_cliente['fecha_vencimiento'], '%Y-%m-%d')
                    opcion_t = st.selectbox("Extender suscripción:", ["No cambiar", "1 Mes", "3 Meses", "6 Meses", "1 Año"])
                    
                    nueva_f = fecha_orig
                    if opcion_t == "1 Mes": nueva_f += timedelta(days=30)
                    elif opcion_t == "3 Meses": nueva_f += timedelta(days=90)
                    elif opcion_t == "6 Meses": nueva_f += timedelta(days=180)
                    elif opcion_t == "1 Año": nueva_f += timedelta(days=365)
                    
                    st.info(f"Vencimiento: **{nueva_f.strftime('%Y-%m-%d')}**")

                if st.button("💾 GUARDAR CAMBIOS", type="primary", use_container_width=True):
                    with st.spinner("Sincronizando..."):
                        supabase.table("perfiles").update({
                            "status": nuevo_status,
                            "fecha_vencimiento": nueva_f.strftime('%Y-%m-%d')
                        }).eq("email", cliente_sel).execute()
                        st.success(f"✅ ¡Licencia de {datos_cliente['nombre_banca']} actualizada!")
                        time.sleep(1)
                        st.rerun()

        with tab2:
            # Llamada a la sección de Leads (Asegúrate de tener definida seccion_solicitudes)
            seccion_solicitudes()

        with tab3:
            # Llamada a la sección de configuración de planes
            seccion_planes()

    except Exception as e:
        st.error(f"🚨 Error de datos: {e}")
