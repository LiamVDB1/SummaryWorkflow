import yt_dlp
import tempfile
import os
import requests

def download_video(url, output_path="Videos/%(title)s.%(ext)s"):
    ydl_opts = {
        'format': 'bestaudio/best',  # Downloads the best audio available
        'outtmpl': output_path,
        'retries': 10,  # Number of retries
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract video info to get the title
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', 'Unknown Title')

def download_video_temp(url):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    video_path = f"{temp_path}.%(ext)s"
    ydl_opts = {
        'format': 'bestaudio/best',  # Downloads the best audio available
        'outtmpl': video_path,  # Use the temporary file path
        'retries': 10, # Number of retries
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        #'quiet': True,  # Suppress output
    }

    # Download and convert the video to mp3
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract video info to get the title
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', 'Unknown Title')
        thumbnail_url = info_dict.get('thumbnail', None)

        # Download the thumbnail if the URL is available
        if thumbnail_url:
            thumbnail_response = requests.get(thumbnail_url)
            if thumbnail_response.status_code == 200:
                thumbnail_path = f"OutputFiles/{video_title}_thumbnail.jpg"
                with open(thumbnail_path, 'wb') as f:
                    f.write(thumbnail_response.content)
                print(f"Thumbnail downloaded at {thumbnail_path}")
            else:
                print("Failed to download thumbnail.")
        else:
            print("No thumbnail found.")

    return f"{temp_path}.mp3", video_title

    # After processing, delete the temp file
    #if os.path.exists(temp_path):
    #    os.remove(temp_path)
    #    print(f"Temporary file {temp_path} has been deleted.")

if __name__ == '__main__':
    video_url = "https://prod-fastly-eu-west-1.video.pscp.tv/Transcoding/v1/hls/jUq3dFMc_lHEssSkEwYUBI8bNuebIqHa96_BETWC5mIc1FO2S6jBqLgkZeepr4JFzlc1CpM7fYl9c3KGDeYDFg/transcode/eu-west-1/periscope-replay-direct-prod-eu-west-1-public/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInZlcnNpb24iOiIyIn0.eyJFbmNvZGVyU2V0dGluZyI6ImVuY29kZXJfc2V0dGluZ183MjBwMzBfMTAiLCJIZWlnaHQiOjcyMCwiS2JwcyI6Mjc1MCwiV2lkdGgiOjEyODB9.ldktM4fCFRfkP4ZEBfZPKtlAUNAcTPkoz994YJAzWpE/playlist_16717819090958262386.m3u8?type=replay"
    download_video_temp(video_url)