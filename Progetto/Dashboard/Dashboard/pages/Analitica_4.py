#ANALITICA 4: I provvedimenti  utilizzati in ambito di respiro, circolo, immmobilizazione in base all'anno (bar chart)
import streamlit as st 
from utils import getProvvedimentiComitato, dbs_new, client
import operator
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Analitica 4",
    page_icon=":medical_symbol:",
    layout="wide"
)

st.title("Analitica :four: - Il numero di provvedimenti utilizzati in ambito respiro, circolo, immobilizzazione o altro in base all'anno scelto.")


selected_year = st.selectbox(" ", dbs_new, index=None, placeholder="Scegli l'anno desiderato...")




def countProvvedimento(selected_year, prov):
    db = client[selected_year]
    provvedimenti  = getProvvedimentiComitato("venezia")[prov]
    countProv = dict.fromkeys(provvedimenti, 0)
    
    for collection_name in db.list_collection_names():
         #provvedimenti relativi a quel provvedimento
        collection = db[collection_name].find({}, {"_id": 0, prov: 1})

        for doc in collection:
            provs_lists= [les.strip() for les in doc[prov].split(", ")]

            for prov_elem in provs_lists:
                if prov_elem in provvedimenti:
                    countProv[prov_elem]  += 1 
    return countProv


def prendiProvvedimenti(selected_year):
    provsGeneral = dict.fromkeys(getProvvedimentiComitato("venezia")["provs"])
    mostUsed = dict.fromkeys(provsGeneral)

    for prov in getProvvedimentiComitato("venezia")["provs"]: #i provvedimenti (respiro, circolo, immobilizzazione, altro)
        mostUsed[prov] = countProvvedimento(selected_year, prov)

    print(mostUsed)
    return mostUsed


def makePlot(mostUsed):

    df = pd.DataFrame(mostUsed).stack().reset_index()
    df.columns = ["metodo utilizzato", "area", "quantità"]

    df = df[df["quantità"] > 0]

    # Crea grafico a barre colorato per metodo utilizzato
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("area:N", title="Area del Provvedimento"),
        y=alt.Y("quantità:Q", title="Quantità"),
        color=alt.Color("metodo utilizzato:N", title="Metodo"),
        tooltip=["area", "metodo utilizzato", "quantità"]
    ).properties(
        title="Metodi utilizzati per area",
        width=700,
        height=500
    )

    st.altair_chart(chart, use_container_width=True)
    
    

if selected_year != None:
    mostUsed = prendiProvvedimenti(selected_year)
    makePlot(mostUsed)





