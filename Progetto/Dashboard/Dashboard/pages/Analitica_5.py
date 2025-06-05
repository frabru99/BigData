#Trovare per ogni sesso quali sono i valori medi di frequenza cardiaca
import streamlit as st
import pandas as pd
from utils import client, dbs_new
from datetime import datetime
from deep_translator import GoogleTranslator


st.set_page_config(
    page_title="Analitica 5",
    page_icon = "⚧️",
    layout="wide"
)

st.title("Analitica :five: - Il valore medio di frequenza caridaca per il sesso specificato in base all'anno e al mese (se specificati)")

sesso_paziente = ['maschio', 'femmina']
lista_media_uomo = []
lista_media_donna = []
lista_media_non_specificato = []

def elaborate_bpms(sesso_scelto, selected_year):
    global lista_media_uomo
    global lista_media_donna
    global lista_media_non_specificato

    
    month_selected_list=[]
    dbs_in = []
    selected_month = " "

    if selected_year == None:
        dbs_in = dbs_new

    else:
        dbs_in.append(selected_year)
        
        db = client[selected_year]
        month_selection = sorted(db.list_collection_names(), key= lambda month: datetime.strptime(GoogleTranslator(source="it", target="en").translate(month.split("_")[1].capitalize()), "%B"))
        selected_month = st.selectbox(" ", month_selection, key=f"moths", index=None, placeholder="Seleziona il mese di interesse...") #index=1 indica che dovrò avere almeno un elemento in output

    
    for dbs in dbs_in:
        if selected_year == None:
            db = client[dbs]
            month_selected_list = db.list_collection_names()
        
        if selected_month == None:
            month_selected_list = db.list_collection_names()
        else:
            month_selected_list.append(selected_month)

      
        for collection_name in month_selected_list:
            print(collection_name)
            collection = db[collection_name].find({}, {"_id": 0, "sesso": 1, "t1_fc_bpm": 1, "t2_fc_bpm": 1, "t3_fc_bpm": 1, "data": 1})
            
            for doc in collection:
                if doc['sesso'] == 'maschile' or doc['sesso'] == sesso_scelto or doc['sesso'] == 'uomo': #se il sesso del paziente corrisponde a quello scelto
                    lista_bpm_uomo = []
                    if doc['t1_fc_bpm'] != " ":
                        lista_bpm_uomo.append(int(doc['t1_fc_bpm'].split(" ")[0]))
                    elif doc['t2_fc_bpm'] != " ":
                        lista_bpm_uomo.append(int(doc['t2_fc_bpm'].split(" ")[0]))
                    elif doc['t3_fc_bpm'] != " ":
                        lista_bpm_uomo.append(int(doc['t3_fc_bpm'].split(" ")[0]))
                    if len(lista_bpm_uomo) > 0:
                        media = float(sum(lista_bpm_uomo) / len(lista_bpm_uomo))
                        lista_media_uomo.append(media)
                elif doc['sesso'] == 'donna' or doc['sesso'] == 'femminile' or doc['sesso'] == sesso_paziente:
                    lista_bpm_donna = []
                    if doc['t1_fc_bpm'] != " ":
                        lista_bpm_donna.append(int(doc['t1_fc_bpm'].split(" ")[0]))
                    elif doc['t2_fc_bpm'] != " ":
                        lista_bpm_donna.append(int(doc['t2_fc_bpm'].split(" ")[0]))
                    elif doc['t3_fc_bpm'] != " ":
                        lista_bpm_donna.append(int(doc['t3_fc_bpm'].split(" ")[0]))
                    if len(lista_bpm_donna) > 0:
                        media = float(sum(lista_bpm_donna) / len(lista_bpm_donna))
                        lista_media_donna.append(media)
                elif doc['sesso'] == " ": #sesso non specificato, nel caso in cui non venga inserito nel campo del report del paziente
                    lista_bpm_non_specificato = []
                    if doc['t1_fc_bpm'] != " ":
                        lista_bpm_non_specificato.append(int(doc['t1_fc_bpm'].split(" ")[0]))
                    elif doc['t2_fc_bpm'] != " ":    
                        lista_bpm_non_specificato.append(int(doc['t2_fc_bpm'].split(" ")[0]))
                    elif doc['t3_fc_bpm'] != " ":
                        lista_bpm_non_specificato.append(int(doc['t3_fc_bpm'].split(" ")[0]))
                    if len(lista_bpm_non_specificato) > 0:
                        media = float(sum(lista_bpm_non_specificato) / len(lista_bpm_non_specificato))
                        lista_media_non_specificato.append(media)
        


col1, col2 = st.columns(2)

#ora calcoliamo la media delle medie per ogni lista

def process_averages():
    #media delle medie per uomo
    if len(lista_media_uomo) > 0: 
        media_delle_medie_uomo = (sum(lista_media_uomo) / len(lista_media_uomo))
    else:
        media_delle_medie_uomo = 0

    #media delle medie per donna
    if len(lista_media_donna) > 0: 
        media_delle_medie_donna = (sum(lista_media_donna) / len(lista_media_donna))
    else:
        media_delle_medie_donna = 0
    #media delle medie per sesso non specificato
    if len(lista_media_non_specificato) > 0: 
        media_delle_medie_non_specificato = (sum(lista_media_non_specificato) / len(lista_media_non_specificato))
    else:
        media_delle_medie_non_specificato = 0
    return media_delle_medie_uomo, media_delle_medie_donna, media_delle_medie_non_specificato


def plot(sesso_scelto, media_delle_medie_uomo, media_delle_medie_donna, media_delle_medie_non_specificato):
    # DataFrame per il grafico
    df_complessivo = pd.DataFrame({
        'Media delle medie': [media_delle_medie_uomo, media_delle_medie_donna, media_delle_medie_non_specificato]
    }, index=['Uomo', 'Donna', 'Non specificato'])
    if sesso_scelto == None:
        st.markdown("### Media complessiva")
        st.bar_chart(df_complessivo)
    elif sesso_scelto == "maschio":
        media_uomo = df_complessivo.loc['Uomo','Media delle medie']
        df_maschio = pd.DataFrame({'Media FC BPM': [media_uomo]}, index=['Uomo'])
        # Grafico a barre con Streamlit
        st.markdown("### Media complessiva per gli uomini")
        st.bar_chart(df_maschio,y="Media FC BPM")
    elif sesso_scelto == "femmina":
        media_donna = df_complessivo.loc['Donna','Media delle medie']
        df_donna = pd.DataFrame({'Media FC BPM': [media_donna]}, index=['Donna'])
        # Grafico a barre con Streamlit
        st.markdown("### Media complessiva per le donne")
        st.bar_chart(df_donna,y="Media FC BPM")

with col1:
    sesso_scelto = st.selectbox(" ", sesso_paziente, index=None, placeholder="Scegli il sesso...")
with col2:
     selected_year = st.selectbox(" ", dbs_new, index=None, placeholder="Seleziona l'anno di interesse...") #index=1 indica che dovrò avere almeno un elemento in output


elaborate_bpms(sesso_scelto, selected_year)

media_delle_medie_uomo, media_delle_medie_donna, media_delle_medie_non_specificato = process_averages()

plot(sesso_scelto, media_delle_medie_uomo, media_delle_medie_donna, media_delle_medie_non_specificato)