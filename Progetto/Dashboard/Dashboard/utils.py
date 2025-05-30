import streamlit as st
import pymongo

def bullet_list(grassetto, normale):
    st.markdown(f"- <span style='color:#00acee'><b>{grassetto}</b></span>: {normale}",
            unsafe_allow_html=True)
    
def init_MongoDB_connection():
    client = pymongo.MongoClient("mongodb+srv://Smembratori:Smembratori99@voice2care.vr6lf61.mongodb.net/?retryWrites=true&w=majority&appName=Voice2Care")
    dbs= client.list_database_names() #mi recupero tutti i db nel mio cluster
    dbs_new = [db_name for db_name in dbs if db_name not in ["admin", "local", "config"]] #mi interessa accedere solo ai db aggiunti dall'ospedale (quindi escluso quelli "riservati")
    return client, dbs_new

client,dbs_new = init_MongoDB_connection()