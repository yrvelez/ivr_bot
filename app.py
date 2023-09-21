from flask import Flask, request, send_from_directory, Response
from twilio.twiml.voice_response import VoiceResponse, Say
from twilio.rest import Client
import openai
import requests
import os
import time 

app = Flask(__name__)

# Load environment variables
openai_key = os.environ.get('OPENAI_API_KEY')
elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
voice_id = os.environ.get('ELEVENLABS_VOICE_ID')

@app.route('/incoming_call', methods=['GET', 'POST'])

def handle_call():
    response = VoiceResponse()
    intro = text_to_speech("Hey! I am an automated survey bot. Please answer the following questions.")
    response.play(intro)
    response.record(action='/process_audio', recording_status_callback_event='completed',
                    recording_format = 'mp3', timeout = 1, play_beep=False)
    return Response(str(response), 200, mimetype='application/xml')

@app.route('/process_audio', methods=['POST'])

def process_audio():
    recording_url = request.values.get('RecordingUrl')
    transcribed_text = transcribe_audio(recording_url)
    gpt3_response = get_gpt3_response(transcribed_text)
    tts_audio_url = text_to_speech(gpt3_response)

    response = VoiceResponse()
    response.play(tts_audio_url)
    response.record(action='/process_audio', recording_status_callback_event='completed',
                    recording_format = 'mp3', timeout = 1, play_beep=False)
    
    return Response(str(response), 200, mimetype='application/xml')

def transcribe_audio(recording_url):
    time.sleep(1)
    # Download the audio file from the recording_url
    audio_response = requests.get(recording_url)
    audio_file_name = "audio_recording.mp3"
    with open(audio_file_name, "wb") as audio_file:
        audio_file.write(audio_response.content)

    whisper_url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {
        'Authorization': 'Bearer' + openai_key
    }

    with open(audio_file_name, "rb") as audio_file:
        files = {'file': audio_file}
        data = {'model': 'whisper-1'}
        response = requests.post(whisper_url, headers=headers, data=data, files=files)

    # Remove the downloaded audio file after processing
    os.remove(audio_file_name)

    if response.status_code == 200:
        transcribed_text = response.json()['text']
        return transcribed_text
    else:
        print("Whisper API response:", response.json())
        raise Exception(f"Whisper ASR API request failed with status code: {response.status_code}")

def get_gpt3_response(transcribed_text):
    prompt = f"{transcribed_text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "You are an automated survey researcher who asks probing questions about politics:" + prompt}],
        max_tokens=100,
        stop=None,
        temperature=0.5
    )

    if response.choices:
        gpt3_response = response.choices[0].message.content.strip()
        return gpt3_response
    else:
        raise Exception("GPT-3 API request failed.")

def text_to_speech(text):
    api_url = 'https://api.elevenlabs.io/v1/text-to-speech/' + voice_id
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': elevenlabs_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'voice_settings': {
            'stability': '.6',
            'similarity_boost': 0
        }
    }
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        file_name = f"tts_{hash(text)}.mp3"
        audio_directory = 'static/audio'
        os.makedirs(audio_directory, exist_ok=True)
        audio_path = os.path.join(audio_directory, file_name)

        with open(audio_path, 'wb') as f:
            f.write(response.content)

        tts_audio_url = f"/audio/{file_name}"
        return tts_audio_url
    else:
        print("Eleven Labs TTS API response:", response.json())
        raise Exception(f"Eleven Labs TTS API request failed with status code: {response.status_code}")

@app.route('/audio/<path:file_name>')
def serve_audio(file_name):
    return send_from_directory('static/audio', file_name)

if __name__ == '__main__':
    app.run()
