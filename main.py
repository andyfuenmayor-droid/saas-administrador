import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import time
import urllib.parse

# =============================================================
# 1. CONFIGURACIÓN DE PÁGINA (ESTILO SAAS + IMAGEN 1)
# =============================================================
st.set_page_config(
    page_title="ME - Control Maestro", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS - IDENTIDAD VISUAL PREMIUM GLASSMORPHISM
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #f8fafc !important;
    }
    input, button, select, textarea {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .main-title, .brand-logo, h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        color: #ffffff !important;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(15, 23, 42, 0.5) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Fondo Degradado Glassmorphism Oscuro */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(at 0% 0%, rgba(30, 41, 59, 0.9) 0, transparent 50%),
                    radial-gradient(at 50% 0%, rgba(2, 171, 33, 0.12) 0, transparent 50%),
                    radial-gradient(at 100% 0%, rgba(3, 105, 161, 0.18) 0, transparent 50%),
                    radial-gradient(at 50% 100%, rgba(15, 23, 42, 1) 0, transparent 100%),
                    linear-gradient(135deg, rgba(15, 23, 42, 1) 0%, rgba(8, 15, 30, 1) 100%) !important;
        background-size: cover !important;
        min-height: 100vh !important;
    }
    
    /* Control de Sidebar colapsable */
    [data-testid="stSidebarCollapsedControl"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    /* Tarjetas Glassmorphism y Expanders */
    .odoo-card, .smart-button, .smart-metric, .odoo-metric-container, div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25) !important;
        color: #ffffff !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 15px !important;
    }
    
    .odoo-card:hover, .smart-button:hover, .smart-metric:hover, .odoo-metric-container:hover, div[data-testid="stExpander"]:hover {
        transform: translateY(-2px) !important;
        background: rgba(255, 255, 255, 0.07) !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.35) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    
    div[data-testid="stExpander"] details summary p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Formularios y bloques verticales */
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorder"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 14px !important;
        padding: 15px !important;
    }
    
    /* Métricas Streamlit */
    .stMetric {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
        min-height: 120px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    .stMetric:hover {
        transform: translateY(-1px) !important;
        background: rgba(255, 255, 255, 0.06) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 26px !important;
    }
    .stMetric [data-testid="stMetricLabel"] p {
        color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    
    /* Tablas y DataFrames */
    [data-testid="stDataFrame"] {
        background-color: rgba(15, 23, 42, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 5px !important;
    }
    
    /* Entradas de formulario y etiquetas */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label, .stDateInput > label, .stTextArea > label, .stMultiSelect > label {
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > div, .stDateInput > div > div > input, .stTextArea > div > div > textarea, .stMultiSelect > div > div > div {
        background-color: rgba(255, 255, 255, 0.04) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus, .stSelectbox > div > div > div:focus, .stDateInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: rgba(2, 171, 33, 0.6) !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 0 0 3px rgba(2, 171, 33, 0.15) !important;
    }
    
    /* Pestañas (Tabs) estilo cápsula */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 14px !important;
        padding: 6px !important;
        gap: 6px !important;
        border-bottom: none !important;
        margin-bottom: 20px !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px !important;
        background-color: transparent !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        padding: 0px 20px !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: rgba(255, 255, 255, 0.65) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    .stTabs [data-baseweb="tab"]:hover p {
        color: #ffffff !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(2, 171, 33, 0.15) !important;
        border: 1px solid rgba(2, 171, 33, 0.35) !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-highlight-bar"] {
        display: none !important;
    }
    
    /* Botones primarios y secundarios */
    button[kind="primary"], button[kind="secondary"] {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"] {
        background-color: #02ab21 !important;
        color: white !important;
        border: 1px solid rgba(2, 171, 33, 0.4) !important;
    }
    button[kind="primary"]:hover {
        background-color: #02941c !important;
        box-shadow: 0 4px 15px rgba(2, 171, 33, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Ajustes de espaciado */
    .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

# 2. CONEXIÓN A SUPABASE (MODO ADMIN SEGURO)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets.get("SUPABASE_SERVICE_KEY", st.secrets["SUPABASE_KEY"])
    return create_client(url, key)

supabase = init_connection()

# =============================================================
# Helper: Enviar Correo con Credenciales (SMTP)
# =============================================================
def enviar_correo_credenciales(email_dest, banca, representante, usuario, password):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    server_host = st.secrets.get("SMTP_SERVER")
    port = st.secrets.get("SMTP_PORT")
    user = st.secrets.get("SMTP_USER")
    password_smtp = st.secrets.get("SMTP_PASSWORD")
    sender = st.secrets.get("SMTP_FROM", user)
    
    if not (server_host and port and user and password_smtp):
        return False, "SMTP no configurado en secrets.toml"
        
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = email_dest
        msg['Subject'] = f"Credenciales de acceso - {banca}"
        
        body = f"""Hola {representante},

Tu SaaS para {banca} ha sido activado con éxito en Multibanca Express.

Aquí tienes tus credenciales de acceso al sistema:
Usuario/Email: {usuario}
Contraseña: {password}

¡Bienvenido al sistema!"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        port_num = int(port)
        if port_num == 465:
            server = smtplib.SMTP_SSL(server_host, port_num, timeout=10)
        else:
            server = smtplib.SMTP(server_host, port_num, timeout=10)
            server.starttls()
            
        server.login(user, password_smtp)
        server.sendmail(sender, email_dest, msg.as_string())
        server.quit()
        return True, "Correo enviado con éxito"
    except Exception as e:
        return False, f"Error al enviar correo: {str(e)}"

# =============================================================
# 3. SEGURIDAD DE ACCESO (LÓGICA COMPLETA DE RECUPERACIÓN)
# =============================================================
def check_password():
    """Verifica credenciales contra la tabla usuarios en Supabase."""
    
    def login_form():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.2, 2, 1.2])
        with col2:
            with st.form("login_form_secure", clear_on_submit=False):
                st.markdown("""
                    <div style='text-align: center; padding: 15px 0 25px 0;'>
                        <h1 style='font-size: 24px; margin-bottom: 8px; color: #ffffff;'>🛡️ Acceso Multi-Usuario</h1>
                        <p style='color: rgba(255,255,255,0.6); font-size: 14px; margin: 0;'>Identifíquese para entrar al Control Maestro</p>
                    </div>
                """, unsafe_allow_html=True)
                
                user_in = st.text_input("Usuario", key="input_user").strip()
                pass_in = st.text_input("Contraseña", type="password", key="input_pass").strip()
                
                st.write("")
                submit_login = st.form_submit_button("INICIAR SESIÓN", use_container_width=True, type="primary")
                
                if submit_login:
                    try:
                        res = supabase.table("usuarios").select("*").eq("Usuario", user_in).eq("Clave", pass_in).execute()
                        
                        if res.data and len(res.data) > 0:
                            st.session_state["password_correct"] = True
                            st.session_state["admin_name"] = res.data[0].get('nombre', user_in)
                            st.session_state["user_id_logged"] = res.data[0].get('id')
                            st.success(f"✅ Bienvenido")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos")
                    except Exception as e:
                        print(f"Error de conexión en login: {e}")
                        st.error("❌ Ocurrió un error de conexión al validar tus credenciales.")

    if "password_correct" not in st.session_state:
        login_form()
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
    try:
        res = supabase.table("config_planes").select("*").order("costo_base").execute()
        planes_db = res.data
        with st.expander("➕ Crear Nuevo Plan", expanded=False):
            col1, col2, col3 = st.columns(3)
            nombre = col1.text_input("Nombre del Nuevo Plan")
            base = col2.number_input("Costo Base (USD)", min_value=0.0, step=10.0, key="new_base")
            punto = col3.number_input("Costo por Punto (USD)", min_value=0.0, step=1.0, key="new_punto")
            desc = st.text_area("Descripción del servicio", key="new_desc")
            if st.button("💾 Crear Plan", use_container_width=True):
                if nombre:
                    if any(p['nombre'] == nombre for p in planes_db):
                        st.error(f"Ya existe el plan '{nombre}'. Usa la opción de editar abajo.")
                    else:
                        data_plan = {"nombre": nombre, "costo_base": base, "costo_por_punto": punto, "descripcion": desc}
                        supabase.table("config_planes").insert(data_plan).execute()
                        st.success(f"¡Plan '{nombre}' creado!")
                        time.sleep(1); st.rerun()
                else:
                    st.error("El nombre del plan es obligatorio.")

        if planes_db:
            st.markdown("#### Planes Activos en Sistema")
            df_p = pd.DataFrame(planes_db)[["nombre", "costo_base", "costo_por_punto", "descripcion"]]
            st.dataframe(df_p, use_container_width=True)
            
            col_edit, col_del = st.columns(2)
            with col_edit:
                with st.expander("✏️ Editar Plan", expanded=True):
                    plan_a_editar = st.selectbox("Seleccione plan a editar:", [p['nombre'] for p in planes_db], key="sel_edit")
                    if plan_a_editar:
                        plan_data = next(p for p in planes_db if p["nombre"] == plan_a_editar)
                        nuevo_base = st.number_input("Costo Base (USD)", min_value=0.0, step=10.0, value=float(plan_data['costo_base']), key="edit_base")
                        nuevo_punto = st.number_input("Costo por Punto (USD)", min_value=0.0, step=1.0, value=float(plan_data['costo_por_punto']), key="edit_punto")
                        nueva_desc = st.text_area("Descripción", value=plan_data.get('descripcion', ''), key="edit_desc")
                        if st.button(f"💾 Guardar Cambios", use_container_width=True, type="primary"):
                            data_update = {"costo_base": nuevo_base, "costo_por_punto": nuevo_punto, "descripcion": nueva_desc}
                            supabase.table("config_planes").update(data_update).eq("nombre", plan_a_editar).execute()
                            st.success(f"Plan {plan_a_editar} actualizado.")
                            time.sleep(1); st.rerun()
                            
            with col_del:
                with st.expander("🗑️ Zona de Peligro", expanded=True):
                    plan_a_borrar = st.selectbox("Seleccione plan a eliminar:", [p['nombre'] for p in planes_db], key="sel_del")
                    if st.button(f"Eliminar {plan_a_borrar}"):
                        supabase.table("config_planes").delete().eq("nombre", plan_a_borrar).execute()
                        st.error(f"Plan {plan_a_borrar} eliminado.")
                        time.sleep(1); st.rerun()
    except Exception as e:
        print(f"Error al conectar con la tabla config_planes: {e}")
        st.error("Error al cargar la configuración de planes de la base de datos.")

def seccion_solicitudes():
    st.markdown("### 🚀 Gestión Estratégica de Leads")
    try:
        res_planes = supabase.table("config_planes").select("*").execute()
        planes_disponibles = res_planes.data
        if not planes_disponibles:
            st.warning("⚠️ Configura los planes primero en la pestaña correspondiente.")
            return

        res_leads = supabase.table("suscriptores_leads").select("*").execute()
        leads = res_leads.data
        if not leads:
            st.info("💡 No hay solicitudes nuevas en este momento.")
        else:
            opciones = {f"ID: {l.get('id')} | {l.get('banca', 'N/A')} ({l.get('representante', 'N/A')})": l for l in leads}
            seleccion = st.selectbox("🎯 Seleccione un Prospecto para gestionar:", options=opciones.keys())
            if seleccion:
                lead = opciones[seleccion]
                lead_id = lead.get('id')
                st.divider()
                col_info, col_planes = st.columns([1, 1])
                with col_info:
                    st.markdown("##### 📄 Datos del Expediente")
                    st.markdown(f"""
                    <div class='odoo-card' style='padding: 22px; border-top: 4px solid #3b82f6;'>
                        <h4 style='margin: 0 0 15px 0; color: #3b82f6;'>💼 {lead.get('banca')}</h4>
                        <table style='width: 100%; border-collapse: collapse;'>
                            <tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>
                                <td style='padding: 8px 0; color: gray; font-size: 13px; width: 35%;'>👤 Representante</td>
                                <td style='padding: 8px 0; font-weight: 500; font-size: 13px;'>{lead.get('representante')}</td>
                            </tr>
                            <tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>
                                <td style='padding: 8px 0; color: gray; font-size: 13px;'>📧 Correo</td>
                                <td style='padding: 8px 0; font-size: 13px;'>{lead.get('email', 'N/A')}</td>
                            </tr>
                            <tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>
                                <td style='padding: 8px 0; color: gray; font-size: 13px;'>📞 WhatsApp</td>
                                <td style='padding: 8px 0; font-size: 13px;'>{lead.get('telefono', 'N/A')}</td>
                            </tr>
                            <tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>
                                <td style='padding: 8px 0; color: gray; font-size: 13px;'>📊 Puntos</td>
                                <td style='padding: 8px 0; font-weight: bold; color: #3b82f6; font-size: 13px;'>{lead.get('puntos_venta')}</td>
                            </tr>
                            <tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>
                                <td style='padding: 8px 0; color: gray; font-size: 13px;'>📍 Ubicación</td>
                                <td style='padding: 8px 0; font-size: 13px;'>{lead.get('estado', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style='padding: 8px 0; color: gray; font-size: 13px;'>🏠 Dirección</td>
                                <td style='padding: 8px 0; font-size: 13px;'>{lead.get('direccion', 'N/A')}</td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                with col_planes:
                    st.markdown("##### 💰 Cotizador Dinámico")
                    plan_sel = st.selectbox("Plan a Cotizar:", [p['nombre'] for p in planes_disponibles])
                    descuento = st.number_input("💸 Aplicar Descuento (USD):", min_value=0.0, step=5.0, value=0.0)
                    metodos_pago = st.multiselect("💳 Métodos de Pago a ofrecer:", ["Zelle", "PayPal", "Binance (USDT)", "Pago Móvil", "Transferencia ACH", "Efectivo"], default=["Zelle", "Binance (USDT)"])
                    
                    datos_plan = next(p for p in planes_disponibles if p["nombre"] == plan_sel)
                    pts = int(lead.get('puntos_venta', 0))
                    total_final = max(0.0, (float(datos_plan['costo_base']) + (pts * float(datos_plan['costo_por_punto']))) - descuento)
                    st.markdown(f"<div class='odoo-card' style='padding: 20px; border-left: 5px solid #02ab21 !important; background: linear-gradient(135deg, rgba(2, 171, 33, 0.1) 0%, rgba(2, 171, 33, 0.02) 100%) !important;'><strong style='font-size: 16px; color: #ffffff;'>Propuesta: {plan_sel}</strong><h2 style='margin: 5px 0; color: #02ab21;'>${total_final:,.2f} USD</h2></div>", unsafe_allow_html=True)
                    
                    tel_raw = str(lead.get('telefono', ''))
                    tel_clean = "".join(filter(str.isdigit, tel_raw))
                    lista_pagos = "\n".join([f"🔹 {mp}" for mp in metodos_pago])
                    msg = f"Hola *{lead.get('representante')}*! 👋\n\nSoy el admin de *Multibanca Express*. Recibimos tu solicitud para *{lead.get('banca')}*.\n\n🏆 *PLAN: {plan_sel.upper()}*\n💰 *INVERSIÓN FINAL: ${total_final:,.2f} USD*\n\n💳 *MÉTODOS DE PAGO:* \n{lista_pagos}\n\n¿Agendamos hoy? 😊"
                    st.link_button("🟢 ENVIAR PROPUESTA POR WHATSAPP", f"https://wa.me/{tel_clean}?text={urllib.parse.quote(msg)}", use_container_width=True)
                    
                    if st.button("🚀 Mover a Seguimiento (Cotizado)", key=f"move_{lead_id}", use_container_width=True, type="primary"):
                        with st.spinner("Moviendo..."):
                            # Guardamos todos los datos de forma estructurada en la tabla leads_seguimiento
                            data_seg = {
                                "banca": lead.get('banca'),
                                "representante": lead.get('representante'),
                                "email": lead.get('email'),
                                "telefono": lead.get('telefono'),
                                "puntos_venta": pts,
                                "plan_cotizado": plan_sel,
                                "total_cotizado": total_final,
                                "estado_seguimiento": "esperando_pago",
                                "estado": lead.get('estado'),
                                "direccion": lead.get('direccion')
                            }
                            supabase.table("leads_seguimiento").insert(data_seg).execute()
                            supabase.table("suscriptores_leads").delete().eq("id", lead_id).execute()
                            st.success(f"✅ Movido a Seguimiento."); time.sleep(1); st.rerun()
    except Exception as e:
        print(f"Error en solicitudes: {e}")
        st.error("🚨 Ocurrió un error inesperado al gestionar los prospectos.")

def seccion_seguimiento():
    st.markdown("### ⏳ Prospectos en Espera de Activación")
    try:
        # Si se acaba de activar un SaaS, mostrar pantalla de confirmación con opciones de envío
        if "nuevo_saas_activado" in st.session_state:
            info = st.session_state["nuevo_saas_activado"]
            st.markdown(f"""
            <div class='odoo-card' style='padding: 22px; border-top: 4px solid #02ab21;'>
                <h3 style='margin: 0 0 10px 0; color: #02ab21;'>🎉 ¡SaaS '{info['banca']}' activado con éxito!</h3>
                <p style='color: rgba(255,255,255,0.85); font-size: 14px; margin: 0;'>Las credenciales para el cliente han sido creadas e inicializadas.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### 📝 Credenciales Generadas")
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"**Usuario/Email:** `{info['email']}`")
            with col_info2:
                st.info(f"**Contraseña:** `{info['password']}`")
                
            st.markdown("##### 📧 Estado de Envío por Correo")
            if info.get("email_auto_sent"):
                st.success(f"✅ Correo enviado automáticamente a **{info['email']}**.")
            else:
                st.warning(f"⚠️ Correo automático no enviado: {info.get('email_error_detail', 'SMTP no configurado en secrets.toml')}")
                
            st.markdown("##### 🟢 Compartir Credenciales")
            
            # Preparar mensajes
            msg_wa = f"¡Hola {info['representante']}! 👋\n\nTu SaaS para *{info['banca']}* ha sido activado con éxito en Multibanca Express. 🚀\n\nAquí tienes tus credenciales de acceso:\n📧 *Usuario/Email:* {info['email']}\n🔑 *Contraseña:* {info['password']}\n\n¡Bienvenido!"
            msg_mail = f"Hola {info['representante']},\n\nTu SaaS para {info['banca']} ha sido activado con éxito en Multibanca Express.\n\nAquí tienes tus credenciales de acceso al sistema:\nUsuario/Email: {info['email']}\nContraseña: {info['password']}\n\n¡Bienvenido al sistema!"
            
            col_sh1, col_sh2, col_sh3 = st.columns(3)
            with col_sh1:
                tel_clean = "".join(filter(str.isdigit, str(info.get('telefono', ''))))
                wa_url = f"https://wa.me/{tel_clean}?text={urllib.parse.quote(msg_wa)}" if tel_clean else f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                st.link_button("🟢 Enviar por WhatsApp", wa_url, use_container_width=True)
            with col_sh2:
                subject_text = f"Credenciales de acceso - {info['banca']}"
                mail_url = f"mailto:{info['email']}?subject={urllib.parse.quote(subject_text)}&body={urllib.parse.quote(msg_mail)}"
                st.link_button("📧 Enviar por Correo (Manual)", mail_url, use_container_width=True)
            with col_sh3:
                if st.button("🏠 Volver a la Lista", use_container_width=True, type="primary"):
                    del st.session_state["nuevo_saas_activado"]
                    st.rerun()
            return

        res = supabase.table("leads_seguimiento").select("*").eq("estado_seguimiento", "esperando_pago").execute()
        seguimiento = res.data
        if not seguimiento:
            st.info("💡 No hay clientes pendientes de pago.")
        else:
            # Mostramos un DataFrame limpio y legible
            datos_mostrar = []
            for s in seguimiento:
                repr_val = s.get('representante', '')
                if " | " in repr_val:
                    real_repr = repr_val.split(" | ")[0]
                    email_val = repr_val.split(" | ")[1]
                else:
                    real_repr = repr_val
                    email_val = s.get('email', 'N/A') or 'N/A'
                
                datos_mostrar.append({
                    "Banca": s.get('banca'),
                    "Representante": real_repr,
                    "Email": email_val,
                    "Plan Cotizado": s.get('plan_cotizado'),
                    "Total Cotizado": s.get('total_cotizado'),
                    "WhatsApp": s.get('telefono'),
                    "Ubicación": s.get('estado', 'N/A'),
                    "Dirección": s.get('direccion', 'N/A')
                })
            df_mostrar = pd.DataFrame(datos_mostrar)
            st.dataframe(df_mostrar, use_container_width=True)
            
            # Selectbox para gestionar
            opciones = {}
            for s in seguimiento:
                repr_val = s.get('representante', '')
                real_repr = repr_val.split(" | ")[0] if " | " in repr_val else repr_val
                opciones[f"{s['banca']} - {real_repr}"] = s
                
            cliente_seg = st.selectbox("🎯 Seleccione un Prospecto para activar:", options=opciones.keys())
            
            if cliente_seg:
                lead_sel = opciones[cliente_seg]
                repr_val = lead_sel.get('representante', '')
                if " | " in repr_val:
                    real_repr = repr_val.split(" | ")[0]
                    email_val = repr_val.split(" | ")[1]
                else:
                    real_repr = repr_val
                    email_val = lead_sel.get('email') or ""
                
                st.divider()
                st.markdown("##### ⚙️ Configuración de Acceso para el Nuevo Suscriptor")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    email_input = st.text_input("📧 Correo de Acceso:", value=email_val, key="acc_email")
                with col_c2:
                    # Generamos una contraseña por defecto basada en el WhatsApp
                    default_pass = f"ME{str(lead_sel.get('telefono', ''))[-6:]}" if lead_sel.get('telefono') else "ME2026!"
                    pass_input = st.text_input("🔑 Contraseña Temporal:", value=default_pass, key="acc_pass")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ DAR DE ALTA (CREAR Y ACTIVAR)", use_container_width=True, type="primary"):
                        if not email_input.strip() or not pass_input.strip():
                            st.warning("⚠️ El correo y la contraseña son obligatorios.")
                        else:
                            with st.spinner("⏳ Creando credenciales e inicializando perfil..."):
                                try:
                                    # 1. Crear usuario en auth.users de Supabase
                                    from supabase import create_client
                                    temp_client = create_client(
                                        st.secrets["SUPABASE_URL"], 
                                        st.secrets.get("SUPABASE_SERVICE_KEY", st.secrets["SUPABASE_KEY"])
                                    )
                                    auth_res = temp_client.auth.sign_up({
                                        "email": email_input.strip(),
                                        "password": pass_input.strip()
                                    })
                                    
                                    if auth_res.user:
                                        u_id = auth_res.user.id
                                        
                                        # Guardar el teléfono en el usuario auth usando el admin api para seguridad
                                        telefono_val = lead_sel.get('telefono', '')
                                        if telefono_val:
                                            try:
                                                temp_client.auth.admin.update_user_by_id(u_id, {
                                                    "phone": telefono_val.strip(),
                                                    "user_metadata": {
                                                        "telefono": telefono_val.strip()
                                                    }
                                                })
                                            except Exception as ex:
                                                print(f"Error guardando telefono en auth: {ex}")
                                                
                                        # 2. Insertar perfil del suscriptor con todos los datos
                                        fecha_ini = datetime.now().isoformat()
                                        fecha_venc = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
                                        profile_data = {
                                            "id": u_id,
                                            "email": email_input.strip(),
                                            "nombre_banca": lead_sel.get('banca'),
                                            "plan": lead_sel.get('plan_cotizado'),
                                            "status": "activo",
                                            "fecha_inicio": fecha_ini,
                                            "fecha_vencimiento": fecha_venc,
                                            "role": "admin",
                                            "rol": "contador",
                                            "limite_agencias": int(lead_sel.get('puntos_venta', 5)),
                                            "representante": real_repr,
                                            "telefono": lead_sel.get('telefono'),
                                            "direccion": lead_sel.get('direccion'),
                                            "estado": lead_sel.get('estado')  # Guardamos la ubicación geográfica (estado) aquí
                                        }
                                        supabase.table("perfiles").insert(profile_data).execute()
                                        
                                        # 3. Eliminar de la lista de seguimiento
                                        supabase.table("leads_seguimiento").delete().eq("id", lead_sel.get('id')).execute()
                                        
                                        # 4. Intentar enviar correo automático por SMTP
                                        email_sent, email_err = enviar_correo_credenciales(
                                            email_dest=email_input.strip(),
                                            banca=lead_sel.get('banca'),
                                            representante=real_repr,
                                            usuario=email_input.strip(),
                                            password=pass_input.strip()
                                        )
                                        
                                        # 5. Guardar en session state y hacer Rerun
                                        st.session_state["nuevo_saas_activado"] = {
                                            "banca": lead_sel.get('banca'),
                                            "representante": real_repr,
                                            "email": email_input.strip(),
                                            "password": pass_input.strip(),
                                            "telefono": lead_sel.get('telefono', ''),
                                            "email_auto_sent": email_sent,
                                            "email_error_detail": email_err
                                        }
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error("❌ No se pudo crear el usuario en Supabase Auth.")
                                except Exception as e:
                                    print(f"Error en alta/activación: {e}")
                                    st.error("🚨 Ocurrió un error inesperado al dar de alta el suscriptor.")
                                    
                with col2:
                    if st.button("❌ Cancelar Solicitud / Eliminar Lead", use_container_width=True):
                        with st.spinner("Eliminando..."):
                            supabase.table("leads_seguimiento").delete().eq("id", lead_sel.get('id')).execute()
                            st.error("Solicitud eliminada.")
                            time.sleep(1)
                            st.rerun()
    except Exception as e:
        print(f"Error en seccion_seguimiento: {e}")
        st.error("Ocurrió un error inesperado al cargar la lista de seguimiento.")


# =============================================================
# 5. LÓGICA PRINCIPAL (FULL WIDTH + MULTI-USUARIO + 4 TABS)
# =============================================================

if check_password():
    st.markdown("<style>[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    col_t, col_l = st.columns([4, 1])
    with col_t:
        nombre_admin = st.session_state.get("admin_name", "Administrador")
        st.markdown(f"<h1 style='margin:0;'>💎 {nombre_admin}</h1>", unsafe_allow_html=True)
    with col_l:
        if st.button("🚪 Salir", use_container_width=True):
            if "password_correct" in st.session_state:
                del st.session_state["password_correct"]
            st.rerun()

    st.write("---")

    try:
        res_p = supabase.table("perfiles").select("*").execute()
        df_clientes = pd.DataFrame(res_p.data)
        mostrar_metricas(df_clientes)
        
        tab1, tab2, tab3, tab4 = st.tabs(["👥 Clientes", "🚀 Solicitudes", "⏳ Seguimiento", "⚙️ Planes"])

        with tab1:
            st.markdown("#### 📋 Gestión de Clientes Activos")
            
            # Formateamos las columnas para mostrar en el dataframe si existen
            columnas_mostrar = ["email", "nombre_banca", "representante", "telefono", "estado", "direccion", "status", "fecha_vencimiento"]
            cols_validas = [c for c in columnas_mostrar if c in df_clientes.columns]
            
            column_names_map = {
                "email": "Email",
                "nombre_banca": "Banca/Negocio",
                "representante": "Representante",
                "telefono": "WhatsApp/Teléfono",
                "estado": "Ubicación (Estado)",
                "direccion": "Dirección",
                "status": "Estatus Licencia",
                "fecha_vencimiento": "Fecha Vencimiento"
            }
            
            df_mostrar_clientes = df_clientes[cols_validas].rename(columns=column_names_map)
            st.dataframe(df_mostrar_clientes, use_container_width=True, height=300)
            with st.expander("✏️ Editar Licencia", expanded=True):
                emails_list = df_clientes["email"].tolist()
                cliente_sel = st.selectbox("Buscar por Email:", emails_list)
                datos_cliente = df_clientes[df_clientes["email"] == cliente_sel].iloc[0]
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Banca:** {datos_cliente['nombre_banca']}")
                    nuevo_status = st.segmented_control("Estatus:", ["activo", "suspendido", "vencido"], default=datos_cliente['status'])
                with col_b:
                    fecha_orig = datetime.strptime(datos_cliente['fecha_vencimiento'], '%Y-%m-%d')
                    opcion_t = st.selectbox("Extender suscripción:", ["No cambiar", "1 Mes", "3 Meses", "6 Meses", "1 Año"])
                    nueva_f = fecha_orig
                    if opcion_t == "1 Mes": nueva_f += timedelta(days=30)
                    elif opcion_t == "3 Meses": nueva_f += timedelta(days=90)
                    elif opcion_t == "6 Meses": nueva_f += timedelta(days=180)
                    elif opcion_t == "1 Año": nueva_f += timedelta(days=365)
                    st.info(f"Vencimiento: **{nueva_f.strftime('%Y-%m-%d')}**")
                if st.button("💾 GUARDAR CAMBIOS", type="primary", use_container_width=True):
                    supabase.table("perfiles").update({"status": nuevo_status, "fecha_vencimiento": nueva_f.strftime('%Y-%m-%d')}).eq("email", cliente_sel).execute()
                    st.success("✅ Licencia actualizada"); time.sleep(1); st.rerun()

                st.markdown("---")
                st.markdown("##### 🔑 Cambiar Contraseña")
                
                # Mostrar mensaje de éxito si se cambió la clave con opción de WhatsApp
                if "cambio_clave_exito" in st.session_state:
                    cc = st.session_state["cambio_clave_exito"]
                    st.markdown(f"""
                    <div class='odoo-card' style='padding: 15px; border-left: 5px solid #02ab21;'>
                        <h5 style='margin:0; color: #02ab21;'>🔑 Contraseña Actualizada para {cc['banca']}</h5>
                        <p style='margin:5px 0 10px 0; font-size:13px;'>La clave de <b>{cc['email']}</b> ha sido actualizada a: <code>{cc['password']}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Preparar mensaje de WhatsApp
                    msg_wa = f"¡Hola! 👋\n\nSe ha actualizado tu contraseña de acceso para *{cc['banca']}*.\n\n📧 *Usuario/Email:* {cc['email']}\n🔑 *Nueva Contraseña:* {cc['password']}\n\n¡Gracias!"
                    
                    col_sh1, col_sh2 = st.columns(2)
                    with col_sh1:
                        tel_clean = "".join(filter(str.isdigit, str(cc.get('telefono', ''))))
                        wa_url = f"https://wa.me/{tel_clean}?text={urllib.parse.quote(msg_wa)}" if tel_clean else f"https://wa.me/?text={urllib.parse.quote(msg_wa)}"
                        st.link_button("🟢 Enviar por WhatsApp", wa_url, use_container_width=True)
                    with col_sh2:
                        if st.button("Cerrar Mensaje", use_container_width=True):
                            del st.session_state["cambio_clave_exito"]
                            st.rerun()
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    nueva_clave_input = st.text_input(
                        "Nueva Contraseña:", 
                        type="password",
                        key="new_pass_edit_field",
                        placeholder="Ingrese la nueva contraseña"
                    )
                with col_p2:
                    confirmar_clave_input = st.text_input(
                        "Confirmar Contraseña:", 
                        type="password",
                        key="new_pass_confirm_field",
                        placeholder="Repita la contraseña"
                    )
                
                if st.button("🔑 ACTUALIZAR CONTRASEÑA EN SISTEMA", type="secondary", use_container_width=True):
                    if not nueva_clave_input.strip():
                        st.error("❌ Por favor ingrese una contraseña válida.")
                    elif nueva_clave_input.strip() != confirmar_clave_input.strip():
                        st.error("❌ Las contraseñas no coinciden.")
                    else:
                        with st.spinner("⏳ Actualizando contraseña en Supabase Auth..."):
                            try:
                                # Buscar el teléfono para el envío
                                tel_dest = datos_cliente.get('telefono') or ""
                                if not tel_dest:
                                    try:
                                        user_auth_res = supabase.auth.admin.get_user_by_id(datos_cliente['id'])
                                        user_auth = user_auth_res.user
                                        tel_dest = user_auth.phone or (user_auth.user_metadata.get('telefono') if user_auth.user_metadata else '')
                                    except:
                                        pass
                                
                                supabase.auth.admin.update_user_by_id(datos_cliente['id'], {"password": nueva_clave_input.strip()})
                                
                                st.session_state["cambio_clave_exito"] = {
                                    "banca": datos_cliente['nombre_banca'],
                                    "email": datos_cliente['email'],
                                    "password": nueva_clave_input.strip(),
                                    "telefono": tel_dest
                                }
                                st.success("✅ Contraseña actualizada con éxito.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al cambiar contraseña: {e}")

        with tab2: seccion_solicitudes()
        with tab3: seccion_seguimiento()
        with tab4: seccion_planes()

    except Exception as e:
        print(f"Error general en dashboard: {e}")
        st.error("🚨 Ocurrió un error al cargar la información del panel.")
