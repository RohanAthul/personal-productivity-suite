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

# Collection Selector - index=None ensures no default selection
collection_name = st.radio(
    "Target Collection:",
    options=["verben", "worte", "nomen"],
    horizontal=True,
    key="col_selector",
    index=None
)

# Logic check: Only show the form if a collection has been selected
if collection_name is None:
    st.info("Please select a target collection to start adding vocabulary.")
else:
    collection = db[collection_name]

    # Use a form to group all inputs
    with st.form("vocab_form", clear_on_submit=True):
        st.subheader(f"General Information ({collection_name})")
        word_val = st.text_input("Word (German)", key="input_word")
        translation_raw = st.text_input("English Translations (separate with commas)", key="input_trans")
        example_de = st.text_input("Example Sentence (DE)", key="input_ex")
        duden_link = st.text_input("Dictionary Link", key="input_link")

        st.divider()
        
        st.subheader("Forms & Auxiliary")
        f1, f2, f3, f4 = st.columns(4)
        infinitiv = f1.text_input("Infinitiv", key="input_inf")
        praeteritum = f2.text_input("Präteritum", key="input_praet")
        partizip_ii = f3.text_input("Partizip II", key="input_p2")
        perfekt_aux = f4.selectbox("Hilfsverb (Perfekt)", ["haben", "sein"], key="input_aux")

        submitted = st.form_submit_button("Load to Database")

        if submitted:
            # Check all primary fields
            fields = [word_val, translation_raw, example_de, infinitiv, 
                      praeteritum, partizip_ii, duden_link]
            
            if not all(f.strip() for f in fields):
                st.error("All fields are required.")
            else:
                # Duplicate check using the "word" key
                if collection.find_one({"word": word_val.strip()}):
                    st.warning(f"'{word_val}' already exists in {collection_name}.")
                else:
                    # Get next ID
                    last_entry = collection.find_one(sort=[("word_id", -1)])
                    new_id = (last_entry["word_id"] + 1) if last_entry else 1

                    # Process translations into a list
                    translation_list = [t.strip() for t in translation_raw.split(",") if t.strip()]

                    doc = {
                        "word_id": new_id,
                        "word": word_val.strip(),
                        "translations": translation_list,
                        "forms": {
                            "infinitiv": infinitiv.strip(),
                            "partizip_II": partizip_ii.strip(),
                            "praeteritum": praeteritum.strip()
                        },
                        "hilfsverben": { "perfekt": perfekt_aux },
                        "example": { "de": example_de.strip() },
                        "dictionary_link": duden_link.strip()
                    }

                    collection.insert_one(doc)
                    st.success(f"Added '{word_val}' (ID: {new_id}) to {collection_name}!")
