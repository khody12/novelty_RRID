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

    prompt = f"""
    You are a novelty detection expert. You assess how likely a preprint paper is novel and will be a successful scientific contribution. You will estimate the novelty of papers given to you.

    Instructions:
    - Return a number from 0.00 to 1.00 that scores how novel the paper seems. 0 = not novel at all, 0.5 = average novelty, 1 = incredibly novel. 
    - Include a one-sentence explanation that incorporates your thoughts on h-index, citations, abstract, and the vector similarity sum.
    - For vector similarity, a sum around 10 to 50 means reasonably different from past papers, a sum around 100 means somewhat different, a sum greater than 150-200 means really quite different from previous papers.
    - You should prioritize papers with a large vector similarity distance sum, meaning they have very different semantic meaning than past papers.
    - Be strict: low citation count and low H-index will generally mean lower impact.
    """

     
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=prompt,
        input=input

    )
    return response.output_text
    print(response.output_text)
