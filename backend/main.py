from constants import GROQ_API_KEY, PINECONE_API_KEY, FIREBASE_ID, BASE_URL, BASE_DOCUMENT, EMBEDDINGS, INDEX_NAME, HEADERS
from db import DB

import xml.dom.minidom
import requests

from sentence_transformers import SentenceTransformer
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from pinecone import Pinecone
from groq import Groq

DB.initialize("../firebase_config.json", FIREBASE_ID)
pc = Pinecone(api_key=PINECONE_API_KEY)
groq = Groq(api_key=GROQ_API_KEY)

def get_value(data: dict, key: str, default="N/A") -> str:
    
    value = data.get(key)
    
    if not value:
        value = default
    
    return value

def get_json(id: str) -> dict:
    
    """
    Retrieve JSON data for a given ID.
    """
    
    url = BASE_URL.format(id=id)
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        
        return response.json()

def format_factors(data: dict, document_data: dict) -> list:
    
    """
    Format the 'factors' section of the data.
    """
    
    document_data["factors"] = []
    factors = data.get("factors", [])
    
    text = ""
    for factor in factors:
    
        factor_name = get_value(factor, "factorName")
        text += f"{factor_name}\n"
    
        document_data["factors"].append(factor_name)
    
    return text.split()

def format_project(data: dict, document_data: dict) -> list:
    
    """
    Format the 'project' section of the data.
    """
    
    document_data["project"] = {}
    
    project_info = {
        "Project Title": get_value(data, "projectTitle"),
        "Project Type": get_value(data, "projectType"),
        "Flight Program": get_value(data, "flightProgram"),
        "Experiment Platform": get_value(data, "experimentPlatform"),
        "Sponsoring Agency": get_value(data, "spaceProgram"),
        "NASA Center": get_value(data, "managingNasaCenter"),
        "Funding Source": get_value(data, "funding"),
    }
    
    text = ""
    for key, value in project_info.items():
    
        text += f"{key}: {value}\n"
        document_data["project"][key] = value
    
    return text.split()

def format_collaborators(data: dict, document_data: dict) -> str:
    
    """
    Format the 'collaborators' section of the data.
    """
    
    document_data["collaborators"] = []
    collaborators = data.get("contacts", [])
    
    collaborators_text = ""
    for collaborator in collaborators:
    
        first_name = get_value(collaborator, "firstName")
        last_name = get_value(collaborator, "lastName")
        email = get_value(collaborator, "email")
        affiliation = get_value(collaborator, "affiliation")
        roles = collaborator.get("roles", [])
        role = roles[0].get("annotationValue") or "N/A" if roles else "N/A"

        document_data["collaborators"].append({
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "affiliation": affiliation,
            "role": role,
        })

        collaborators_text += f"""
<Name>
    {first_name} {last_name}
</Name>
<Email>
    {email}
</Email>
<Affiliation>
    {affiliation}
</Affiliation>
<Role>
    {role}
</Role>
"""

    return collaborators_text.strip()

def format_payload(data: dict, document_data: dict) -> list:
   
    """
    Format the 'payload' section of the data.
    """
   
    document_data["payload"] = {}
    payloads = data.get("payloads", [])
   
    if payloads:
        
        payload = payloads[0]
        
        payload_info = {
            "Identifier": get_value(payload, 'identifier'),
            "Name": get_value(payload, 'payloadName'),
            "Description": get_value(payload, 'description'),
        }
        
        text = ""
        for key, value in payload_info.items():
        
            text += f"{key}: {value}\n"        
            document_data["payload"][key] = value

        return text.split()

def format_mission(data: dict, document_data: dict) -> list:
   
    """
    Format the 'mission' section of the data
    """
   
    document_data["mission"] = {}
   
    mission_info = {
        "Name": get_value(data, "missionName"),
        "Start": get_value(data, "missionStart"),
        "End": get_value(data, "missionEnd"),
    }
   
    text = ""
   
    for key, value in mission_info.items():
   
        text += f"{key}: {value}\n"
        document_data["mission"][key] = value
   
    return text.split()

def format_protocols(data: dict, document_data: dict) -> str:
    
    """
    Format the 'protocols' section of the data.
    """
    
    document_data["protocols"] = []
    protocols = data.get("protocols", [])
    
    protocols_text = ""
    for protocol in protocols:
    
        name = get_value(protocol, "name")
        description = get_value(protocol, "description")

        document_data["protocols"].append({ 
            "name": name,
            "description": description 
        })

        protocols_text += f"""
<Protocol>
    <Name>{name}</Name>
    <Description>{description}</Description>
</Protocol>
"""
    
    return protocols_text.strip()

def get_sample_data(data: dict, accession: str, sample_data: dict):
    
    table = data['samples'][0]['table']['table']
    header = data['samples'][0]['table']['header']
    
    sample_name = table.get("Sample Name", "Unknown Sample")
    col_vals =[h['title'] for h in header]
    
    row_data = { col: val for col, val in table.items() if col != "Sample Name" and col in col_vals }

    sample_data[accession] = {
        sample_name: row_data
    }
    
def get_assay_data(data: dict, accession: str, assay_data: dict):
    
    toread_assay = data['assays'][0]['table']['table']
    header = data['assays'][0]['table']['header']
    
    sample_name = toread_assay.get("Sample Name", "Unknown Sample")
    col_vals =[h['title'] for h in header]
    
    row_data = { col: val for col, val in toread_assay.items() if col != "Sample Name" and col in col_vals }

    assay_data[accession] = {
        sample_name: row_data
    }
    
def create_document(data: dict) -> tuple:
    
    """
    Create the document by populating the BASE_DOCUMENT template with formatted data.
    """
    
    document_data = dict()

    title = get_value(data, "title", "Untitled")
    document_data["title"] = title

    accession = get_value(data, "accession")
    document_data["accession"] = accession

    description = get_value(data, "description", "No description available.")
    document_data["description"] = description

    factors = format_factors(data, document_data)
    organism_links = data.get("organisms", {}).get("links", {})
    organism = next(iter(organism_links.keys()), "N/A")

    project = format_project(data, document_data)
    collaborators = format_collaborators(data, document_data)
    payload = format_payload(data, document_data)
    mission = format_mission(data, document_data)
    protocols = format_protocols(data, document_data)

    DB.add_document("Project", document_data, accession)

    sample_data = dict()
    assay_data = dict()

    get_sample_data(data, accession, sample_data)
    get_assay_data(data, accession, assay_data)

    DB.add_document("Sample", sample_data, accession)
    DB.add_document("Assay", assay_data, accession)

    metadata = { "project_title": title }

    document = BASE_DOCUMENT.format(
        accession=accession,
        description=description,
        factors=factors,
        organism=organism,
        project=project,
        collaborators=collaborators,
        payload=payload,
        mission=mission,
        protocols=protocols,
    )

    dom = xml.dom.minidom.parseString(document)
    pretty_document = dom.toprettyxml(indent="\t")

    return metadata, pretty_document

def add(accession: str):
    
    data = get_json(accession)

    PineconeVectorStore(index_name=INDEX_NAME, embedding=EMBEDDINGS)
    metadata, page_content = create_document(data)

    document = Document(
        page_content=page_content,
        metadata=metadata
    )

    PineconeVectorStore.from_documents(
        [document],
        EMBEDDINGS,
        index_name=INDEX_NAME
    )

def search(accession: str):

    document = DB.get_document("Project", accession)
   
    if document is None:
   
        add(accession)

        return DB.get_document("Project", accession)
   
    else: 
        
        return document

def get_huggingface_embeddings(text, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(text)

def chatbot(query):

    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    pc_index = pinecone.Index(INDEX_NAME)

    raw_query_embedding = get_huggingface_embeddings(query)

    top_matches = pc_index.query(vector=raw_query_embedding.tolist(), top_k=4, include_metadata=True)
    contexts = [item['metadata']['text'] for item in top_matches['matches']]

    augmented_query = "\n" + "\n\n-------\n\n".join(contexts[:10]) + "\n-------\n\n\n\n\nMY QUESTION:\n" + query

    system_prompt = f"""
    You are a science expert. More specifically, your concentration includes science experiments on space. 

    I am a scientists myself as well. However, I don't have expertise in experiments run on an outer space setting. 

    I want you to answer as if you were having a conversation with me, a scientist. 

    Always consider all of the context provided when forming your response. 
    """

    groq_client = Groq(api_key=GROQ_API_KEY)

    llm_response = groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": augmented_query}
        ]
    )

    response = llm_response.choices[0].message.content
    
    return response

if __name__ == "__main__":
    
    accessions = ["OSD-665", "OSD-379"]
    
    for accession in accessions:
        search(accession)
    
    # response = chatbot("Using direct reports, can you give me some intresting results found from experiments on mice.")

    #print(response)
