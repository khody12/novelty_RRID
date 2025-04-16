from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import json

# We can essentially use this code for either novelty, where we basically compare embedding
# of an incoming preprint to a database of existing preprints.
# if a preprint is the least like the other preprints in the database, we can consider that novel
# and potentially boost that in our novelty score.
# This is not necessarily sound theory, it's just something we can potentially consider

# if this approach to novelty doesn't work out well, we can use this code to make clusters
# and allow students to find similar preprints

# potentially we could also use this by looking at the top papers it matches with, and if those previous papers were quite successful
# then perhaps it implies that this one may also be successful. 

# lot to go into here.

index = faiss.read_index("semantic_scholar_data/paper_index.faiss")

with open("semantic_scholar_data/paper_metadata.json", "r") as f:
    metadata = json.load(f)

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")


# insert code to retrieve preprints from scraping part of RRID program
def find_similarity(title, abstract):
# new_title = "Machine Learning in medicine"
# new_abstract = """
# We use artificial intelligence to predict how the body will react to specific medicines.
# We train a gene network model which allows us to perform perturbation and observe
# cell state changes. 
# """
    combined = f"{title}. {abstract}"

    query_embedding = model.encode([combined]).astype("float32")

    k = 100
    D, I = index.search(query_embedding, k)

    print(f"\n🔍 Top {k} most similar papers:\n")

    sum_of_similarity = 0
    for rank, (i, dist) in enumerate(zip(I[0], D[0]), 1):
        paper = metadata[i]
        
        #print(f"[{rank}] {paper['title']}")
        sum_of_similarity += dist
        #print(f"Distance: {dist:.4f}")
        #print(f"Abstract: {paper['abstract'][:250]}...")
        
    # this sum can then be passed. 
    # we are using euclidean distance, so the larger the distance is, the farther away it is from other papers.

    # most similar pairs have a distance in range 0.1 to 0.5
    # distance around 1 means reasonably different
    #distance > 1.5/2 means really quite different. 

    return sum_of_similarity



    # idea being if top 100 end up with a sum over 100, then this paper is quite different. 
    # an additional thing to think about, if the preprint is incredibly different, then maybe it doesnt even have anything to do with 
    # infectious diseases
    # this is where i think the LLM will come in to really solve these problems and provide a check on our score. 