import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

#pip install --upgrade google-cloud-aiplatform
#gcloud auth application-default login


def generate():
    vertexai.init(project="betajupiterhorizon", location="europe-west1")
    model = GenerativeModel(
        "gemini-1.5-pro-002",
        system_instruction=[textsi_1]
    )
    responses = model.generate_content(
        [text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        print(response.text, end="")

# The Transcription/Prompt!
text1 = """
"""

# The System Instruction!
textsi_1 = """
"""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.5,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

generate()