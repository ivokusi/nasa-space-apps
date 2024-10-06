from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from db import DB
import os

app = Flask(__name__)
CORS(app)

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
    
if __name__ == '__main__':
    app.run(debug=True)
