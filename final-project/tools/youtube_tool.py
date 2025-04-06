from .schemas import YouTubeInputSchema, YouTubeOutputSchema, YouTubeTranscriptChunkSchema
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> str | None:
    """Extracts YouTube video ID from various URL formats."""
    # Examples:
    # - http://www.youtube.com/watch?v=VIDEO_ID
    # - http://youtu.be/VIDEO_ID
    # - http://www.youtube.com/embed/VIDEO_ID
    # - http://www.youtube.com/v/VIDEO_ID?version=3&hl=en_US
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
        if parsed_url.path.startswith( '/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    # Add more parsing logic if needed for other formats
    return None

def get_youtube_transcript(input_data: YouTubeInputSchema) -> YouTubeOutputSchema:
    """Fetches and structures the transcript of a YouTube video."""
    logger.info(f"Fetching transcript for URL: {input_data.url}")
    video_id = extract_video_id(input_data.url)
    if not video_id:
        logger.error(f"Could not extract video ID from URL: {input_data.url}")
        # Consider raising an error or returning a specific error state
        return YouTubeOutputSchema(video_id="", title="", transcript=[])

    try:
        # Attempt to get manually created transcripts first, then generated ones
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Simple preference: Italian -> English -> First available
        preferred_langs = ['it', 'en']
        transcript = None
        for lang in preferred_langs:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                logger.info(f"Found manually created transcript in {lang}.")
                break
            except Exception:
                continue

        if not transcript:
            for lang in preferred_langs:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    logger.info(f"Found auto-generated transcript in {lang}.")
                    break
                except Exception:
                    continue

        if not transcript:
             # Fallback to the first available transcript if no preferred language found
            first_transcript_info = next(iter(transcript_list._transcripts.values()), None)
            if first_transcript_info:
                 transcript = transcript_list.find_transcript([first_transcript_info.language_code])
                 logger.warning(f"Preferred language transcript not found. Using first available: {first_transcript_info.language_code}")
            else:
                raise Exception("No transcript available for this video.")

        fetched_transcript = transcript.fetch()
        video_title = "Unknown Title" # Placeholder, API doesn't directly give title
        # In a real app, you might use youtube-dlp or another API to get the title

        output_transcript = [
            YouTubeTranscriptChunkSchema(
                text=chunk['text'],
                start=chunk['start'],
                duration=chunk['duration']
            ) for chunk in fetched_transcript
        ]

        logger.info(f"Successfully fetched transcript for video ID: {video_id}")
        return YouTubeOutputSchema(
            video_id=video_id,
            title=video_title,
            transcript=output_transcript
        )

    except Exception as e:
        logger.error(f"Error fetching transcript for video ID {video_id}: {e}", exc_info=True)
        return YouTubeOutputSchema(video_id=video_id, title="Error", transcript=[])

# Example usage (for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Replace with a real YouTube URL that has transcripts
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Example, pick one with italian/english transcript
    test_input = YouTubeInputSchema(url=test_url)
    output = get_youtube_transcript(test_input)
    print(output.model_dump_json(indent=2))
