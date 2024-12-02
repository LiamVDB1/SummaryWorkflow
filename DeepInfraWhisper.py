import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv
from pydub import AudioSegment
import tempfile


def split_audio(file_path, max_size_mb=50):
    # Load the audio file using pydub
    audio = AudioSegment.from_file(file_path)

    # Determine the chunk size based on the maximum file size allowed
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb <= max_size_mb:
        # If the file size is within the limit, create a temporary copy to work with consistently
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio.export(temp_file.name, format="mp3")
        return [temp_file.name]

    # Split the audio into smaller chunks if it exceeds the maximum file size
    print("Splitting audio into smaller chunks...")
    chunk_length_ms = len(audio) * (max_size_mb / file_size_mb)
    overlap_ms = 200  # 0.2-second overlap
    chunks = [audio[i:i + int(chunk_length_ms) + overlap_ms] for i in range(0, len(audio), int(chunk_length_ms))]

    # Export each chunk to a temporary file
    chunk_files = []
    for chunk in chunks:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        chunk.export(temp_file.name, format="mp3")
        chunk_files.append(temp_file.name)

    return chunk_files


async def transcribe_chunk(session, api_url, headers, temp_file_path, max_tries=5, current_retry=0):
    with open(temp_file_path, "rb") as f:
        files = {"audio": f}
        try:
            print(f"Transcribing {temp_file_path}...")
            async with session.post(api_url, headers=headers, data=files) as response:
                response.raise_for_status()
                response_json = await response.json()
                print(f"Succesfully transcribed {temp_file_path}")
                return response_json.get("text", "No transcription found in the response.")
        except aiohttp.ClientError as e:
            if current_retry < max_tries:
                print(f"Error: {e}. Retrying...")
                return await transcribe_chunk(session, api_url, headers, temp_file_path, max_tries, current_retry + 1)
            else:
                print(f"Error: Failed to transcribe the audio. Details: {e}")
                sys.exit(1)


async def transcribe_audio(file_path, video_title):
    # Load environment variables from .env file
    load_dotenv()

    # Make sure the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)

    # Split the audio file if it exceeds the maximum allowed size
    audio_files = split_audio(file_path)

    # Set DeepInfra API endpoint and token
    api_url = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3"
    token = os.getenv("DEEPINFRA_TOKEN")
    if not token:
        print("Error: DEEPINFRA_TOKEN environment variable is not set.")
        sys.exit(1)

    # Prepare the request headers
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Transcribe each chunk asynchronously and combine the transcriptions
    async with aiohttp.ClientSession() as session:
        tasks = [transcribe_chunk(session, api_url, headers, temp_file_path) for temp_file_path in audio_files]
        transcriptions = await asyncio.gather(*tasks)

    # Remove the temporary files (only the temp chunk files)
    for temp_file_path in audio_files:
        os.remove(temp_file_path)

    # Combine all transcriptions
    complete_transcription = " ".join(transcriptions)

    # Save the complete transcription to a file
    output_path = f"OutputFiles/{video_title}_transcription.txt"
    with open(output_path, "w") as f:
        f.write(complete_transcription)
    print(f"Transcription saved to {output_path}")

def run(audio_path, video_title):
    asyncio.run(transcribe_audio(audio_path, video_title))

if __name__ == "__main__":
    audio_file_path = "twitter_video_trimmed.mp3"
    asyncio.run(transcribe_audio(audio_file_path))