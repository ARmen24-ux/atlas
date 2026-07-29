from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

st.write("URL:", SUPABASE_URL)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

try:
    prueba = (
        supabase
        .table("reportes")
        .select("*")
        .limit(1)
        .execute()
    )

    st.success("Conexión correcta")
    st.write(prueba.data)

except Exception as e:

    st.error(e)