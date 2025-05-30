import streamlit as st
from utils import client, dbs_new

st.title("Analitica :two: - Riportare il numero di pazienti che hanno una o più specifiche lesioni per ogni anno, tramite istogramma")

#faccio scegliere il db all'utente
anno_scelto = st.selectbox("Scegli l'anno: ", dbs_new, index=0)

#mi estrapolo tutte le possibili lesioni (da tutti i db e da tutte le collezioni di ciascun db)
lesioni = []

for dbs in dbs_new: #per ogni database nel cluster
    db = client[dbs] #mi salvo l'i-mo db
    for collection_name in db.list_collection_names(): #per ogni collezione in uno specifico db
        query_lesioni_riscontrate = db[collection_name].find({'lesioni_riscontrate': 1})
        query_splitted = str(query_lesioni_riscontrate).split(",")
        lesioni.append(query_splitted)


