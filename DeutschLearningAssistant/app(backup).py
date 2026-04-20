import streamlit as st
import pymongo
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

@st.cache_resource
def init_connection():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        st.error("MONGODB_URI not found in .env file")
        st.stop()
    return pymongo.MongoClient(uri)

client = init_connection()
db = client["deutsch"]

st.title("Deutsch Vocabulary Manager")

# Collection Selector
collection_name = st.radio(
    "Target Collection:",
    options=["verben", "worte", "nomen"],
    horizontal=True,
    key="col_selector"
)
collection = db[collection_name]

# Use a form to group all inputs
with st.form("vocab_form", clear_on_submit=True):
    st.subheader("General Information")
    word = st.text_input("Word (Worte)", key="input_word")
    translation = st.text_input("English Translation", key="input_trans")
    example_de = st.text_input("Example Sentence (DE)", key="input_ex")

    st.divider()
    
    st.subheader("Forms & Auxiliary")
    f1, f2, f3, f4 = st.columns(4)
    infinitiv = f1.text_input("Infinitiv", key="input_inf")
    praeteritum = f2.text_input("Präteritum", key="input_praet")
    partizip_ii = f3.text_input("Partizip II", key="input_p2")
    perfekt_aux = f4.selectbox("Hilfsverb (Perfekt)", ["haben", "sein"], key="input_aux")

    st.divider()
    
    st.subheader("Präsens Conjugation")
    # Row 1
    c1, c2, c3, c4 = st.columns(4)
    ich = c1.text_input("ich", key="conj_ich")
    du = c2.text_input("du", key="conj_du")
    er_sie_es = c3.text_input("er/sie/es", key="conj_er")
    wir = c4.text_input("wir", key="conj_wir")
    
    # Row 2
    c5, c6, c7, c8 = st.columns(4)
    ihr = c5.text_input("ihr", key="conj_ihr")
    sie_pl = c6.text_input("Sie/sie", key="conj_sie")

    submitted = st.form_submit_button("Load to Database")

    if submitted:
        # Check all fields
        fields = [word, translation, example_de, infinitiv, praeteritum, 
                  partizip_ii, ich, du, er_sie_es, wir, ihr, sie_pl]
        
        if not all(f.strip() for f in fields):
            st.error("All fields are required.")
        else:
            # Duplicate check
            if collection.find_one({"worte": word.strip()}):
                st.warning(f"'{word}' already exists in {collection_name}.")
            else:
                # Get next ID
                last_entry = collection.find_one(sort=[("word_id", -1)])
                new_id = (last_entry["word_id"] + 1) if last_entry else 1

                doc = {
                    "word_id": new_id,
                    "worte": word.strip(),
                    "translation": translation.strip(),
                    "forms": {
                        "infinitiv": infinitiv.strip(),
                        "partizip_II": partizip_ii.strip(),
                        "praeteritum": praeteritum.strip()
                    },
                    "hilfsverben": { "perfekt": perfekt_aux },
                    "conjugation": {
                        "praesens": {
                            "ich": ich.strip(),
                            "du": du.strip(),
                            "er": er_sie_es.strip(),
                            "sie": er_sie_es.strip(),
                            "es": er_sie_es.strip(),
                            "wir": wir.strip(),
                            "ihr": ihr.strip(),
                            "Sie": sie_pl.strip()
                        }
                    },
                    "example": { "de": example_de.strip() }
                }

                collection.insert_one(doc)
                st.success(f"Added '{word}' (ID: {new_id}) to {collection_name}!")
                