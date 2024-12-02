from youtube_transcript_api import YouTubeTranscriptApi
import json

# Function to extract the video ID from the URL
def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    else:
        raise ValueError("Invalid YouTube URL")

# Function to retrieve transcript and save it to a file
def save_transcript(url, file_name):
    try:
        # Extract video ID from the URL
        video_id = get_video_id(url)

        print(f"Extracted Video_id: {video_id}")
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        print("Fetched Transcript")
        # Create a formatted transcript string
        formatted_transcript = "\n".join([item['text'] for item in transcript])

        # Save to a text file
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(formatted_transcript)

        print(f"Transcript saved successfully to {file_name}")

    except Exception as e:
        print(f"Error: {e}")

# Example usage:
youtube_url = "https://www.youtube.com/watch?v=vDTtuDWovN0"  # Replace with your YouTube video URL
save_transcript(youtube_url, "transcript.txt")