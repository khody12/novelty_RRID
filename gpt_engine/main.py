import openai
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from pyairtable import Api
load_dotenv()
api = Api(os.getenv("AIRTABLE_API_KEY"))
table = api.table("appvtCMw78DSAMOUH", "Team1_Preprints")

# example pipeline
from gpt_engine.engine_test import generate_novelty
from faiss_engine.engine import find_similarity
def get_preprints():
    records = table.all()
    preprints = []
    for r in records:
        fields = r['fields']
        if 'Abstract' in fields and 'Title' in fields:
            preprints.append({
                'id': r['id'],  # Useful if you want to update later
                'title': fields['Title'],
                'abstract': fields['Abstract'],
                'id_score': fields.get('ID Score'),
                'team_score': fields.get('Team Score')
            })
            # at this point, we need to scrape 
    return preprints

def fetch_preprints():
    records = table.all()
    for i, record in enumerate(records[:10]):  # Show first 10 for preview
        print(f"\n--- Preprint {i+1} ---")
        for key, value in record['fields'].items():
            print(f"{key}: {value}")

preprints = get_preprints()


for preprint in preprints:
    preprint_model_info = {}
    preprint_model_info["Title"] = preprint["title"]
    preprint_model_info["Abstract"] = preprint["abstract"] # here we will add retrieval of H-index and citations once we figure out the scraping approach. 
    preprint_model_info["Similarity"] = float(find_similarity(preprint_model_info["Title"], preprint_model_info["Abstract"])) # find_similiarity returns a np.float32 because of faiss' format. this isn't compatible with json.dump so we convert to float.

    preprint_model_info["novelty_score"] = generate_novelty(preprint_model_info) # add a new novelty_score. then we can just push these to the airtable and then sort via existing sort.py.
    print(preprint_model_info["novelty_score"])


