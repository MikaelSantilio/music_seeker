#!/usr/bin/env python3
"""
Debug script para testar a busca semântica
"""

import os
import sys
import requests
import json
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.database import SessionLocal
from app.services.embedding_service import EmbeddingService

def test_embedding_generation():
    """Test if embedding generation is working"""
    print("=== Testing Embedding Generation ===")
    
    try:
        service = EmbeddingService()
        embedding = service.generate_query_embedding("love")
        print(f"✅ Embedding generated successfully: {len(embedding)} dimensions")
        print(f"First 5 values: {embedding[:5]}")
        return embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None

def test_database_query(query_embedding):
    """Test direct database query"""
    print("\n=== Testing Database Query ===")
    
    if not query_embedding:
        print("❌ No embedding to test with")
        return
    
    try:
        db = SessionLocal()
        
        # Convert embedding to string format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Test simple query without similarity
        print("Testing basic query...")
        result = db.execute(text("SELECT COUNT(*) as count FROM songs WHERE embedding IS NOT NULL"))
        count = result.fetchone().count
        print(f"✅ Found {count} songs with embeddings")
        
        # Test similarity query
        print("Testing similarity query...")
        sql_query = f"""
            SELECT id, track_name, artist_name, 
                   (1 - (embedding <=> '{embedding_str}'::vector)) as similarity_score
            FROM songs 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT 3
        """
        
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        
        print(f"✅ Similarity query returned {len(rows)} results:")
        for row in rows:
            print(f"  - {row.track_name} by {row.artist_name} (similarity: {row.similarity_score:.4f})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database query error: {e}")

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("\n=== Testing API Endpoint ===")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/search",
            headers={"Content-Type": "application/json"},
            json={"query": "love", "limit": 3},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {len(data.get('results', []))} results")
            print(f"Query: {data.get('query')}")
            print(f"Processing time: {data.get('processing_time_ms')}ms")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ API request error: {e}")

if __name__ == "__main__":
    print("🔍 MusicSeeker Debug Tool\n")
    
    # Test embedding generation
    embedding = test_embedding_generation()
    
    # Test database query
    test_database_query(embedding)
    
    # Test API endpoint
    test_api_endpoint()
