import os
import sys
import asyncio
import fal_client
import httpx
from dotenv import load_dotenv
from fal_client import InProgress, Queued, Completed
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

    print("Splitting completed")
    return chunk_files

async def submit(audio_url):
    handler = await fal_client.submit_async(
        "fal-ai/wizper",
        arguments={
            "audio_url": audio_url
        },
    )
    return handler.request_id

async def transcribe_chunk(temp_file_path, max_tries=5, current_retry=0):
    try:
        data_url = await fal_client.upload_file_async(temp_file_path)

        request_id = await submit(data_url)
        print(f"Submitted request with ID: {request_id}")

        status = await fal_client.status_async("fal-ai/wizper", request_id, with_logs=True)
        while isinstance(status, InProgress) or isinstance(status, Queued):
            await asyncio.sleep(5)
            status = await fal_client.status_async("fal-ai/wizper", request_id, with_logs=True)
            print("Status:", status)

        # I don't think there's a Failed status in the fal_client
        #if isinstance(status, ) and current_retry < max_tries:
        #    print(f"Error: Failed to transcribe {temp_file_path}. Retrying...")
        #    return await transcribe_chunk(temp_file_path, max_tries, current_retry + 1)

        if isinstance(status, Completed):
            result = await fal_client.result_async("fal-ai/wizper", request_id)
            return result["text"]
    except:
        if current_retry < max_tries:
            print(f"Timeout occurred. Retrying... (Attempt {current_retry + 1})")
            await asyncio.sleep(2 ** current_retry)  # Exponential backoff
            return await transcribe_chunk(temp_file_path, max_tries, current_retry + 1)
        else:
            print(f"Max retries reached. Failed to transcribe {temp_file_path}.")
            return None

"""
async def transcribe_chunk(temp_file_path):
    print(f"Transcribing {temp_file_path}...")
    audio_url = await fal_client.upload_file_async(temp_file_path)
    response = await fal_client.run_async("fal-ai/wizper", arguments={"audio_url": audio_url})
    return response["text"]
"""

async def transcribe_audio(file_path, video_title):
    # Load environment variables from .env file
    load_dotenv()

    # Make sure the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)

    # Split the audio file if it exceeds the maximum allowed size
    audio_files = split_audio(file_path)

    # Set FalAI API token
    token = os.getenv("FALAI_TOKEN")
    if not token:
        print("Error: FALAI_TOKEN environment variable is not set.")
        sys.exit(1)
    os.environ["FAL_KEY"] = token

    # Transcribe each chunk asynchronously and combine the transcriptions
    tasks = [transcribe_chunk(temp_file_path) for temp_file_path in audio_files]
    transcriptions = await asyncio.gather(*tasks)

    # Remove the temporary files (only the temp chunk files)
    for temp_file_path in audio_files:
        os.remove(temp_file_path)

    # Combine all transcriptions
    complete_transcription = " ".join(transcriptions)

    # Save the complete transcription to a file
    output_path = f"OutputFiles/{video_title}_transcription.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(complete_transcription)
    print(f"Transcription saved to {output_path}")

def run(audio_path, video_title):
    asyncio.run(transcribe_audio(audio_path, video_title))

if __name__ == "__main__":
    audio_file_path = "InputFiles/OfficeHours21-10-24.mp3"
    video_title = "OfficeHours21-10-24"  # You can set this to any title you prefer
    run(audio_file_path, video_title)