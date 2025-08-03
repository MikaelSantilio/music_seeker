#!/usr/bin/env python3
"""
Simple test script for embedding generation
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_embedding():
    """Test basic embedding generation"""
    try:
        # Initialize client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test embedding generation
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="Test song lyrics for embedding generation",
            dimensions=1536
        )
        
        embedding = response.data[0].embedding
        print(f"✅ Embedding generated successfully!")
        print(f"   Dimensions: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI embedding generation...")
    test_embedding()
