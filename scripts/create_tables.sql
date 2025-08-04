-- Create tables for MusicSeeker application
-- Run this script manually in Digital Ocean database console if needed

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create songs table
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    track_name VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    album VARCHAR(255),
    year INTEGER,
    date VARCHAR(50),
    lyrics TEXT NOT NULL,
    full_text TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_songs_artist_name ON songs(artist_name);
CREATE INDEX IF NOT EXISTS idx_songs_track_name ON songs(track_name);
CREATE INDEX IF NOT EXISTS idx_songs_year ON songs(year);
CREATE INDEX IF NOT EXISTS idx_songs_embedding ON songs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON TABLE songs TO your_username;
-- GRANT USAGE, SELECT ON SEQUENCE songs_id_seq TO your_username;

-- Verify table creation
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'songs' 
ORDER BY ordinal_position;
