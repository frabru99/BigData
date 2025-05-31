import streamlit as st

st.set_page_config(
    page_title = "Homepage",
    page_icon="🏠",
    layout='wide'
)
#st.image("METTERE EVENTUALMENTE LOGO VOICE2CARE")
st.title("Dashboard Analitiche - **Voice2Care: A voice for Health**") 

st.write(""" L'obiettivo di tale dashboard è riportare una serie di reportistiche che permettano di conoscere informazioni sui pazienti, 
recuperare i pdf, visualizzare la mappa delle residenze e effettuare ulteriori analisi.  """)

st.page_link("pages/Analitica_1.py", label="Analitica", icon="1️⃣")
st.markdown("$\quad \quad$ **Questa sezione permette di recuperare le _informazioni utili in base all'anno e al mese specificato_. E' possibile consultare anche una :green[_Mappa delle Residenze_] in base al filtro specificato.**")

st.page_link("pages/Analitica_2.py", label="Analitica", icon="2️⃣")
st.markdown("$\quad \quad$ **Questa sezione permette di recuperare informazioni per quanto riguarda la quantità di pazienti che hanno _contratto certe :red[lesioni]_ che è possibile specificare.**")


st.page_link("pages/Analitica_3.py", label="Analitica", icon="3️⃣")
st.markdown("$\quad \quad$ **Questa sezione permette di valutare come evolte il :grey[tempo medio di servizio] (per anno) inteso come, _ora sul posto - ora chiamata_ in base alla città scelta**")


st.page_link("pages/Analitica_4.py", label="Analitica", icon="4️⃣")
st.markdown("$\quad \quad$ **Questa sezoione permette di valutare quali sono i _:blue[provvedimenti] più utilizzati_ in base all'anno scelto.**")

st.page_link("pages/Analitica_5.py", label="Analitica", icon="5️⃣")
st.markdown("$\quad \quad$ **Questa sezione permette di valutare quale è la :violet[Frequenza Cardiaca Media] presente nel DataBase in base al sesso specificato, con la possibilità di specificare l'anno e il mese di interesse.**")




