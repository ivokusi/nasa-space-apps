import firebase_admin
from firebase_admin import credentials, firestore

class DB:
    # Static class variable to hold the Firestore client
    _db = None

    @staticmethod
    def initialize(firebase_key_path, project_id):
        """Initialize Firestore with Firebase credentials."""
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred, {
            'projectId': project_id,
        })
        DB._db = firestore.client()

    @staticmethod
    def add_document(collection_name, document_data, document_id=None):
        """Add a new document to a collection, with an optional document ID."""
        if document_id:
            doc_ref = DB._db.collection(collection_name).document(document_id)
            doc_ref.set(document_data)
            print(f"Document {document_id} added successfully.")
        else:
            DB._db.collection(collection_name).add(document_data)
            print(f"Document added successfully with auto-generated ID.")

    @staticmethod
    def get_document(collection_name, document_id):
        """Retrieve a document by its ID from a collection."""
        doc_ref = DB._db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None

    @staticmethod
    def update_document(collection_name, document_id, updates):
        """Update specific fields of a document."""
        doc_ref = DB._db.collection(collection_name).document(document_id)
        doc_ref.update(updates)
        print(f"Document {document_id} updated successfully.")

    @staticmethod
    def delete_document(collection_name, document_id):
        """Delete a document from a collection."""
        doc_ref = DB._db.collection(collection_name).document(document_id)
        doc_ref.delete()
        print(f"Document {document_id} deleted successfully.")

    @staticmethod
    def query_documents(collection_name, field, operation, value):
        """Query a collection for documents matching certain criteria."""
        collection_ref = DB._db.collection(collection_name)
        query = collection_ref.where(field, operation, value).stream()

        results = []
        for doc in query:
            results.append(doc.to_dict())
            print(f"Document {doc.id} => {doc.to_dict()}")
        
        return results

    @staticmethod
    def delete_collection(collection_name, batch_size=10):
        """Delete all documents in a collection (batch delete)."""
        coll_ref = DB._db.collection(collection_name)
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            print(f"Deleted doc {doc.id} from collection {collection_name}")
            deleted += 1
        if deleted >= batch_size:
            return DB.delete_collection(collection_name, batch_size)

