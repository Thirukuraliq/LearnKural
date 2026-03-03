import os
import pandas as pd
from elevenlabs.client import ElevenLabs
import argparse
import time

from elevenlabs import VoiceSettings

# Configuration
API_KEY = "sk_efe945501fc4a2ba48efb6686082cf84dcf30394017cd8c7"
# Maneesh - Upbeat, Professional & Friendly
VOICE_ID = "pTM0m0egrCpo5i9b1gpo" 
MODEL_ID = "eleven_v3"
OUTPUT_DIR = "audio"

client = ElevenLabs(api_key=API_KEY)

def generate_audio(text, output_path):
    # The CSV contains literal \n characters (backslash + n)
    # We strip those out entirely, along with any real newlines
    processed_text = text.replace('\\n', ' ').replace('\n', ' ')
    # Flatten whitespace
    processed_text = " ".join(processed_text.split())
    
    try:
        audio_generator = client.text_to_speech.convert(
            text=processed_text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            voice_settings=VoiceSettings(
                stability=0.8, # Increased stability to reduce inhalations/pauses
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
                speed=0.8
            )
        )
        
        with open(output_path, 'wb') as f:
            for chunk in audio_generator:
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error generating audio: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate Thirukkural audio files.')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of files to generate')
    parser.add_argument('--start_id', type=int, default=1, help='ID to start from')
    args = parser.parse_args()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = pd.read_csv('Thirukural.csv')
    
    # Filter by start_id
    df = df[df['id'] >= args.start_id]
    
    count = 0
    for index, row in df.iterrows():
        if args.limit and count >= args.limit:
            break
            
        kural_id = int(row['id'])
        text = row['kural_tamil']
        output_file = os.path.join(OUTPUT_DIR, f"kural{kural_id}.mp3")
        
        if os.path.exists(output_file):
            print(f"Skipping kural {kural_id}, already exists.")
            continue
            
        print(f"Generating audio for kural {kural_id}...")
        success = generate_audio(text, output_file)
        
        if success:
            print(f"Successfully saved to {output_file}")
            count += 1
            # Small delay to avoid hitting rate limits too aggressively
            time.sleep(1)
        else:
            print(f"Failed to generate audio for kural {kural_id}")
            # Stop on failure to avoid burning credits on errors
            break

    print(f"Done! Generated {count} files.")

if __name__ == "__main__":
    main()
