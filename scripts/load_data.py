"""
Data loading and preprocessing script for MusicSeeker

This script loads all CSV files from data/lyrics/ directory, 
cleans and normalizes the text data, and loads it into PostgreSQL.
"""

import os
import sys
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict
from sqlalchemy.orm import Session

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal, create_tables, engine
from app.models.song import Song


def clean_text(text: str) -> str:
    """
    Clean and normalize text data
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to UTF-8 and normalize
    text = str(text).encode('utf-8', errors='ignore').decode('utf-8')
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.,!?;:\-\'\"()]', ' ', text)
    
    # Remove multiple spaces again
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text


def create_full_text(track_name: str, artist_name: str, lyrics: str) -> str:
    """
    Create combined full text field for better semantic search
    
    Args:
        track_name: Song title
        artist_name: Artist name
        lyrics: Song lyrics
        
    Returns:
        Combined text string
    """
    # Clean individual components
    clean_track = clean_text(track_name)
    clean_artist = clean_text(artist_name)
    clean_lyrics = clean_text(lyrics)
    
    # Combine with clear separators for better embedding
    full_text = f"Title: {clean_track}. Artist: {clean_artist}. Lyrics: {clean_lyrics}"
    
    return full_text


def load_csv_files(data_dir: str = "data/lyrics") -> pd.DataFrame:
    """
    Load and combine all CSV files from the data directory
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Combined DataFrame with all songs
    """
    data_path = Path(data_dir)
    csv_files = list(data_path.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    all_dataframes = []
    
    for csv_file in csv_files:
        print(f"Loading {csv_file.name}...")
        try:
            df = pd.read_csv(csv_file)
            
            # Validate required columns
            required_columns = ['Artist', 'Title', 'Lyric']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Warning: {csv_file.name} missing columns: {missing_columns}")
                continue
            
            # Add source file for tracking
            df['source_file'] = csv_file.stem
            all_dataframes.append(df)
            print(f"Loaded {len(df)} songs from {csv_file.name}")
            
        except Exception as e:
            print(f"Error loading {csv_file.name}: {e}")
            continue
    
    if not all_dataframes:
        raise ValueError("No valid CSV files could be loaded")
    
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"\nTotal songs loaded: {len(combined_df)}")
    
    return combined_df


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the combined dataframe
    
    Args:
        df: Raw combined dataframe
        
    Returns:
        Preprocessed dataframe
    """
    print("Preprocessing data...")
    
    # Map columns to our schema
    df_processed = df.rename(columns={
        'Artist': 'artist_name',
        'Title': 'track_name',
        'Lyric': 'lyrics',
        'Album': 'album',
        'Year': 'year',
        'Date': 'date'
    }).copy()
    
    # Fill missing values
    df_processed['album'] = df_processed.get('album', '').fillna('Unknown')
    df_processed['year'] = df_processed.get('year', None)
    df_processed['date'] = df_processed.get('date', '').fillna('')
    
    # Clean text fields
    print("Cleaning text data...")
    df_processed['track_name'] = df_processed['track_name'].apply(clean_text)
    df_processed['artist_name'] = df_processed['artist_name'].apply(clean_text)
    df_processed['lyrics'] = df_processed['lyrics'].apply(clean_text)
    
    # Create full_text field
    print("Creating full_text field...")
    df_processed['full_text'] = df_processed.apply(
        lambda row: create_full_text(row['track_name'], row['artist_name'], row['lyrics']),
        axis=1
    )
    
    # Remove duplicates based on track_name + artist_name
    print("Removing duplicates...")
    before_dedup = len(df_processed)
    df_processed = df_processed.drop_duplicates(subset=['track_name', 'artist_name'], keep='first')
    after_dedup = len(df_processed)
    print(f"Removed {before_dedup - after_dedup} duplicate songs")
    
    # Filter out rows with empty essential fields
    df_processed = df_processed[
        (df_processed['track_name'].str.len() > 0) &
        (df_processed['artist_name'].str.len() > 0) &
        (df_processed['lyrics'].str.len() > 10)  # At least 10 characters in lyrics
    ]
    
    print(f"Final dataset size: {len(df_processed)} songs")
    return df_processed


def save_to_database(df: pd.DataFrame, batch_size: int = 100) -> None:
    """
    Save preprocessed data to PostgreSQL database
    
    Args:
        df: Preprocessed dataframe
        batch_size: Number of records to insert per batch
    """
    print("Saving to database...")
    
    # Create tables if they don't exist
    create_tables()
    
    db: Session = SessionLocal()
    
    try:
        # Clear existing data (optional - remove if you want to append)
        print("Clearing existing songs...")
        db.query(Song).delete()
        db.commit()
        
        total_songs = len(df)
        songs_created = 0
        
        # Process in batches
        for i in range(0, total_songs, batch_size):
            batch = df.iloc[i:i + batch_size]
            
            song_objects = []
            for _, row in batch.iterrows():
                song = Song(
                    track_name=row['track_name'],
                    artist_name=row['artist_name'],
                    album=row.get('album', 'Unknown'),
                    year=int(row['year']) if pd.notna(row.get('year')) else None,
                    date=row.get('date', ''),
                    lyrics=row['lyrics'],
                    full_text=row['full_text']
                )
                song_objects.append(song)
            
            # Bulk insert batch
            db.bulk_save_objects(song_objects)
            db.commit()
            
            songs_created += len(song_objects)
            print(f"Saved batch {i//batch_size + 1}: {songs_created}/{total_songs} songs")
        
        print(f"Successfully saved {songs_created} songs to database!")
        
    except Exception as e:
        db.rollback()
        print(f"Error saving to database: {e}")
        raise
    finally:
        db.close()


def main():
    """
    Main function to execute the data loading pipeline
    """
    try:
        print("=== MusicSeeker Data Loading Pipeline ===\n")
        
        # Load CSV files
        df_raw = load_csv_files()
        
        # Preprocess data
        df_processed = preprocess_dataframe(df_raw)
        
        # Save to database
        save_to_database(df_processed)
        
        print("\n=== Data loading completed successfully! ===")
        print(f"Total songs in database: {len(df_processed)}")
        
        # Show sample statistics
        print("\nDataset statistics:")
        print(f"- Unique artists: {df_processed['artist_name'].nunique()}")
        print(f"- Year range: {df_processed['year'].min()} - {df_processed['year'].max()}")
        print(f"- Average lyrics length: {df_processed['lyrics'].str.len().mean():.0f} characters")
        
    except Exception as e:
        print(f"Error in data loading pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
