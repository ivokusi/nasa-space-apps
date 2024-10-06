from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
FIREBASE_ID = os.getenv("FIREBASE_ID")

BASE_URL = "https://osdr.nasa.gov/geode-py/ws/repo/studies/{id}"

BASE_DOCUMENT = """
<CONTENT>
    <ACCESSION>
        {accession}
    </ACCESSION>
    <DESCRIPTION>
        {description}
    </DESCRIPTION>
    <FACTORS>
        {factors}
    </FACTORS>
    <ORGANISM>
        {organism}
    </ORGANISM>
    <PROJECT>
        {project}
    </PROJECT>
    <COLLABORATORS>
        {collaborators}
    </COLLABORATORS>
    <PAYLOAD>
        {payload}
    </PAYLOAD>
    <MISSIONS>
        {mission}
    </MISSIONS>
    <PROTOCOLS>
        {protocols}
    </PROTOCOLS>
</CONTENT>
"""

EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

INDEX_NAME = "space-apps"

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}
