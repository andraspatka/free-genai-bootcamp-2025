import boto3
import json
import os


class AudioGenerator:
    def __init__(self):
        # AWS clients
        self.polly = boto3.client('polly', region_name='us-east-1')
        
        # Define Italian neural voices by gender
        self.voices = {
            'male': ['Giorgio'],  # Example male voice
            'female': ['Carla']   # Example female voice
        }
        
        # Create audio output directory
        self.audio_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data/static/audio"
        )
        os.makedirs(self.audio_dir, exist_ok=True)


    def generate_audio_part(self, text: str, voice_name: str, video_id: str) -> str:
        """Generate audio for a single part using Amazon Polly"""
        if os.path.exists(os.path.join(self.audio_dir, f"{video_id}.mp3")):
            return os.path.join(self.audio_dir, f"{video_id}.mp3")
        response = self.polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_name,
            Engine='standard',
            LanguageCode='it-IT'  # Set to Italian
        )
        
        # Save to temporary file
        with open(os.path.join(self.audio_dir, f"{video_id}.mp3"), 'wb') as f:
            f.write(response['AudioStream'].read())
        return os.path.join(self.audio_dir, f"{video_id}.mp3")


if __name__ == "__main__":
    video_id = "VdiaPYEYJbc"
    with open(os.path.join("data", "structured", f"{video_id}.json")) as f:
        text = f.read()
    
    text_json = json.loads(json.loads(text))
    print(type(text_json))
    transcript = text_json['transcript']

    try:
        print("Initializing audio generator...")
        generator = AudioGenerator()
        
        print("\nParsing conversation...")
        audio_file = generator.generate_audio_part(transcript, voice_name="Carla", video_id=video_id)

        print(f"Audio file generated: {audio_file}")
    except Exception as e:
        print(f"\nError during test: {str(e)}")