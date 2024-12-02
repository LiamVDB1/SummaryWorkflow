import streamlit as st
import os
import asyncio
import json
import re
import tempfile
from pathlib import Path

# Import your custom modules
import YoutubeDownloader
import FalAIWhisper

# For AI summarization (e.g., using OpenAI API)
import openai

# Set OpenAI API key from Streamlit secrets for security
openai.api_key = st.secrets["openai_api_key"]

# Initialize session state variables
def initialize_session_state():
    for key, default in {
        'transcription': '',
        'summaries': [],
        'final_summary': '',
        'prompt_list': []
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

# Load prompt library from a JSON file
def load_prompts(prompt_file='prompts.json'):
    if os.path.exists(prompt_file):
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                st.session_state['prompt_list'] = json.load(f)
        except json.JSONDecodeError:
            st.error("Failed to decode prompts.json. Please check the file format.")
            st.session_state['prompt_list'] = []
    else:
        st.session_state['prompt_list'] = []

# Save prompt library to a JSON file
def save_prompts(prompt_file='prompts.json'):
    try:
        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(st.session_state['prompt_list'], f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Failed to save prompts: {e}")

# Function to handle video processing
def process_video(video_url):
    try:
        with st.spinner('Downloading and processing video...'):
            audio_path, video_title = YoutubeDownloader.download_video_temp(video_url)
            if os.path.exists(audio_path):
                transcription = FalAIWhisper.run(audio_path, video_title)
                st.session_state['transcription'] = transcription
                st.success('Transcription completed!')
            else:
                st.error('Failed to download or process the video.')
    except Exception as e:
        st.error(f"An error occurred during video processing: {e}")
    finally:
        # Ensure the audio file is removed to free up space
        if 'audio_path' in locals() and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception as e:
                st.warning(f"Could not remove temporary audio file: {e}")

# Function to generate summaries using OpenAI's ChatCompletion API
def generate_summaries(prompt_text, num_generations):
    try:
        with st.spinner('Generating summaries...'):
            st.session_state['summaries'] = []
            for i in range(num_generations):
                response = openai.ChatCompletion.create(
                    model='gpt-4',
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt_text + "\n\n" + st.session_state['transcription']}
                    ],
                    max_tokens=150,
                    temperature=0.7,
                )
                summary = response.choices[0].message['content'].strip()
                st.session_state['summaries'].append(summary)
            st.success('Summaries generated!')
    except Exception as e:
        st.error(f"An error occurred during summarization: {e}")

# Function to add a new prompt
def add_new_prompt(new_prompt_name, new_prompt_text):
    if any(prompt['name'].lower() == new_prompt_name.lower() for prompt in st.session_state['prompt_list']):
        st.sidebar.error('A prompt with this name already exists. Please choose a different name.')
        return
    st.session_state['prompt_list'].append({'name': new_prompt_name, 'text': new_prompt_text})
    save_prompts()
    st.sidebar.success('New prompt saved!')

# Function to search within the transcription
def search_transcription(transcription, search_term):
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    matches = pattern.finditer(transcription)
    results = [match.group() for match in matches]
    return results

# Main Streamlit app
def main():
    st.set_page_config(page_title='Horizon Summaries', layout='wide')
    st.title('📹 Horizon Summaries')

    # Initialize session state
    initialize_session_state()

    # Input the .m3u8 video URL
    video_url = st.text_input('🔗 Enter the Youtube/.m3u8 video URL')

    # Load prompts
    load_prompts()

    # Prompt management in sidebar
    st.sidebar.header('📚 Prompt Library')
    prompt_names = [prompt['name'] for prompt in st.session_state['prompt_list']]
    if prompt_names:
        selected_prompt_name = st.sidebar.selectbox('Choose a prompt', options=prompt_names)
        selected_prompt = next((item for item in st.session_state['prompt_list'] if item['name'] == selected_prompt_name), None)
    else:
        selected_prompt = None
        st.sidebar.info('No prompts available. Add a new prompt below.')

    st.sidebar.subheader('➕ Add New Prompt')
    new_prompt_name = st.sidebar.text_input('🔖 New Prompt Name')
    new_prompt_text = st.sidebar.text_area('✏️ New Prompt Text')
    if st.sidebar.button('💾 Save New Prompt'):
        if new_prompt_name and new_prompt_text:
            add_new_prompt(new_prompt_name, new_prompt_text)
        else:
            st.sidebar.error('Please enter both a name and text for the new prompt.')

    # Number of generations
    num_generations = st.sidebar.number_input('🧮 Number of Summaries', min_value=1, max_value=5, value=3, step=1)

    # Process the video
    if st.button('▶️ Process Video'):
        if video_url:
            process_video(video_url)
        else:
            st.error('❌ Please enter a valid video URL.')

    # Display transcription and search functionality
    if st.session_state['transcription']:
        st.header('📝 Transcription')
        search_term = st.text_input('🔍 Search Transcription')
        if search_term:
            results = search_transcription(st.session_state['transcription'], search_term)
            if results:
                st.markdown(f"### Found {len(results)} result(s):")
                for idx, match in enumerate(results, 1):
                    st.write(f"{idx}. {match}")
            else:
                st.write('No matches found.')
        else:
            st.text_area('Full Transcription', st.session_state['transcription'], height=200)

        # Generate summaries
        st.markdown("---")
        if st.button('📝 Generate Summaries'):
            if selected_prompt:
                generate_summaries(selected_prompt['text'], num_generations)
            else:
                st.error('❌ Please select or add a prompt.')

        # Display summaries
        if st.session_state['summaries']:
            st.header('🗒️ Generated Summaries')
            # Limit the number of columns to a reasonable number (e.g., 3)
            max_columns = 3
            cols = st.columns(min(len(st.session_state['summaries']), max_columns))
            for idx, summary in enumerate(st.session_state['summaries'], 1):
                with cols[idx % max_columns]:
                    st.text_area(f'Summary {idx}', summary, height=150)

            # Final summary editing
            st.header('🖊️ Final Summary')
            st.session_state['final_summary'] = st.text_area(
                'Edit and combine summaries here',
                st.session_state['final_summary'],
                height=200
            )

            if st.button('💾 Save Final Summary'):
                try:
                    with open('final_summary.txt', 'w', encoding='utf-8') as f:
                        f.write(st.session_state['final_summary'])
                    st.success('✅ Final summary saved!')
                except Exception as e:
                    st.error(f"Failed to save final summary: {e}")

if __name__ == '__main__':
    main()