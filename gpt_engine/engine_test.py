import openai
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import sys
# retrieve preprints here.
load_dotenv()
#test 
def generate_novelty(paper_info):
    test_paper_info = {
        "title": "Measuring outbreak-detection performance by using controlled feature set simulations.",
        "abstract": "INTRODUCTION\nThe outbreak-detection performance of a syndromic surveillance system can be measured in terms of its ability to detect signal (i.e., disease outbreak) against background noise (i.e., normally varying baseline disease in the region). Such benchmarking requires training and the use of validation data sets. Because only a limited number of persons have been infected with agents of biologic terrorism, data are generally unavailable, and simulation is necessary. An approach for evaluation of outbreak-detection algorithms was developed that uses semisynthetic data sets to provide real background (which effectively becomes the noise in the signal-to-noise problem) with artificially injected signal. The injected signal is defined by a controlled feature set of variable parameters, including size, shape, and duration.\n\n\nOBJECTIVES\nThis report defines a flexible approach to evaluating public health surveillance systems for early detection of outbreaks and provides examples of its use.\n\n\nMETHODS\nThe stages of outbreak detection are described, followed by the procedure for creating data sets for benchmarking performance. Approaches to setting parameters for simulated outbreaks by using controlled feature sets are detailed, and metrics for detection performance are proposed. Finally, a series of experiments using semisynthetic data sets with artificially introduced outbreaks defined with controlled feature sets is reviewed.\n\n\nRESULTS\nThese experiments indicate the flexibility of controlled feature set simulation for evaluating outbreak-detection sensitivity and specificity, optimizing attributes of detection algorithms (e.g., temporal windows), choosing approaches to syndrome groupings, and determining best strategies for integrating data from multiple sources.\n\n\nCONCLUSIONS\nThe use of semisynthetic data sets containing authentic baseline and simulated outbreaks defined by a controlled feature set provides a valuable means for benchmarking the detection performance of syndromic surveillance systems.",
        "h-index": 26,
        "citations": 100,
        "date_published" : "2025-01-15"
    }
    #input = json.dumps(test_paper_info, indent=2)

    input = json.dumps(paper_info, indent=2)   
    print(input) 

    

    prompt = f"""
    You are a novelty detection expert tasked with evaluating how novel and impactful a scientific preprint is. Your assessment should emphasize both the uniqueness of the paper’s content and the scientific credibility of its authors.

    Instructions:
    - Return a number from 0.00 to 1.00 representing the novelty of the paper. 
        - 0.00 = not novel at all
        - 0.50 = moderately novel
        - 1.00 = extremely novel and potentially field-shifting
    - Your score **must be heavily influenced** by the following:
        1. **Vector Similarity Sum**: This quantifies how different the paper’s abstract and title are from previously published works. 
            - A sum of 10–50 implies moderate novelty.
            - A sum of 100 implies noticeable difference.
            - A sum above 150–200 implies strong semantic divergence and likely high novelty.
        2. **Author H-Index and Citation Count**: High H-index and citation counts suggest credible authorship and greater potential impact. Low values should result in a more skeptical rating unless offset by very high semantic uniqueness.
        3. **Abstract & Title**: These should reflect originality, clear scientific value, and potential for contribution to the field.

    - Provide a **brief explanation sentence** that references vector similarity, H-index, citation count, and abstract content. Make it clear how each factor influenced your decision.

    - Be strict. If vector similarity is low and author metrics are weak, give a low score—even if the abstract seems promising.
    """

     
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=prompt,
        input=input

    )
    return response.output_text
