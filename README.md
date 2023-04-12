# Survey Bot

A Flask-based application that acts as an automated survey bot for probing questions about politics. The application leverages Twilio's Voice API to receive and process incoming calls, OpenAI's Whisper ASR API to transcribe speech, GPT-3.5 Turbo to generate responses, and Eleven Labs' TTS API to convert text to speech.

## Prerequisites

1. Python 3.6 or higher
2. Flask
3. Twilio SDK
4. OpenAI SDK
5. A Twilio account with a valid phone number
6. An OpenAI API key
7. An Eleven Labs API key

## Installation

Clone the repository:
git clone https://github.com/yrvelez/ivr_bot.git

Install the required dependencies:
pip install -r requirements.txt

Set up environment variables for your API keys and Eleven Labs Voice ID:
export OPENAI_API_KEY="your_openai_key"
export ELEVENLABS_API_KEY="your_elevenlabs_key"
export ELEVENLABS_VOICE_ID="your_voice_id"

Run the Flask app:
python app.py

Important: Configure your Twilio webhook to point to your running application's /incoming_call endpoint.

## Usage
Call your Twilio phone number.
The automated survey bot will ask questions about politics.
The bot will use GPT-3 to generate probing follow-up questions based on your answers.
