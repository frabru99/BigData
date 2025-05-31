#ANALITICA 3: Trovare il tempo medio di servizio al mese per ogni anno (simple line chart), è possibile filtrare per Città

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta #per convertire le stringhe orarie in tempi effettivi
from collections import defaultdict
import locale #per la geolocalizzazione italiana (per i mesi)
from utils import client, dbs_new
import re #per convertire i secondi della differenza in minuti

st.set_page_config(
    page_title="Analitica 3",
    page_icon="⌛",
    layout="wide"
)

st.title("Analitica :three: - Trovare il tempo medio di servizio al mese per ogni anno, specificando la città.")

#in questa lista memorizzo le residenze (senza duplicati) di tutti i pazienti
residenze_all_patients = []

def retrieve_documents():
    global residenze_all_patients
    #per filtare sulla città, devo prima retrievare tutte le città nel db
    for dbs in dbs_new:
        db = client[dbs] #accedo al db i-mo
        for collection_name in db.list_collection_names(): #itero sulle collezioni dell'i-mo db
            collection = db[collection_name].find({},{'_id':0,'residente_a': 1})
            for doc in collection: #itero su ogni documento di quella collezione
                if doc['residente_a'] not in residenze_all_patients: #verifico se quella città non è stata già salvata
                    residenze_all_patients.append(doc['residente_a'])

def localization():
    try:
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    except locale.Error:
        # Se 'it_IT.UTF-8' non è disponibile, prova altre varianti o ignora
        try:
            locale.setlocale(locale.LC_TIME, 'it_IT')
        except locale.Error:
            print("Avviso: Impossibile impostare la localizzazione italiana. "
                    "Assicurati che sia installata sul tuo sistema.")

def save_service_times(city_selected, formato_data):
    global service_times_per_month_and_year
    for dbs in dbs_new:
        db = client[dbs]
        for collection_name in db.list_collection_names():
            collection = db[collection_name].find({},{'_id':0, 'residente_a': 1, 'data': 1, 'h_chiamata': 1, 'h_sul_posto': 1})
            for doc in collection:
                if doc['residente_a'] == city_selected:
                    #mi salvo ora chiamata e ora sul posto
                    if doc['h_chiamata'] != " " and doc['h_sul_posto'] != " ":
                        h_call = doc['h_chiamata']
                        h_place = doc['h_sul_posto']
                        mese = doc['data'].split(" ")[1]
                        anno = doc['data'].split(" ")[2]
                        h_call_converted = datetime.strptime(h_call,formato_data)
                        h_place_converted = datetime.strptime(h_place,formato_data)
                        diff = h_place_converted - h_call_converted
                        diff_minutes = diff.seconds / 60
                        service_times_per_month_and_year.append({'tempo di servizio (in minuti)': diff_minutes, 'mese': mese, 'anno': anno}) #mi salvo le medie temporali di servizio per ogni mese

def fill_dictionary_month():
    global dizionario_mese_tempo
    global service_times_per_month_and_year
    for item in service_times_per_month_and_year:
        mese = item['mese']
        anno = item['anno']
        chiave = f"{mese} {anno}"
        if chiave not in dizionario_mese_tempo:
            dizionario_mese_tempo[chiave] = []
        dizionario_mese_tempo[chiave].append(item['tempo di servizio (in minuti)'])

def fill_final_results():
    global dizionario_mese_tempo
    global risultati_finali
    for chiave, medie in dizionario_mese_tempo.items():
        risultati_finali[chiave] = sum(medie) / len(medie) #calcolo la media delle medie per ogni specifico mese

def make_plot(city_selected):
    global risultati_finali
    # Creo una lista con i dati strutturati per DataFrame
    dati_plot = []
    for chiave, valore in risultati_finali.items():
        mese = chiave.strip().split(" ")[0]
        anno = chiave.strip().split(" ")[1]
        dati_plot.append({
            'Anno': anno.strip(),
            'Mese': mese.strip(),
            'Media minuti': valore
        })

    # Converto in DataFrame
    df_plot = pd.DataFrame(dati_plot)

    # Raggruppo per Anno e Mese per calcolare la media
    df_plot_grouped = df_plot.groupby(['Anno', 'Mese'], as_index=False).mean()

    # Ordino i mesi correttamente
    mesi_ordinati = [
        'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
        'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'
    ]

    df_plot_grouped['Mese'] = pd.Categorical(df_plot_grouped['Mese'], categories=mesi_ordinati, ordered=True)
    df_plot_grouped = df_plot_grouped.sort_values(['Anno', 'Mese'])

    # Creo il grafico con Altair
    chart = alt.Chart(df_plot_grouped).mark_line(point=True).encode(
        x=alt.X('Mese:N', sort=mesi_ordinati, title='Mese'),
        y=alt.Y('Media minuti:Q', title='Tempo medio di servizio (minuti)',scale=alt.Scale(align=40)),
        color=alt.Color('Anno:N', title='Anno'),
        tooltip=['Anno', 'Mese', 'Media minuti']
    ).properties(
        width=800,
        height=400,
        title=f'Tempo medio di servizio per mese a {city_selected}'
    )

    # Mostro il grafico su Streamlit
    st.altair_chart(chart, use_container_width=True)



retrieve_documents()

#selectbox per far scegliere la città
city_selected = st.selectbox(" ",residenze_all_patients, index=None, placeholder="Scegli la città...")

if city_selected:

    media_delle_medie_per_mese= []
    service_times_per_month_and_year = []

    localization()

    #mi serve per convertire l'ora da stringa a tipo "datetime"
    formato_data = "%H:%M"

    save_service_times(city_selected, formato_data)

    #print(service_times_per_month_and_year)

    dizionario_mese_tempo = {}

    fill_dictionary_month()

    print(dizionario_mese_tempo)

    risultati_finali={} #dizionario in cui le chiavi sono i mesi e i valori sono le medie delle medie

    fill_final_results()

    print(risultati_finali)

    make_plot(city_selected)
