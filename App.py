import streamlit as st
import os
import asyncio
import json
import re

# Import your custom modules
import YoutubeDownloader
import FalAIWhisper

# For AI summarization (e.g., using OpenAI API)
import openai

# Initialize session state variables
if 'transcription' not in st.session_state:
    st.session_state['transcription'] = ''
if 'summaries' not in st.session_state:
    st.session_state['summaries'] = []
if 'final_summary' not in st.session_state:
    st.session_state['final_summary'] = ''
if 'prompt_list' not in st.session_state:
    st.session_state['prompt_list'] = []

# Load prompt library from a JSON file
def load_prompts():
    if os.path.exists('prompts.json'):
        with open('prompts.json', 'r') as f:
            st.session_state['prompt_list'] = json.load(f)
    else:
        st.session_state['prompt_list'] = []

# Save prompt library to a JSON file
def save_prompts():
    with open('prompts.json', 'w') as f:
        json.dump(st.session_state['prompt_list'], f)

# Function to handle video processing
def process_video(video_url):
    with st.spinner('Downloading and processing video...'):
        audio_path, video_title = YoutubeDownloader.download_video_temp(video_url)
        if os.path.exists(audio_path):
            st.session_state['transcription'] = FalAIWhisper.run(audio_path, video_title)
            os.remove(audio_path)
            st.success('Transcription completed!')
        else:
            st.error('Failed to process the video.')

# Function to generate summaries
def generate_summaries(prompt_text, num_generations):
    with st.spinner('Generating summaries...'):
        st.session_state['summaries'] = []
        for _ in range(num_generations):
            # Replace this with your actual AI summarization method
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=prompt_text + '\n\n' + st.session_state['transcription'],
                max_tokens=150,
                temperature=0.7,
            )
            summary = response.choices[0].text.strip()
            st.session_state['summaries'].append(summary)
        st.success('Summaries generated!')

# Main Streamlit app
def main():
    st.title('Video Transcription and Summarization Tool')

    # Input the .m3u8 video URL
    video_url = st.text_input('Enter the .m3u8 video URL')

    # Load prompts
    load_prompts()

    # Prompt management
    st.sidebar.header('Prompt Library')
    prompt_options = [prompt['name'] for prompt in st.session_state['prompt_list']]
    selected_prompt_name = st.sidebar.selectbox('Choose a prompt', options=prompt_options)
    selected_prompt = next((item for item in st.session_state['prompt_list'] if item['name'] == selected_prompt_name), None)

    st.sidebar.subheader('Add New Prompt')
    new_prompt_name = st.sidebar.text_input('New Prompt Name')
    new_prompt_text = st.sidebar.text_area('New Prompt Text')
    if st.sidebar.button('Save New Prompt'):
        if new_prompt_name and new_prompt_text:
            st.session_state['prompt_list'].append({'name': new_prompt_name, 'text': new_prompt_text})
            save_prompts()
            st.sidebar.success('New prompt saved!')
        else:
            st.sidebar.error('Please enter both a name and text for the new prompt.')

    # Number of generations
    num_generations = st.sidebar.number_input('Number of Generations', min_value=1, max_value=10, value=3)

    # Process the video
    if st.button('Process Video'):
        if video_url:
            process_video(video_url)
        else:
            st.error('Please enter a video URL.')

    # Display transcription and search functionality
    if st.session_state['transcription']:
        st.header('Transcription')
        search_term = st.text_input('Search Transcription')
        if search_term:
            pattern = re.compile(f'.*{re.escape(search_term)}.*', re.IGNORECASE)
            matches = pattern.findall(st.session_state['transcription'])
            if matches:
                for match in matches:
                    st.write(match)
            else:
                st.write('No matches found.')
        else:
            st.text_area('Full Transcription', st.session_state['transcription'], height=200)

        # Generate summaries
        if st.button('Generate Summaries'):
            if selected_prompt:
                generate_summaries(selected_prompt['text'], num_generations)
            else:
                st.error('Please select a prompt.')

        # Display summaries side by side
        if st.session_state['summaries']:
            st.header('Generated Summaries')
            cols = st.columns(num_generations)
            for i, col in enumerate(cols):
                with col:
                    st.text_area(f'Summary {i+1}', st.session_state['summaries'][i], height=200)

            # Final summary editing
            st.header('Final Summary')
            st.session_state['final_summary'] = st.text_area(
                'Edit and combine summaries here',
                st.session_state['final_summary'],
                height=200
            )

            if st.button('Save Final Summary'):
                with open('final_summary.txt', 'w') as f:
                    f.write(st.session_state['final_summary'])
                st.success('Final summary saved!')

if __name__ == '__main__':
    main()