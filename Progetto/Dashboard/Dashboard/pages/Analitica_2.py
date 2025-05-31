import streamlit as st
import pandas as pd
from utils import client, dbs_new


st.set_page_config(
    page_title="Analitica 2",
    page_icon="⛑️",
    layout="wide"
)

st.title("Analitica :two: - Riportare il numero di pazienti che hanno una o più specifiche lesioni per ogni anno, tramite istogramma.")

#mi estrapolo tutte le possibili lesioni (da tutti i db e da tutte le collezioni di ciascun db)
lesioni = ["amputazione","deformita","dolore","emorragia","ferita profonda","ferita superficiale","trauma chiuso","ustione","deficit motorio","sensibilità assente","frattura","lussazione"]


#questa lista conterrà tutti i pazienti che hanno una di quelle specifiche lesioni selezionate dall'utente
pazienti_con_lesioni = []
lesioni_selezionate = st.multiselect(
    "Scegli una o più lesioni:",
    lesioni,
    default=[],
    placeholder="Scegli almeno una opzione..."
)

lesioni_with_no_patients = []
lesioni_all_collections_and_dbs = []

def query_with_push():
    global lesioni_all_collections_and_dbs
    global pazienti_con_lesioni
    global lesioni_selezionate
    for dbs in dbs_new: #per ogni database nel cluster
        db = client[dbs] #mi salvo l'i-mo db
        for collection_name in db.list_collection_names(): #per ogni collezione in uno specifico db
            collection = db[collection_name].find({}, {"_id": 0, "lesioni_riscontrate": 1, "data": 1, "cognome_nome": 1}) #mi recupero ogni collezione nel db

            for doc in collection:
                lesioni_str=doc.get('lesioni_riscontrate')
                #verifico se 'lesioni_riscontrate' sia una stringa ed esista
                if lesioni_str and isinstance(lesioni_str, str):
                #inserisco nella lista di lesioni tutte le
                #lesioni_db = [l.strip() for l in lesioni_str.split(', ') if l.strip()]
                    lesioni_db = [les.strip() for les in lesioni_str.split(", ")]

                else:
                    lesioni_db = []

                if any(lesione_selezionata in lesioni_db for lesione_selezionata in lesioni_selezionate): #verifico se almeno una delle lesioni selezionate sia presente in uno specifico paziente
                #print(lesioni_db)
                    paziente=doc['cognome_nome'] #mi estrapolo il suo nome e cognome
                    anno = doc['data'].split(" ")[2] #mi salvo l'anno in cui il soccorso è avvenuto
                    for lesione in lesioni_db:
                        #print(lesione)
                        if lesione in lesioni_selezionate:
                        #print("HEY")
                            pazienti_con_lesioni.append({'cognome_nome': paziente, 'anno': anno, 'lesione': lesione}) #li appendo nella lista complessiva come un dizionario
                        #se la seguente lesione non è presente nella lista delle lesioni dell'intero cluster, allora la pusho
                        if lesione not in lesioni_all_collections_and_dbs:
                            lesioni_all_collections_and_dbs.append(lesione)

#print(lesioni_all_collections_and_dbs)
def plot_optimization():
    global lesioni_all_collections_and_dbs
    global lesioni_with_no_patients
    global lesioni_selezionate
    #per ogni lesione selezionata, controllo se ognuna di esse sia presente (o meno) nella lista "totale"
    for les in lesioni_selezionate:
        if les not in lesioni_all_collections_and_dbs:
            lesioni_with_no_patients.append(les)    
    if len(lesioni_with_no_patients) > 0:
        st.error(f"Non è presente nessun paziente per le seguenti lesioni: {lesioni_with_no_patients}", icon = "🚨")

def plot_bar_chart(pazienti_con_lesioni):
    df_lesioni_occorrenze = pd.DataFrame(pazienti_con_lesioni)

    if 'lesione' in df_lesioni_occorrenze.columns and 'anno' in df_lesioni_occorrenze.columns:
        st.subheader("Occorrenze di Ogni Lesione Selezionata per Anno")
        conteggio_lesioni_per_anno_tipo = df_lesioni_occorrenze.groupby(['anno', 'lesione']).size().reset_index(name='Numero di Occorrenze')
        try:
            conteggio_lesioni_per_anno_tipo['anno'] = pd.to_numeric(conteggio_lesioni_per_anno_tipo['anno'], errors='coerce')
            conteggio_lesioni_per_anno_tipo.dropna(subset=['anno'], inplace=True)
            df_lesioni_occorrenze['anno'] = df_lesioni_occorrenze['anno'].astype(str)
            conteggio_lesioni_per_anno_tipo['anno']  = conteggio_lesioni_per_anno_tipo['anno'].replace(',','')
            conteggio_lesioni_per_anno_tipo['anno'] = conteggio_lesioni_per_anno_tipo['anno'].astype(int)
            conteggio_lesioni_per_anno_tipo = conteggio_lesioni_per_anno_tipo.sort_values(by='anno')
        except Exception as e:
            st.warning(f"Impossibile convertire o ordinare gli anni per il grafico dettagliato. Errore: {e}")

        conteggio_pivotato = conteggio_lesioni_per_anno_tipo.pivot_table(
            index='anno',
            columns='lesione',
            values='Numero di Occorrenze'
        ).fillna(0)

        conteggio_pivotato.index.name = 'Anno'

        st.dataframe(conteggio_pivotato, use_container_width=True)
        st.bar_chart(conteggio_pivotato, stack=False)

    plot_optimization()

query_with_push()
plot_bar_chart(pazienti_con_lesioni)
