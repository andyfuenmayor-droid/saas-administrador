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

# Estilos CSS - IDENTIDAD VISUAL "IMAGEN 1" (Limpio + Acento Rojo)
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    [data-testid="stHeader"] { background: #1e293b; }
    
    /* Tabs Estilo Imagen 1: Sin fondo, línea roja inferior */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent !important;
        border-radius: 0px !important; border: none !important;
        font-size: 16px; color: #1f77b4; font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #FF4B4B !important; 
        border-bottom: 2px solid #FF4B4B !important;
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
# 3. SEGURIDAD DE ACCESO (LÓGICA COMPLETA DE RECUPERACIÓN)
# =============================================================
def check_password():
    """Verifica credenciales contra la tabla admin_users en Supabase con opción de recuperación."""
    
    if "forgot_pass_mode" not in st.session_state:
        st.session_state["forgot_pass_mode"] = False

    def recovery_form():
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 25px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;'>
                    <h2 style='color: #714B67; margin-bottom: 5px;'>🔑 Restaurar Acceso</h2>
                    <p style='color: #64748b; font-size: 14px;'>Ingrese su usuario para actualizar la contraseña</p>
                </div>
            """, unsafe_allow_html=True)
            
            user_reset = st.text_input("Confirmar Usuario", key="reset_user")
            new_pass = st.text_input("Nueva Contraseña", type="password", key="new_pass")
            
            c1, c2 = st.columns(2)
            if c1.button("ACTUALIZAR", use_container_width=True, type="primary"):
                try:
                    check_user = supabase.table("admin_users").select("*").eq("usuario", user_reset).execute()
                    if check_user.data:
                        supabase.table("admin_users").update({"password_text": new_pass}).eq("usuario", user_reset).execute()
                        st.success("✅ Contraseña actualizada correctamente")
                        time.sleep(1.5)
                        st.session_state["forgot_pass_mode"] = False
                        st.rerun()
                    else:
                        st.error("❌ El usuario no existe en el sistema")
                except Exception as e:
                    st.error(f"Error al restaurar: {e}")
            
            if c2.button("CANCELAR", use_container_width=True):
                st.session_state["forgot_pass_mode"] = False
                st.rerun()

    def login_form():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 30px; background: white; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);'>
                    <h1 style='color: #1e293b; font-size: 24px;'>🛡️ Acceso Multi-Usuario</h1>
                    <p style='color: #64748b;'>Identifíquese para entrar al Control Maestro</p>
                </div>
            """, unsafe_allow_html=True)
            
            user_in = st.text_input("Usuario", key="input_user")
            pass_in = st.text_input("Contraseña", type="password", key="input_pass")
            
            if st.button("INICIAR SESIÓN", use_container_width=True, type="primary"):
                try:
                    res = supabase.table("admin_users").select("*").eq("usuario", user_in).eq("password_text", pass_in).execute()
                    if res.data and len(res.data) > 0:
                        st.session_state["password_correct"] = True
                        st.session_state["admin_name"] = res.data[0]['nombre']
                        st.session_state["user_id_logged"] = res.data[0]['id']
                        st.success(f"✅ Bienvenido, {res.data[0]['nombre']}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
            
            st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
            if st.button("¿Olvidaste tu contraseña?", type="secondary"):
                st.session_state["forgot_pass_mode"] = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if "password_correct" not in st.session_state:
        if st.session_state["forgot_pass_mode"]:
            recovery_form()
        else:
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
        with st.expander("➕ Crear o Editar Plan en la Nube", expanded=True):
            col1, col2, col3 = st.columns(3)
            nombre = col1.text_input("Nombre del Plan")
            base = col2.number_input("Costo Base (USD)", min_value=0.0, step=10.0)
            punto = col3.number_input("Costo por Punto (USD)", min_value=0.0, step=1.0)
            desc = st.text_area("Descripción del servicio")
            if st.button("💾 Guardar en Base de Datos", use_container_width=True):
                if nombre:
                    data_plan = {"nombre": nombre, "costo_base": base, "costo_por_punto": punto, "descripcion": desc}
                    supabase.table("config_planes").upsert(data_plan, on_conflict="nombre").execute()
                    st.success(f"¡Plan '{nombre}' sincronizado!")
                    time.sleep(1); st.rerun()
                else:
                    st.error("El nombre del plan es obligatorio.")

        if planes_db:
            st.markdown("#### Planes Activos en Sistema")
            df_p = pd.DataFrame(planes_db)[["nombre", "costo_base", "costo_por_punto", "descripcion"]]
            st.dataframe(df_p, use_container_width=True)
            with st.expander("🗑️ Zona de Peligro"):
                plan_a_borrar = st.selectbox("Seleccione plan a eliminar:", [p['nombre'] for p in planes_db])
                if st.button(f"Eliminar {plan_a_borrar}"):
                    supabase.table("config_planes").delete().eq("nombre", plan_a_borrar).execute()
                    st.error(f"Plan {plan_a_borrar} eliminado.")
                    time.sleep(1); st.rerun()
    except Exception as e:
        st.error(f"Error al conectar con la tabla config_planes: {e}")

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
                col_info, col_planes = st.columns([1, 1.2])
                with col_info:
                    st.markdown("##### 📄 Datos del Expediente")
                    st.markdown(f"<div style='background: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;'><strong>Empresa:</strong> {lead.get('banca')}<br><strong>Titular:</strong> {lead.get('representante')}<br><strong>Puntos:</strong> {lead.get('puntos_venta')}</div>", unsafe_allow_html=True)
                    descuento = st.number_input("💸 Aplicar Descuento (USD):", min_value=0.0, step=5.0, value=0.0)
                    metodos_pago = st.multiselect("💳 Métodos de Pago a ofrecer:", ["Zelle", "PayPal", "Binance (USDT)", "Pago Móvil", "Transferencia ACH", "Efectivo"], default=["Zelle", "Binance (USDT)"])
                with col_planes:
                    st.markdown("##### 💰 Cotizador Dinámico")
                    plan_sel = st.selectbox("Plan a Cotizar:", [p['nombre'] for p in planes_disponibles])
                    datos_plan = next(p for p in planes_disponibles if p["nombre"] == plan_sel)
                    pts = int(lead.get('puntos_venta', 0))
                    total_final = max(0.0, (float(datos_plan['costo_base']) + (pts * float(datos_plan['costo_por_punto']))) - descuento)
                    st.markdown(f"<div style='background: #f0f9ff; padding: 15px; border-radius: 10px; border-left: 5px solid #0369a1;'><strong style='font-size: 16px;'>Propuesta: {plan_sel}</strong><h2 style='margin: 5px 0; color: #0369a1;'>${total_final:,.2f} USD</h2></div>", unsafe_allow_html=True)
                    
                    tel_raw = str(lead.get('telefono', ''))
                    tel_clean = "".join(filter(str.isdigit, tel_raw))
                    lista_pagos = "\n".join([f"🔹 {mp}" for mp in metodos_pago])
                    msg = f"Hola *{lead.get('representante')}*! 👋\n\nSoy el admin de *Multibanca Express*. Recibimos tu solicitud para *{lead.get('banca')}*.\n\n🏆 *PLAN: {plan_sel.upper()}*\n💰 *INVERSIÓN FINAL: ${total_final:,.2f} USD*\n\n💳 *MÉTODOS DE PAGO:* \n{lista_pagos}\n\n¿Agendamos hoy? 😊"
                    st.link_button("🟢 ENVIAR PROPUESTA POR WHATSAPP", f"https://wa.me/{tel_clean}?text={urllib.parse.quote(msg)}", use_container_width=True)
                    
                    if st.button("🚀 Mover a Seguimiento (Cotizado)", key=f"move_{lead_id}", use_container_width=True, type="primary"):
                        with st.spinner("Moviendo..."):
                            data_seg = {"banca": lead.get('banca'), "representante": lead.get('representante'), "telefono": lead.get('telefono'), "puntos_venta": pts, "plan_cotizado": plan_sel, "total_cotizado": total_final, "estado_seguimiento": "esperando_pago"}
                            supabase.table("leads_seguimiento").insert(data_seg).execute()
                            supabase.table("suscriptores_leads").delete().eq("id", lead_id).execute()
                            st.success(f"✅ Movido a Seguimiento."); time.sleep(1); st.rerun()
    except Exception as e:
        st.error(f"🚨 Error: {e}")

def seccion_seguimiento():
    st.markdown("### ⏳ Prospectos en Espera de Activación")
    try:
        res = supabase.table("leads_seguimiento").select("*").eq("estado_seguimiento", "esperando_pago").execute()
        seguimiento = res.data
        if not seguimiento:
            st.info("No hay clientes pendientes de pago.")
        else:
            df_seg = pd.DataFrame(seguimiento)
            st.dataframe(df_seg[["banca", "representante", "plan_cotizado", "total_cotizado", "telefono"]], use_container_width=True)
            cliente_seg = st.selectbox("Seleccionar para activar:", [f"{s['banca']} - {s['representante']}" for s in seguimiento])
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ DAR DE ALTA (ACTIVAR)", use_container_width=True):
                    st.balloons(); st.success("¡Cliente activado con éxito!")
            with col2:
                if st.button("❌ Cancelar Solicitud", use_container_width=True):
                    sel_id = next(s['id'] for s in seguimiento if f"{s['banca']} - {s['representante']}" == cliente_seg)
                    supabase.table("leads_seguimiento").delete().eq("id", sel_id).execute()
                    st.rerun()
    except Exception as e:
        st.error(f"Error en seguimiento: {e}")

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
            st.dataframe(df_clientes[["email", "nombre_banca", "status", "fecha_vencimiento"]], use_container_width=True, height=300)
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

        with tab2: seccion_solicitudes()
        with tab3: seccion_seguimiento()
        with tab4: seccion_planes()

    except Exception as e:
        st.error(f"🚨 Error de datos: {e}")
