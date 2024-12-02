import subprocess


def download_twitter_audio(twitter_url, output_file):
    command = [
        "ffmpeg",
        "-i", twitter_url,
        "-vn",  # Ignore video stream
        "-acodec", "pcm_s16le",  # Use the WAV format audio codec
        "-ar", "44100",  # Set audio sampling rate (44.1 kHz)
        "-ac", "2",  # Set number of audio channels (stereo)
        output_file
    ]

    try:
        # Run the command
        subprocess.run(command, check=True)
        print(f"Download and conversion completed: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    # Example usage
    #m3u8_url = "https://video.twimg.com/amplify_video/1838502470332375040/pl/z5KpZ5qYi4-umQP9.m3u8?tag=16"
    m3u8_url = "https://prod-fastly-us-east-1.video.pscp.tv/Transcoding/v1/hls/S8R5VB-wH4ni0xWsvOqkroE-l2af7HLwx50dQWAa-iUwjbeFGAwFB5EZ9C1Jx4d66TfDdJMjayDdh63YaIBm5g/transcode/us-east-1/periscope-replay-direct-prod-us-east-1-public/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInZlcnNpb24iOiIyIn0.eyJFbmNvZGVyU2V0dGluZyI6ImVuY29kZXJfc2V0dGluZ18zMjBwMzBfMTAiLCJIZWlnaHQiOjMyMCwiS2JwcyI6NjAwLCJUcmFuc2NvZGVBdWRpbyI6dHJ1ZSwiV2lkdGgiOjU2OH0.es_XpNv3J12hFXU4WrCwmH28GmToYAPDPdT_EjerHCU/playlist_16723763947653051752.m3u8?type=replay"
    output_file = "TESToutput.wav"

    download_twitter_audio(m3u8_url, output_file)