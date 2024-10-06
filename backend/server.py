from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
import os

from chatbot import chatbot, chatbot_specific
from db import DB

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

load_dotenv()

FIREBASE_KEY_PATH = "../firebase_config.json"
FIREBASE_ID = os.getenv("FIREBASE_ID")

DB.initialize(FIREBASE_KEY_PATH, FIREBASE_ID)

@app.route('/api/<collection_name>', methods=['POST'])
def add_document(collection_name):
    document_data = request.json
    document_id = document_data.get('id')  # Optional custom ID
    if document_data:
        if document_id:
            DB.add_document(collection_name, document_data, document_id)
            return jsonify({'message': f'Document {document_id} added successfully.'}), 201
        else:
            DB.add_document(collection_name, document_data)
            return jsonify({'message': 'Document added successfully with auto-generated ID.'}), 201
    else:
        return jsonify({'error': 'No data provided.'}), 400

@app.route('/api/<collection_name>/<document_id>', methods=['GET'])
def get_document(collection_name, document_id):
    data = DB.get_document(collection_name, document_id)
    if data:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Document not found'}), 404

@app.route('/api/<collection_name>/<document_id>', methods=['PUT'])
def update_document(collection_name, document_id):
    updates = request.json
    if updates:
        try:
            DB.update_document(collection_name, document_id, updates)
            return jsonify({'message': f'Document {document_id} updated successfully.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'error': 'No update data provided.'}), 400

@app.route('/api/<collection_name>/<document_id>', methods=['DELETE'])
def delete_document(collection_name, document_id):
    try:
        DB.delete_document(collection_name, document_id)
        return jsonify({'message': f'Document {document_id} deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/<collection_name>/query', methods=['GET'])
def query_documents(collection_name):
    field = request.args.get('field')
    operation = request.args.get('operation', '==')
    value = request.args.get('value')

    if field and value:
        results = DB.query_documents(collection_name, field, operation, value)
        return jsonify(results), 200
    else:
        return jsonify({'error': 'Field and value query parameters are required.'}), 400
    
@app.route('/api/<collection_name>/all', methods=['GET'])
def get_all_documents(collection_name):
    
    try:
        
        documents = DB.get_all_documents(collection_name)

        data = list()
        for document in documents:

            row = dict()
            
            row["accession"] = document["accession"]
            row["title"] = document["title"]
            row["organism"] = document["organism"]
            row["slug"] = document["accession"]

            data.append(row)

        return data, 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    user_input = data['message']
    print(user_input)
    try:
        bot_response = chatbot(user_input)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while processing your message.'}), 500
    return jsonify({'response': bot_response}), 200

@app.route('/api/chatbot/project', methods=['POST'])
def chatbot_project_api():
    
    data = request.get_json()
    print(data)
    
    table = data["data"]
    percent = data["percent"]
    accession = data["accession"]
    query = data["query"]

    table_text = ""
    for row in table:
        table_text += f"{row["name"]}: {row["value"]}{"%" if percent else ""}\n"
    
    table_text.strip()
    table_text = "<DATA VISUAL>\n" + table_text + "\n</DATA VISUA>"

    try:
         bot_response = chatbot_specific(query, table_text, accession)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while processing your message.'}), 500
    
    return jsonify({'response': bot_response}), 200


if __name__ == '__main__':
    app.run(debug=True)
