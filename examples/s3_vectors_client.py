#!/usr/bin/env python3
"""S3 Vectors client implementation example."""

import boto3
import json
import numpy as np
from typing import List, Dict, Any, Tuple

class S3VectorsClient:
    """Client for S3-based vector similarity search."""
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1', profile_name: str = None):
        """Initialize S3 Vectors client."""
        session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.s3 = session.client('s3', region_name=region)
        self.bucket_name = bucket_name
        
    def insert_vector(self, vector_id: str, vector: List[float], metadata: Dict[str, Any] = None) -> bool:
        """Insert a vector with metadata into S3."""
        try:
            key = f"vectors/{vector_id}.json"
            data = {
                'id': vector_id,
                'vector': vector,
                'metadata': metadata or {}
            }
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            return True
        except Exception as e:
            print(f"Error inserting vector {vector_id}: {e}")
            return False
    
    def batch_insert_vectors(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> int:
        """Batch insert multiple vectors."""
        success_count = 0
        for vector_id, vector, metadata in vectors:
            if self.insert_vector(vector_id, vector, metadata):
                success_count += 1
        return success_count
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search_similar_vectors(self, query_vector: List[float], k: int = 10, 
                             prefix: str = "vectors/") -> List[Dict[str, Any]]:
        """Search for k most similar vectors."""
        try:
            # List all vector objects
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            
            if 'Contents' not in response:
                return []
            
            similarities = []
            
            # Calculate similarity for each vector
            for obj in response['Contents']:
                try:
                    # Get vector data
                    vector_obj = self.s3.get_object(Bucket=self.bucket_name, Key=obj['Key'])
                    vector_data = json.loads(vector_obj['Body'].read())
                    
                    # Calculate similarity
                    similarity = self.cosine_similarity(query_vector, vector_data['vector'])
                    
                    similarities.append({
                        'id': vector_data['id'],
                        'similarity': similarity,
                        'metadata': vector_data.get('metadata', {}),
                        'vector': vector_data['vector']
                    })
                    
                except Exception as e:
                    print(f"Error processing {obj['Key']}: {e}")
                    continue
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:k]
            
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from S3."""
        try:
            key = f"vectors/{vector_id}.json"
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(f"Error deleting vector {vector_id}: {e}")
            return False
    
    def get_vector(self, vector_id: str) -> Dict[str, Any]:
        """Retrieve a specific vector by ID."""
        try:
            key = f"vectors/{vector_id}.json"
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(response['Body'].read())
        except Exception as e:
            print(f"Error retrieving vector {vector_id}: {e}")
            return None
    
    def list_vectors(self, prefix: str = "vectors/", max_keys: int = 1000) -> List[str]:
        """List all vector IDs in the bucket."""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name, 
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' not in response:
                return []
            
            vector_ids = []
            for obj in response['Contents']:
                # Extract vector ID from key
                key = obj['Key']
                if key.endswith('.json'):
                    vector_id = key.replace(prefix, '').replace('.json', '')
                    vector_ids.append(vector_id)
            
            return vector_ids
            
        except Exception as e:
            print(f"Error listing vectors: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = S3VectorsClient(
        bucket_name='your-vector-bucket',
        region='us-east-1',
        profile_name='your-aws-profile'  # Optional
    )
    
    # Example vectors (384-dimensional for demonstration)
    sample_vectors = [
        ("doc_001", [0.1] * 384, {"title": "Document 1", "category": "tech"}),
        ("doc_002", [0.2] * 384, {"title": "Document 2", "category": "science"}),
        ("doc_003", [0.3] * 384, {"title": "Document 3", "category": "tech"}),
    ]
    
    # Batch insert vectors
    print("Inserting sample vectors...")
    success_count = client.batch_insert_vectors(sample_vectors)
    print(f"Successfully inserted {success_count} vectors")
    
    # Search for similar vectors
    query_vector = [0.15] * 384
    print("\nSearching for similar vectors...")
    results = client.search_similar_vectors(query_vector, k=5)
    
    print(f"Found {len(results)} similar vectors:")
    for result in results:
        print(f"  ID: {result['id']}, Similarity: {result['similarity']:.4f}")
        print(f"  Metadata: {result['metadata']}")
    
    # List all vectors
    print(f"\nAll vectors in bucket:")
    vector_ids = client.list_vectors()
    for vid in vector_ids:
        print(f"  {vid}")
