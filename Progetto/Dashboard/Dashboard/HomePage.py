import streamlit as st
from utils import bullet_list

st.set_page_config(
    page_title = "Homepage",
    page_icon="🏠",
    layout='wide'
)
#st.image("METTERE EVENTUALMENTE LOGO VOICE2CARE")
st.title("Dashboard Analitiche Healthcare")
st.write("L'obiettivo di tale dashboard è riportare una serie di reportistiche che permettano di conoscere...")

st.write("Le analitiche sono divise in <> gruppi .....")

bullet_list("Analitica 1 - ....", "Questa sezione ...")

bullet_list("Analitica 2 - ....", "Questa sezione ...")

bullet_list("Analitica 3 - ....", "Questa sezione ...")
