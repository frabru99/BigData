import streamlit as st
import pymongo
import base64, os
from utils import client, dbs_new
from geopy.geocoders import Nominatim
from pprint import pprint
import pandas as pd
import numpy as np

app = Nominatim(user_agent="tutorial")

st.set_page_config(
    page_title="Analitica 1",
    page_icon="👤",
    layout="wide"
)

st.title('Analitica :one: - Recupero di tutti i documenti per uno specifico anno e mese')

#id globale univoco per discriminare i documenti
ids = 0

col3, col4 = st.columns(2)


def carica_pdf_per_anno(selected_year):
    city_list = []
    global ids

    st.markdown("\n")
    st.warning("Una volta fatto l'upload del nuovo pdf, rieseguire i filtri per visualizzare le modifiche.", icon="⚠️")

    print(selected_year) #debug
    db=client[selected_year] #accedo al db scelto dall'utente
    pdf_data_list = [] #mi salvo tutti i pdf decodificati

    months = sorted(db.list_collection_names())
    with col4:
        month = st.selectbox(" ", months, index=None, placeholder="Scegli il mese desiderato...")

    if month != None:
        months= []
        months.append(month)

    st.markdown("\n")
    for collection_name in months: #ciclo su tutte le collezioni di quel db scelto
        collection=db[collection_name].find({}, {"_id": 1, "cognome_nome":1, "sesso": 1, "pdf": 1, "pdf_aggiornato": 1, "nato_il": 1, "residente_a": 1, "data": 1, "condizione_riferita":1}).sort("data", 1) #recupero tutti i documenti

        st.markdown(f"---")
        st.markdown(f"## :gray[_{collection_name.split("_")[1].capitalize()}_]")

        for doc in collection: #per ogni pdf nella collezione
            st.markdown("\n")
            cognome_paziente = doc['cognome_nome'].split(" ")[0]
            nome_paziente = doc['cognome_nome'].split(" ")[1]
            
            
            if "maschile" in doc["sesso"] or "maschio" in doc["sesso"]:
                st.markdown(f"### {cognome_paziente} {nome_paziente} :male_sign: ")
            elif "femminile" in doc["sesso"] or "femmina" in doc["sesso"]:
                st.markdown(f"### {cognome_paziente} {nome_paziente} :female_sign: ")
            else:
                st.markdown(f"### {cognome_paziente} {nome_paziente} ")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"_Nato il_: {doc["nato_il"]}")
                st.markdown(f"_Residente a_: {doc["residente_a"]}") 
                city_list.append(doc["residente_a"])

            with col2:
                st.markdown(f"**_Data dell'intervento_**: {doc["data"].capitalize()}")
                st.markdown(f"**_Condizione riferita_**: {doc["condizione_riferita"].capitalize()}")


            try:
                if "pdf_aggiornato" in doc and doc["pdf_aggiornato"] != " ":
                    decoded_pdf = base64.b64decode(doc['pdf_aggiornato']) #decodifico
                    with col2:
                        st.markdown("\n")

                        if st.button("Elimina pdf aggiornato", type="primary", key=f"document_{ids+1}"):
                            removeUpdatedPdf(selected_year, collection_name, doc["_id"])
                else:
                    decoded_pdf = base64.b64decode(doc['pdf']) #decodifico
                
                #pulsante per scaricare il pdf di uno specifico paziente
                with col1:
                    st.markdown("\n")
                    st.download_button(
                    label=f"Scarica Documento {ids + 1}",
                    data=decoded_pdf,
                    file_name=f"documento_{selected_year}_{ids + 1}.pdf",
                    mime="application/pdf",
                    key=f"download_button_{selected_year}_{ids+1}" # Chiave unica per ogni pulsante
                    )
                ids = ids + 1
            except Exception as e:
                st.error(f"Errore durante la decodifica del PDF per il documento: {e}")  
            
            uploaded_file = st.file_uploader(" ", type="pdf", key=f"upload_button_{selected_year}_{ids}")

            if uploaded_file != None:
                updatePDF(selected_year, collection_name, uploaded_file, doc["_id"])

    return city_list


def removeUpdatedPdf(selected_year, collection_name, id):
    db = client[selected_year]
    result = db[collection_name].update_one({"_id": id}, {"$set": {"pdf_aggiornato": " "}})


    if result.modified_count > 0:
        st.toast("PDF aggiornato rimosso!", icon="✅")
    else:
        st.toast("PDF aggiornato non rimosso!", icon="🚨")



def updatePDF(selected_year, collection_name, uploaded_file, id):
    pdf_base64 = base64.b64encode(uploaded_file.read()).decode('utf-8')
    db = client[selected_year]
    result = db[collection_name].update_one({"_id": id}, {"$set": {"pdf_aggiornato": pdf_base64}})


    if result.modified_count > 0:
        st.toast("PDF aggiornato correttamente!", icon="✅")
    else:
        st.toast("PDF non aggiornato!", icon="🚨")




@st.cache_data
def createMap(city_list):
    st.markdown("\n")
    dataframe_map_year = pd.DataFrame(columns=["lat", "lon", "color"]) #dataframe latitudini e longitudini
    for city in city_list:
        location = app.geocode(city).raw
        dataframe_map_year = dataframe_map_year._append({"lat": float(location["lat"]), "lon": float(location["lon"]), "color": list(np.random.rand(3))}, ignore_index=True) #retrieve latitudine elongitudine per anno
    
    st.markdown(f"## Mappa delle residenze")
    st.map(dataframe_map_year, latitude="lat", longitude="lon", color="color")
#selectbox per scegliere l'anno


with col3:
    selected_year = st.selectbox(" ", dbs_new, index=None, placeholder="Seleziona l'anno di interesse...") #index=1 indica che dovrò avere almeno un elemento in output


if selected_year != None:
    city_list = carica_pdf_per_anno(selected_year) #invoco la funzione ogni volta che riclicco la selectbox
    createMap(city_list)