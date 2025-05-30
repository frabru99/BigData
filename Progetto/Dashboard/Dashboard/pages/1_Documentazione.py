import streamlit as st
from utils import bullet_list

st.set_page_config(
    page_title="Documentazione",
    page_icon="🗒️",
    layout="wide"
)

st.markdown("<h2 style='text-align: center;'>Documentazione del progetto<br>di Big Data Engineering</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Anno 2024/2025</h6>", unsafe_allow_html=True)

st.write("Boccarossa Antonio M63001643")
st.write("Brunello Francesco M63001655")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""


# Voice2Care - A voice for Health
  **Boccarossa Antonio M63001643** 
  
  **Brunello Francesco M63001655**
""")

st.image("Dashboard/Dashboard/static/img/Voice2Care.png", width=200)


st.markdown("""
## ❓ Problema

Nel contesto sanitario, soprattutto nei reparti di emergenza, il personale medico è spesso costretto a trascrivere manualmente annotazioni cliniche in condizioni di stress e urgenza. Questo processo è:
- Lento e dispendioso in termini di tempo,
- Poco scalabile,
- Non ottimizzato per l’integrazione con i moderni sistemi informatici sanitari.

## 💡 Soluzione

_Voice2Care - A voice for health_ è un sistema integrato che automatizza il processo di documentazione clinica partendo da registrazioni vocali. Grazie a tecnologie di riconoscimento vocale, LLM (Large Language Model) e una dashboard interattivq, la piattaforma consente:
- La trascrizione automatica di note vocali.
- L’estrazione e strutturazione di informazioni cliniche rilevanti, al fine di compilare il report strutturato, in formato PDF.
- L’archiviazione rapida e scalabile tramite un database NoSQL Documentale.
- La visualizzazione di analitiche utili sui dati raccolti.

## 🧱 Architettura del Sistema
""")

st.image("Dashboard/Dashboard/static/img/BigDataStructure.jpg")

st.markdown(
"""
1. Voce del Medico catturata da interfaccia Web-Based
2. Server-Side
   1. **Speech-to-Text**
      1. Modello Speech-to-Text (**Whisper AI**)  
      2. LLM (**Gemini 2.0 Flash**)  
      3. Output strutturato in JSON  
      4. Modifica e conferma da parte del medico
   2. **Data Elaboration**
      1. Compilazione del PDF
      2. Decodifica e inserimento nel JSON finale
3. Database NoSQL per lo Storage (**MongoDB**)  
4. Dashboard interattiva (**Streamlit**)  

## ⏯️ Come Avviare il Progetto

1. Clona il repository:
   - `git clone https://github.com/frabru99/BigData.git`
   - `cd Progetto`
   -  **Caricare il Notebook su Colab e inserire le proprie API_KEY per Gemini, Ngrok e MongoDB Atlas**. 
   La struttura del Workspace dovrà essere la seguente:

      ```bash
      .
      └── Colab  Workspace/
         ├── static/
         │   ├── Voice2Care.png
         │   └── stle.css
         ├── templates/
         │   └── page.html
         └── report.pdf
      ```


2. Installa le dipendenze (per la Dashboard da eseguire in locale):
   - `pip install -r requirements.txt`

3. Avvia i componenti:
   - Avvia il notebook e accedi alla pagina wev esposta da ngrok.
   - Avvia la dashboard con: `streamlit run HomePage.py`
  
### 🕸️ Web Page
""")


st.image("Dashboard/Dashboard/static/img/ScreenShot_1.png", width= 500)
st.image("Dashboard/Dashboard/static/img/ScreenShot_2.png", width= 500)
st.image("Dashboard/Dashboard/static/img/ScreenShot_3.png", width= 500)



st.markdown("""
## 🧪 Esempi d’Uso

- Chiamata al pronto soccorso: voce medico → trascrizione e generazione del documento.
- Briefing post intervento


## 📊 Tipologie di Dati Gestiti

- Audio registrato (**.mp3**)
- Testo trascritto
- JSON strutturati
- PDF

## 📈 Analitiche
- **Analitica 1**: 
- **Analitica 2**:
- **Analitica 3**:
- **Analitica 4**:
- **Analitica 5**:

## 🛠️ Tecnologie Utilizzate

- Whisper AI - Speech-to-text  
- Gemini 2.0 Flash - LLM  
- MongoDB - Database NoSQL  
- Streamlit - Dashboard UI  
- pymupdf, pyPDF2 - Generazione PDF

             """)

st.markdown("</br>", unsafe_allow_html=True)