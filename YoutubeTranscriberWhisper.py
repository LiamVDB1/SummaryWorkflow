import openai
import yt_dlp
from openai import OpenAI
import os
from pydub import AudioSegment
from math import ceil

# Initialize OpenAI API key
client = OpenAI(api_key=OPENAI_API_KEY)


# Step 1: Download only the YouTube audio stream
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': './%(title)s.%(ext)s',  # Save the audio with the title of the video
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Extract audio as MP3
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# Step 2: Split audio into chunks if it exceeds the size limit (25MB)
def split_audio(file_path, chunk_size=24 * 1024 * 1024):  # Chunk size slightly less than 25 MB
    audio = AudioSegment.from_file(file_path)
    duration_ms = len(audio)
    num_chunks = ceil(os.path.getsize(file_path) / chunk_size)

    chunk_duration = duration_ms // num_chunks
    chunks = []

    for i in range(num_chunks):
        start_ms = i * chunk_duration
        end_ms = min((i + 1) * chunk_duration, duration_ms)
        chunk = audio[start_ms:end_ms]
        chunk_file = f"{file_path[:-4]}_chunk{i}.mp3"
        chunk.export(chunk_file, format="mp3")
        chunks.append(chunk_file)

    return chunks


# Step 3: Transcribe audio using OpenAI Whisper
def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(model="whisper-1",
            file=audio_file,
            response_format="text",
            language="en",  # Change this to your desired language (e.g., "nl" for Dutch)
            temperature=0)
        return transcription

    except openai.OpenAIError as e:
        print(f"Error during transcription: {e}")
        return ""


# Main function to download audio, transcribe, and save the result
def process_youtube_video(video_url):
    # Step 1: Download the YouTube audio as mp3
    #download_audio(video_url)

    # Find the downloaded audio file (assuming it's saved as .mp3)
    for file in os.listdir():
        if file.endswith(".mp3"):
            audio_file_path = file
            break
    else:
        print("Audio file not found after download.")
        return

    # Step 2: Check file size and split if necessary
    file_size = os.path.getsize(audio_file_path)
    if file_size > 25 * 1024 * 1024:  # If the file is larger than 25 MB
        audio_chunks = split_audio(audio_file_path)
    else:
        audio_chunks = [audio_file_path]

    # Step 3: Transcribe each chunk and save the result
    full_transcription = ""
    for chunk in audio_chunks:
        transcription = transcribe_audio(chunk)
        full_transcription += transcription

    # Step 4: Save full transcription to a text file
    with open(f"{audio_file_path[:-4]}.txt", "w") as output_file:
        output_file.write(full_transcription)
    print(f"Transcription saved to {audio_file_path[:-4]}.txt")


# Example usage
if __name__ == '__main__':
    video_url = "https://www.youtube.com/watch?v=vDTtuDWovN0"  # Replace with your YouTube URL
    process_youtube_video(video_url)