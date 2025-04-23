import openai
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from pyairtable import Api
import requests
from scholarly import scholarly
load_dotenv()

api = Api(os.getenv("AIRTABLE_API_KEY"))
table = api.table("appvtCMw78DSAMOUH", "Team1_Preprints")
import sys
# example pipeline
from gpt_engine.engine_test import generate_novelty
from faiss_engine.engine import find_similarity

def get_authors_in_array(input):
    output = []
    if input:
        input = input.split(";")
        for ele in input:
            ele = ele.replace(",", "")
            output.append(ele)
    return output

def get_preprints():
    records = table.all()
    preprints = []
    num = 0
    for r in records: # 10 for testing and eval. 
        num += 1
        if num > 10:
            print("done")
            break
        
        fields = r['fields']
        authors = get_authors_in_array(r['fields']['Authors'])
        author = authors[0]
        print(author)
        if 'Abstract' in fields and 'Title' in fields:
            preprints.append({
                'id': r['id'],  # Useful if you want to update later
                'title': fields['Title'],
                'abstract': fields['Abstract'],
                'h_index': fetch_h_index_for_preprint(author)
            })
            # at this point, we need to scrape 
    return preprints

def verify_h_index(name):
    search_query = scholarly.search_author(name)
    try:
        #only one return
        author = next(search_query)
        filled_author = scholarly.fill(author, sections=['basics', 'indices'])
        h_index = filled_author.get("hindex")
        #several returns
    except:
        h_index = 0
    return h_index

def fetch_h_index_for_preprint(author_name):

    base_url = "https://api.openalex.org/authors"
    params = {"search": author_name}
    response = requests.get(base_url, params=params, timeout=10)

    if response.status_code != 200:
        print(f"fail: {response.status_code}")
        return None
        
    data = response.json()
    val = data.get("results", [])

    #not find in openAlex --> search in google sholar
    if not val:
        # print("not found2")
        h_index = verify_h_index(author_name)
        # print(h_index)
    else:
        works_count = val[0].get("works_count",0)
        # with open("records_output.json", "w") as f:
        #     json.dump(val[0], f, indent=2, ensure_ascii=False)
        if works_count > 50000:
            h_index = verify_h_index(author_name)
        else:
            h_index = val[0]["summary_stats"].get("h_index", None)
    print(h_index)
    
    return h_index

def fetch_preprints():
    records = table.all()
    for i, record in enumerate(records[:10]):  # Show first 10 for preview
        print(f"\n--- Preprint {i+1} ---")
        for key, value in record['fields'].items():
            print(f"{key}: {value}")

preprints = get_preprints()


for preprint in preprints:
    preprint_model_info = {}

    #preprint[h_index] = fetch_hetch_index_for_preprint(author_corr) 
    # this right here is so that we can keep the existing dictionary with all of its information but only pass the information we really want the model to see. 
    preprint_model_info["Title"] = preprint["title"]
    preprint_model_info["Abstract"] = preprint["abstract"] # here we will add retrieval of H-index and citations once we figure out the scraping approach. 
    preprint_model_info["Similarity"] = float(find_similarity(preprint_model_info["Title"], preprint_model_info["Abstract"])) # find_similiarity returns a np.float32 because of faiss' format. this isn't compatible with json.dump so we convert to float.
    preprint_model_info["h_index"] = preprint["h_index"]
    preprint_model_info["novelty_score"] = generate_novelty(preprint_model_info) # add a new novelty_score. then we can just push these to the airtable and then sort via existing sort.py.
    
    print(preprint_model_info["novelty_score"])