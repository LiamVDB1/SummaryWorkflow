from openai import audio

import YoutubeDownloader
import FalAIWhisper
import os

def run(video_url):
    audio_path, video_title = YoutubeDownloader.download_video_temp(video_url)

    if os.path.exists(audio_path):
        print("Transcribing audio...")
        FalAIWhisper.run(audio_path, video_title)

        os.remove(audio_path)

    print("Transcription completed")

if __name__ == "__main__":
    video_url = "https://prod-fastly-eu-west-1.video.pscp.tv/Transcoding/v1/hls/tx6VqmEQn27Cn9wfQ-xZfHDK6pAY0klVSUdYpUNRNom9ku7SzK9xJsKuObTi8WxFmZaycYlDlhE1UBimjfnlPw/transcode/eu-west-1/periscope-replay-direct-prod-eu-west-1-public/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInZlcnNpb24iOiIyIn0.eyJFbmNvZGVyU2V0dGluZyI6ImVuY29kZXJfc2V0dGluZ183MjBwMzBfMTAiLCJIZWlnaHQiOjcyMCwiS2JwcyI6Mjc1MCwiV2lkdGgiOjEyODB9.ldktM4fCFRfkP4ZEBfZPKtlAUNAcTPkoz994YJAzWpE/playlist_16713580915904783855.m3u8?type=replay"
    run(video_url)



