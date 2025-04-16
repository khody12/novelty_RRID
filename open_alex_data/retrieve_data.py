import requests
import json
import time
import os

BATCH_SIZE = 100
SAVE_FILE = "openalex_papers.json"
SEEN_FILE = "openalex_seen_ids.json"
FIELDS = "id,title,abstract_inverted_index,authorships,publication_year,cited_by_count"

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
# DECODE ABSTRACT
def decode_abstract(inverted_index):
    if not inverted_index:
        return ""
    # Find max position
    max_index = max(pos for positions in inverted_index.values() for pos in positions)
    # Initialize list of empty tokens
    abstract_words = [None] * (max_index + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            abstract_words[pos] = word
    return " ".join(word if word is not None else "" for word in abstract_words)
def get_author_hindex(author_id):
    url = f"https://api.openalex.org/authors/{author_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return data.get("summary_stats", {}).get("h_index")
# 
def fetch_openalex_papers(query, per_page=100, max_results=500):
    results = []
    seen_ids = load_seen_ids()
    cursor = "*"
    url = "https://api.openalex.org/works"

    while len(results) < max_results:
        params = {
            "filter": f"title.search:{query}",
            "per-page": per_page,
            "cursor": cursor,
            "mailto": "eric_khodorenko@berkeley.edu",  # required by OpenAlex
            "select": "id,title,abstract_inverted_index,publication_year,cited_by_count,authorships"
        }
        r = requests.get(url, params=params)
        data = r.json()

        for result in data["results"]:
            if result["id"] in seen_ids:
                continue
            seen_ids.add(result["id"])

            # decode abstract
            abstract_index = result.get("abstract_inverted_index")
            result["abstract_text"] = decode_abstract(abstract_index)

            # Get first author's H-index
            authorships = result.get("authorships", [])
            if authorships:
                first_author = authorships[0].get("author", {})
                author_id = first_author.get("id", "").replace("https://openalex.org/", "")
                h_index = get_author_hindex(author_id)
            else:
                h_index = None

            result["first_author_h_index"] = h_index
            # get rid of the inverted index and replace it with abstract text.
            filtered_result = {
                "id": result.get("id"),
                "title": result.get("title"),
                "abstract_text": result.get("abstract_text"),
                "publication_year": result.get("publication_year"),
                "cited_by_count": result.get("cited_by_count"),
                "first_author_h_index": h_index
            }


            results.append(filtered_result)
            if len(results) >= max_results:
                break

        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(1)  # respect rate limits

    save_seen_ids(seen_ids)
    save_papers(results)
    return results


if __name__ == "__main__":
    for QUERY in QUERIES:
        papers = fetch_openalex_papers("infectious disease", max_results=100)
        print(f"Fetched {len(papers)} new papers.")