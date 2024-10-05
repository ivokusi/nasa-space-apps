import requests
import json
import re

from db import DB

DB.initialize("../firebase_config.json", "spaceapps-b7fd1")

BASE_URL = "https://osdr.nasa.gov/geode-py/ws/repo/studies/{id}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

def get_json(id: str) -> json:

    url = BASE_URL.format(id=id)
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
    
    return data

def store_json(data: json, file: str):

    accession = data["accession"]
       
    title = data["title"]
    description = data["description"]

    factors = data["factors"]
    for factor in factors:
        print(factor["factorName"])

    organism = list(data["organisms"]["links"].keys())[0]

    projectTitle = data["projectTitle"]
    projectType = data["projectType"]
    flightProgram = data["flightProgram"]
    experimentPlatform = data["experimentPlatform"]
    spaceProgram = data["spaceProgram"]
    managingNasaCenter = data["managingNasaCenter"]
    funding = data["funding"]

    collaborators = data["contacts"]
    for collaborator in collaborators:
        
        firstName = collaborator["firstName"]
        lastName = collaborator["lastName"]

        email = collaborator["email"]

        affiliation = collaborator["affiliation"]
        role = collaborator["roles"][0]["annotationValue"]

        print(firstName, lastName, email, affiliation, role)

    payloadIdentifier = data["payloads"][0]["identifier"]
    payloadName = data["payloads"][0]["payloadName"]
    payloadDescription = data["payloads"][0]["description"]

    missionName = data["missionName"]
    missionStart = data["missionStart"]
    missionEnd = data["missionEnd"]

    protocols = data["protocols"]
    for protocol in protocols:

        protocolDescription = protocol["description"]
        protocolName = protocol["name"]
        
def new_entry(id: str):

    file = f"{id}.txt"
    FileManager.create_file(file)

    data = get_json(id)
    store_json(data, file)

new_entry("OSD-379")