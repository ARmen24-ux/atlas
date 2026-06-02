import streamlit as st
from auth import USUARIOS

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(page_title="ATLAS Login")

st.title("🔐 ATLAS - Acceso mantenimiento")

st.write("Solo personal autorizado")

# =====================================================
# CONTROL DE SESIÓN
# =====================================================

if "usuario" not in st.session_state:

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        if (
            usuario in USUARIOS
            and USUARIOS[usuario]["password"] == password
        ):

            st.session_state.usuario = usuario
            st.session_state.rol = USUARIOS[usuario]["rol"]

            st.success("Acceso concedido")

            st.switch_page("pages/2_Dashboard.py")

        else:

            st.error("Credenciales incorrectas")

else:

    # ==========================================
    # VALIDAR SESIÓN
    # ==========================================

    if "rol" not in st.session_state:

        if "usuario" in st.session_state:
            del st.session_state.usuario

        st.error("Sesión inválida")
        st.stop()

    # ==========================================
    # SESIÓN ACTIVA
    # ==========================================

    st.success(
        f"Sesión activa: {st.session_state.usuario}"
    )

    # ==========================================
    # CERRAR SESIÓN
    # ==========================================

    if st.button("Cerrar sesión"):

        del st.session_state.usuario
        del st.session_state.rol

        st.rerun()