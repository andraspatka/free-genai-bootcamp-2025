import chromadb
from chromadb.utils import embedding_functions
import json
import os
import boto3
from typing import Dict, List, Optional


class BedrockEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_id="amazon.titan-embed-text-v2:0"):
        """Initialize Bedrock embedding function"""
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.model_id = model_id


    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Bedrock"""
        embeddings = []
        for text in texts:
            try:
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "inputText": text
                    })
                )
                response_body = json.loads(response['body'].read())
                embedding = response_body['embedding']
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding: {str(e)}")
                # Return a zero vector as fallback
                embeddings.append([0.0] * 1024)  # Titan model uses 1024 dimensions
        return embeddings


class QuestionVectorStore:
    def __init__(self, persist_directory: str = "data/vectorstore"):
        """Initialize the vector store for JLPT listening questions"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use Bedrock's Titan embedding model
        self.embedding_fn = BedrockEmbeddingFunction()
        
        
        # Create or get collections for each section type
        self.collections = {
            "exercises": self.client.get_or_create_collection(
                name="exercises",
                embedding_function=self.embedding_fn,
                metadata={"description": "Italian listening exercises transcripts"}
            )
        }


    def add_exercise(self, exercise: Dict, video_id: str):
        """Add exercise to the vector store"""
        exercise = json.loads(exercise)
            
        collection = self.collections["exercises"]
        
        ids = []
        documents = []
        metadatas = []
        
        # Create a unique ID for each exercise
        exercise_id = video_id
        ids = [exercise_id]
        
        # Store the full exercise structure as metadata
        metadatas.append({
        "video_id": video_id,
        "full_structure": json.dumps(exercise)
        })

        document = f"""
        Exercise: {exercise['transcript']}
        EnglishTranslation: {exercise['english_translation']}
        """
        documents.append(document)
        
        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )


    def search_similar_exercises(
        self, 
        query: str, 
        n_results: int = 5
    ) -> List[Dict]:
        """Search for similar exercises in the vector store"""
        collection = self.collections["exercises"]
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Convert results to more usable format
        questions = []
        for idx, metadata in enumerate(results['metadatas'][0]):
            question_data = json.loads(metadata['full_structure'])
            question_data['similarity_score'] = results['distances'][0][idx]
            questions.append(question_data)
            
        return questions


    def index_questions_file(self, filename: str):
        """Index all questions from a file into the vector store"""
        # Extract video ID from filename
        video_id = os.path.basename(filename).split('_section')[0]
        
        # Parse questions from file
        with open(filename, "r") as f:
            exercise = json.load(f)
        
        # Add to vector store
        if exercise:
            self.add_exercise(exercise, video_id)
            print(f"Indexed exercise from {filename}")


if __name__ == "__main__":
    # Example usage
    store = QuestionVectorStore()
    
    # Index questions from files
    exercise_files = [
        "data/structured/Bdu-Bm7Yno8.json",
        "data/structured/j1YL56zE7kk.json",
        "data/structured/xo2JBr0x58Q.json",
    ]
    
    for filename in exercise_files:
        if os.path.exists(filename):
            store.index_questions_file(filename)
    
    # Search for similar questions
    similar = store.search_similar_exercises("Good food", n_results=1)
    print(similar)