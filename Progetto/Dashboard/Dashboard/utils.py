import streamlit as st
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

provvedimenti = {
    "venezia": {
     "provs": ["respiro", "circolo", "immobilizzazione", "provvedimenti_altro"], 
     "respiro": ["aspirazione", "cannula orofaringea", "monitor spO2", "ossigeno", "ventilazione", "intubazione"],
     "circolo":  ["emostasi", "accesso venoso", "ecg", "nibp", "monitor ecg", "monitor nibp", "dae"], 
     "immobilizzazione": ["collare cervicale", "KED", "barella cucchiaio", "tavola spinale", "steccobenda", "materassino"],
     "provvedimenti_altro":  ["coperta termica", "medicazione", "ghiaccio",  "osservazione"]
    }
}

    
def init_MongoDB_connection():
    client = pymongo.MongoClient(f"mongodb+srv://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@voice2care.vr6lf61.mongodb.net/?retryWrites=true&w=majority&appName=Voice2Care")
    dbs= client.list_database_names() #mi recupero tutti i db nel mio cluster
    dbs_new = [db_name for db_name in dbs if db_name not in ["admin", "local", "config"]] #mi interessa accedere solo ai db aggiunti dall'ospedale (quindi escluso quelli "riservati")
    return client, dbs_new

def getProvvedimentiComitato(comitato):
    return provvedimenti[comitato]

client,dbs_new = init_MongoDB_connection()