from constants import GROQ_API_KEY, PINECONE_API_KEY, INDEX_NAME

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from groq import Groq

pc = Pinecone(api_key=PINECONE_API_KEY)
groq = Groq(api_key=GROQ_API_KEY)

def get_huggingface_embeddings(text, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(text)

def chatbot(query):

    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    pc_index = pinecone.Index(INDEX_NAME)

    raw_query_embedding = get_huggingface_embeddings(query)

    top_matches = pc_index.query(vector=raw_query_embedding.tolist(), top_k=3, include_metadata=True)
    contexts = [item['metadata']['text'] for item in top_matches['matches']]

    augmented_query = "\n" + "\n\n-------\n\n".join(contexts[:10]) + "\n-------\n\n\n\n\nMY QUESTION:\n" + query

    system_prompt = f"""
    You are a science expert. More specifically, your concentration includes science experiments on space. 

    I am a scientists myself as well. However, I don't have expertise in experiments run on an outer space setting. 

    Always consider all of the context provided when forming your response. 
    
    Limit your response to 250 words.

    When responding format your response in bullet points (use newlines if needed).

    I want you to answer as if you were having a CONVERSATION with me, a scientist. 
    
    Also refrain from saying given the information provided or any such expression.  
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

def chatbot_specific(query, table, accession):

    pinecone = Pinecone(api_key=PINECONE_API_KEY)
    pc_index = pinecone.Index(INDEX_NAME)

    embedding_dim = 384  # Replace with the actual dimension of your index
    dummy_vector = [0] * embedding_dim

    metadata_filter = {
        "accession": accession
    }

    # Perform the query with the metadata filter
    response = pc_index.query(
        vector=dummy_vector,     
        filter=metadata_filter,    
        top_k=1,
        include_metadata=True            
    )

    contexts = response["matches"][0]['metadata']['text']

    augmented_query = contexts + table + "\n\n\n\nMY QUESTION:\n" + query

    print(len(augmented_query))

    system_prompt = f"""
    You are a science expert. More specifically, your concentration includes science experiments on space. 

    I am a scientists myself as well. However, I don't have expertise in experiments run on an outer space setting. 

    Always consider all of the context and table provided when forming your response.
    
    Limit your response to 250 words.

    When responding format your response in bullet points (use newlines if needed).

    I want you to answer as if you were having a CONVERSATION with me, a scientist. 
    
    Also refrain from saying given the information provided or any such expression.  
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
