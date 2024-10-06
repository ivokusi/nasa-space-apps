from constants import GROQ_API_KEY, PINECONE_API_KEY, FIREBASE_ID, BASE_URL, BASE_DOCUMENT, EMBEDDINGS, INDEX_NAME, HEADERS
from db import DB

import xml.dom.minidom
import requests

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
            "identifier": get_value(payload, 'identifier'),
            "name": get_value(payload, 'payloadName'),
            "description": get_value(payload, 'description'),
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
        "name": get_value(data, "missionName"),
        "start": get_value(data, "missionStart"),
        "end": get_value(data, "missionEnd"),
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
    
    table = data["samples"]["table"]
    header = data["samples"]["header"]
    
    columns = [h["field"] for h in header]

    rows = list()
    
    row_data = dict()
    for row in table:

        for col, val in row.items():
        
            if col in columns:
            
                if col != columns[1]:
            
                    row_data[col] = val
            
                else:
            
                    sample_name = val
        
        rows.append({sample_name: row_data})
                    
    sample_data[accession] = rows
    
def get_assay_data(data: dict, accession: str, assay_data: dict):
    
    table = data['assays'][0]['table']['table']
    header = data['assays'][0]['table']['header']
    
    columns = [h["field"] for h in header]

    rows = list()
    
    row_data = dict()
    for row in table:

        for col, val in row.items():
        
            if col in columns:
            
                if col != columns[0]:
            
                    row_data[col] = val
            
                else:
            
                    sample_name = val
        
        rows.append({sample_name: row_data})
                    
    assay_data[accession] = rows
    
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
    document_data["organism"] = organism

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

    metadata = { 
        "project_title": title,
        "accession": accession
    }

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

if __name__ == "__main__":
    
    accessions = ["OSD-665", "OSD-379", "OSD-702", "OSD-678", "OSD-718", "OSD-742", "OSD-516"]
    
    for accession in accessions:
        search(accession)
    
    # response = chatbot("Using direct reports, can you give me some intresting results found from experiments on mice.")

    #print(response)
