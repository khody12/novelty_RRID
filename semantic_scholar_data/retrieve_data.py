import requests
import time # pause between requests due to semantic scholar rate limit
import json
import os


BATCH_SIZE = 100
MAX_RESULTS = 500
SAVE_FILE = "test.json"
SEEN_FILE = "seen_ids.json"

FIELDS = "title,abstract,year,authors,paperId,citationCount,fieldsOfStudy,publicationDate"

def load_seen_ids():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()
def save_seen_ids(seen_ids):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_ids), f, indent=2)

def save_papers(new_papers):
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            existing = json.load(f)
    else:
        existing = []
    existing.extend(new_papers)

    with open(SAVE_FILE, "w") as f:
        json.dump(existing, f, indent=2)

QUERIES = [
    "emerging infectious diseases",
    "zoonotic disease transmission",
    "viral zoonosis",
    "pathogen surveillance",
    "infectious disease modeling",
    "epidemiological forecasting",
    "pandemic preparedness",
    "vaccine development",
    "mRNA vaccine infectious disease",
    "vector-borne pathogens",
    "mosquito-borne viruses",
    "tick-borne disease",
    "arbovirus transmission",
    "COVID-19 variants",
    "SARS-CoV-2 immune escape",
    "H5N1 influenza",
    "avian influenza outbreaks",
    "influenza pandemic modeling",
    "global outbreak detection",
    "antiviral resistance",
    "antimicrobial resistance",
    "antibiotic stewardship",
    "nosocomial infection control",
    "hospital-acquired infections",
    "infectious disease diagnostics",
    "PCR diagnostics infectious diseases",
    "rapid antigen tests",
    "point-of-care diagnostics",
    "viral genome sequencing",
    "genomic epidemiology",
    "wastewater-based epidemiology",
    "real-time outbreak tracking",
    "zoonotic virus emergence",
    "spillover event modeling",
    "re-emerging pathogens",
    "neglected tropical diseases",
    "tuberculosis surveillance",
    "multidrug-resistant TB",
    "malaria drug resistance",
    "Plasmodium falciparum evolution",
    "vaccine efficacy field studies",
    "vaccination coverage infectious diseases",
    "maternal vaccination programs",
    "measles resurgence",
    "polio eradication strategies",
    "HIV/AIDS prevention strategies",
    "HIV drug resistance",
    "syndromic surveillance",
    "biosecurity infectious diseases",
    "bioterrorism and infectious disease",
    "viral latency and reactivation",
    "coronavirus pathogenesis",
    "novel coronavirus discovery",
    "bat virus spillover",
    "Lyme disease ecology",
    "West Nile virus outbreaks",
    "dengue virus transmission",
    "Zika virus microcephaly",
    "Chikungunya virus outbreaks",
    "Lassa fever outbreaks",
    "Ebola virus disease outbreaks",
    "Marburg virus outbreaks",
    "filovirus transmission",
    "global health infectious diseases",
    "vaccine hesitancy and outbreaks",
    "human-animal interface disease",
    "infectious disease public policy",
    "global disease burden",
    "climate change and infectious disease",
    "infectious disease in displaced populations",
    "COVID-19 long-term effects",
    "monkeypox surveillance",
    "respiratory syncytial virus RSV",
    "pneumonia global burden",
    "cholera outbreak response",
    "typhoid fever epidemiology",
    "hepatitis B vaccine coverage",
    "hepatitis C diagnostics",
    "rotavirus vaccination impact",
    "norovirus transmission modeling",
    "syphilis resurgence",
    "gonorrhea antimicrobial resistance",
    "leptospirosis outbreak detection"
    ]

QUERIES = ["test query"]

def fetch_batch(query, offset):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    
    headers = {"User-Agent": "RRID_novelty_v1"}
    params = {
        "query": query,
        "offset": offset, # where to start in the results list, specifically of the papers that come up from the query.
        "limit": 100, # how many papers to return. 
        "fields": FIELDS # metadata fields requested for each paper.
    }

    # grab the author field here and use this for H-index eventually.

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data.get("data", [])
        

def main():
    seen_ids = load_seen_ids() # get ids of previously loaded papers
    all_new_papers = [] # new papers from this batch
    for query in QUERIES:
        print(f"Starting fetch for query: '{query}'")
        for offset in range(0, MAX_RESULTS, BATCH_SIZE): # step is batch_size, so we have some maybe 1000 papers for a query and can only load batch_size numbers of papers. So we basically create a loop and have 
            # the computer sleep between requests so we dont hit the requests limit. 
            print(f"Fetching papers {offset}-{offset+BATCH_SIZE}...")

            try:
                papers = fetch_batch(query, offset)
            except Exception as e:
                print(f"Error: {e}")
                break

            new_papers = []
            for paper in papers:
                pid = paper["paperId"]
                if pid not in seen_ids and paper.get("abstract"):
                    new_papers.append(paper)
                    seen_ids.add(pid)

            if not new_papers:
                print("No new papers found. Stopping early.")
                break

            print(f"✓ Found {len(new_papers)} new papers.")
            all_new_papers.extend(new_papers)
            time.sleep(3.2)  # stay well below the rate limit
        time.sleep(10) 

    if all_new_papers:
        save_papers(all_new_papers)
        save_seen_ids(seen_ids)
        print(f"\n✅ Saved {len(all_new_papers)} new papers to {SAVE_FILE}")
    else:
        print("\n⚠️ No new papers to save.")


if __name__ == "__main__":
    main()


