import streamlit as st
import os
import json
import re
from pathlib import Path

# Import your custom modules
import YoutubeDownloader
import FalAIWhisper

# For AI summarization (e.g., using OpenAI API)
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai_api_key"])

# Set OpenAI API key from Streamlit secrets for security

# Directory paths
DATA_DIR = Path('data')
PROMPTS_DIR = DATA_DIR / 'prompts'
TRANSCRIPTS_DIR = DATA_DIR / 'transcripts'
SUMMARIES_DIR = DATA_DIR / 'summaries'

# Ensure directories exist
for directory in [DATA_DIR, PROMPTS_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Initialize session state variables
def initialize_session_state():
    for key, default in {
        'transcription': '',
        'summaries': [],
        'final_summary': '',
        'prompt_list': [],
        'page': 'Home',
        'selected_prompt': None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

# Load prompt library from a JSON file
def load_prompts():
    prompt_files = PROMPTS_DIR.glob('*.json')
    prompts = []
    for prompt_file in prompt_files:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = json.load(f)
            prompts.append(prompt)
    st.session_state['prompt_list'] = prompts

# Save prompt to a JSON file
def save_prompt(prompt):
    prompt_file = PROMPTS_DIR / f"{prompt['name']}.json"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        json.dump(prompt, f, ensure_ascii=False, indent=4)

# Update an existing prompt
def update_prompt(original_name, updated_prompt):
    original_file = PROMPTS_DIR / f"{original_name}.json"
    if original_file.exists():
        original_file.unlink()
    save_prompt(updated_prompt)

# Function to handle video processing
def process_video(video_url):
    try:
        with st.spinner('Downloading and processing video...'):
            audio_path, video_title = YoutubeDownloader.download_video_temp(video_url)
            if os.path.exists(audio_path):
                transcription = FalAIWhisper.run_no_write(audio_path)
                st.session_state['transcription'] = transcription
                st.session_state['video_title'] = video_title
                # Save transcription
                transcript_file = TRANSCRIPTS_DIR / f"{video_title}.txt"
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(transcription)
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
                response = client.chat.completions.create(model='gpt-4',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt_text + "\n\n" + st.session_state['transcription']}
                ],
                max_tokens=500,
                temperature=0.7)
                summary = response.choices[0].message.content.strip()
                st.session_state['summaries'].append(summary)
            st.success('Summaries generated!')
            # Save summaries
            for idx, summary in enumerate(st.session_state['summaries'], 1):
                summary_file = SUMMARIES_DIR / f"{st.session_state['video_title']}_summary_{idx}.txt"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
    except Exception as e:
        st.error(f"An error occurred during summarization: {e}")

# Function to search within the transcription and highlight matches
def search_and_highlight_transcription(transcription, search_term):
    highlighted_text = re.sub(
        f"({re.escape(search_term)})",
        r"<mark>\1</mark>",
        transcription,
        flags=re.IGNORECASE
    )
    return highlighted_text

# Main Streamlit app
def main():
    st.set_page_config(page_title='Horizon Summaries', layout='wide')
    initialize_session_state()

    # Sidebar navigation
    pages = ['Home', 'Prompt Library', 'Transcription Library', 'Summary Library']
    st.sidebar.title('Navigation')
    st.session_state['page'] = st.sidebar.radio('Go to', pages)

    if st.session_state['page'] == 'Home':
        home_page()
    elif st.session_state['page'] == 'Prompt Library':
        prompt_library_page()
    elif st.session_state['page'] == 'Transcription Library':
        transcription_library_page()
    elif st.session_state['page'] == 'Summary Library':
        summary_library_page()

def home_page():
    st.title('📹 Horizon Summaries')

    # Input the video URL
    video_url = st.text_input('🔗 Enter the YouTube/.m3u8 video URL')

    # Load prompts
    load_prompts()

    # Select prompt
    st.header('Select a Prompt')
    prompt_names = [prompt['name'] for prompt in st.session_state['prompt_list']]
    if prompt_names:
        selected_prompt_name = st.selectbox('Choose a prompt', options=prompt_names)
        st.session_state['selected_prompt'] = next(
            (item for item in st.session_state['prompt_list'] if item['name'] == selected_prompt_name),
            None
        )
    else:
        st.info('No prompts available. Please add prompts in the Prompt Library.')

    # Number of generations
    num_generations = st.number_input('🧮 Number of Summaries', min_value=1, max_value=5, value=3, step=1)

    # Process the video
    if st.button('▶️ Process Video'):
        if video_url:
            process_video(video_url)
        else:
            st.error('❌ Please enter a valid video URL.')

    # Display transcription and search functionality
    if st.session_state['transcription']:
        st.header('📝 Transcription')
        search_term = st.text_input('🔍 Search Transcription', key='search')
        if search_term:
            highlighted_transcription = search_and_highlight_transcription(
                st.session_state['transcription'], search_term)
            st.markdown(
                f"<div style='white-space: pre-wrap;'>{highlighted_transcription}</div>",
                unsafe_allow_html=True
            )
        else:
            st.text_area('Full Transcription', st.session_state['transcription'], height=200)

        # Generate summaries
        st.markdown("---")
        if st.button('📝 Generate Summaries'):
            if st.session_state['selected_prompt']:
                generate_summaries(st.session_state['selected_prompt']['text'], num_generations)
            else:
                st.error('❌ Please select or add a prompt.')

        # Display summaries with synchronized scrolling
        if st.session_state['summaries']:
            st.header('🗒️ Generated Summaries')

            # Display summaries with synchronized scrolling using JavaScript
            summary_ids = []
            for idx, summary in enumerate(st.session_state['summaries'], 1):
                summary_id = f"summary_{idx}"
                summary_ids.append(summary_id)
                st.markdown(f"#### Summary {idx}")
                st.markdown(
                    f"<div id='{summary_id}' style='overflow-y: auto; height: 150px; border: 1px solid gray; padding: 5px;'>{summary}</div>",
                    unsafe_allow_html=True
                )

            # Add JavaScript for synchronized scrolling
            sync_script = f"""
            <script>
            const summaryIds = {summary_ids};
            const summaries = summaryIds.map(id => document.getElementById(id));

            summaries.forEach(summary => {{
                summary.addEventListener('scroll', () => {{
                    const scrollTop = summary.scrollTop;
                    summaries.forEach(otherSummary => {{
                        if (otherSummary !== summary) {{
                            otherSummary.scrollTop = scrollTop;
                        }}
                    }});
                }});
            }});
            </script>
            """
            st.components.v1.html(sync_script, height=0, width=0)

            # Final summary editing
            st.header('🖊️ Final Summary')
            st.session_state['final_summary'] = st.text_area(
                'Edit and combine summaries here',
                st.session_state['final_summary'],
                height=200
            )

            if st.button('💾 Save Final Summary'):
                try:
                    final_summary_file = SUMMARIES_DIR / f"{st.session_state['video_title']}_final_summary.txt"
                    with open(final_summary_file, 'w', encoding='utf-8') as f:
                        f.write(st.session_state['final_summary'])
                    st.success('✅ Final summary saved!')
                except Exception as e:
                    st.error(f"Failed to save final summary: {e}")

def prompt_library_page():
    st.title('📚 Prompt Library')

    # Load prompts
    load_prompts()

    # List prompts
    prompt_names = [prompt['name'] for prompt in st.session_state['prompt_list']]
    selected_prompt_name = st.selectbox('Select a prompt to edit', options=prompt_names)
    selected_prompt = next(
        (item for item in st.session_state['prompt_list'] if item['name'] == selected_prompt_name),
        None
    )

    # Edit prompt
    if selected_prompt:
        st.subheader('Edit Prompt')
        new_prompt_name = st.text_input('🔖 Prompt Name', value=selected_prompt['name'])
        new_prompt_text = st.text_area('✏️ Prompt Text', value=selected_prompt['text'])
        if st.button('💾 Update Prompt'):
            if new_prompt_name and new_prompt_text:
                updated_prompt = {'name': new_prompt_name, 'text': new_prompt_text}
                update_prompt(selected_prompt['name'], updated_prompt)
                st.success('Prompt updated!')
                # Reload prompts
                load_prompts()
            else:
                st.error('Please enter both a name and text for the prompt.')

    # Add new prompt
    st.subheader('➕ Add New Prompt')
    new_prompt_name = st.text_input('🔖 New Prompt Name', key='new_prompt_name')
    new_prompt_text = st.text_area('✏️ New Prompt Text', key='new_prompt_text')
    if st.button('💾 Save New Prompt'):
        if new_prompt_name and new_prompt_text:
            new_prompt = {'name': new_prompt_name, 'text': new_prompt_text}
            if any(prompt['name'].lower() == new_prompt_name.lower() for prompt in st.session_state['prompt_list']):
                st.error('A prompt with this name already exists. Please choose a different name.')
            else:
                save_prompt(new_prompt)
                st.success('New prompt saved!')
                # Reload prompts
                load_prompts()
        else:
            st.error('Please enter both a name and text for the new prompt.')

def transcription_library_page():
    st.title('📂 Transcription Library')

    # List transcription files
    transcripts = list(TRANSCRIPTS_DIR.glob('*.txt'))
    if transcripts:
        transcript_files = [file.name for file in transcripts]
        selected_transcript_name = st.selectbox('Select a transcription to view', options=transcript_files)
        with open(TRANSCRIPTS_DIR / selected_transcript_name, 'r', encoding='utf-8') as f:
            transcription_content = f.read()
        st.text_area('Transcription Content', transcription_content, height=300)
    else:
        st.info('No transcriptions available.')

def summary_library_page():
    st.title('📂 Summary Library')

    # List summary files
    summaries = list(SUMMARIES_DIR.glob('*_summary_*.txt'))
    if summaries:
        summary_files = [file.name for file in summaries]
        selected_summary_name = st.selectbox('Select a summary to view', options=summary_files)
        with open(SUMMARIES_DIR / selected_summary_name, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        st.text_area('Summary Content', summary_content, height=300)
    else:
        st.info('No summaries available.')

if __name__ == '__main__':
    main()