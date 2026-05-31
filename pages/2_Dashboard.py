import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard", layout="wide")

RUTA = "data/reportes.csv"

if not os.path.exists(RUTA):
    st.warning("No hay datos")
    st.stop()

df = pd.read_csv(RUTA)
df.columns = df.columns.str.strip()

# FIX AUTOMÁTICO
for col in ["Edificio","Area","Activo","Categoria","Impacto","Estado"]:
    if col not in df.columns:
        df[col] = "Sin dato"

st.title("Dashboard ATLAS")

st.metric("Total reportes", len(df))

fig = px.bar(df["Activo"].value_counts().reset_index(),
             x="index", y="Activo")

st.plotly_chart(fig, use_container_width=True)
