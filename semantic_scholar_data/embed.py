from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

import json

with open("papers.json", "r") as f:
    papers = json.load(f)

texts = []
metadata = []
for paper in papers:
    title = paper.get("title", "") # .get (key, default)
    abstract = paper.get("abstract", "")
    if title and abstract:
        combined = f"{title}, {abstract}"  
        texts.append(combined)
        metadata.append({
            "paperId": paper.get("paperId", ""),
            "title": title,
            "abstract": abstract
        })
with open("paper_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

embeddings = model.encode(texts, show_progress_bar=True) # encode everything within papers.json. 

embeddings = np.array(embeddings).astype("float32") # faiss requires float32

index = faiss.IndexFlatL2(embeddings.shape[1])

index.add(embeddings)

print(f"Indexed {index.ntotal} papers.")


faiss.write_index(index, "paper_index.faiss")
print("Saved FAISS index to disk.")



    