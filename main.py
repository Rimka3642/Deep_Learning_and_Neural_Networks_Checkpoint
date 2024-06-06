import streamlit as st
import speech_recognition as sr
import re
import sounddevice as sd
import wavio
import numpy as np
import nltk

# Download NLTK data files (if not already downloaded)
nltk.download('punkt')

# Define the chatbot dialogue patterns
pairs = [
    ["(.*)appel(.*)", ["Hello %2"]],
    ["(.*)nom(.*)", ["Hello %2"]],
    ["(Bonjour|Salut|Coucou)", ["Salut toi", "Hello", 'En quoi puis-je aider']],
    ["Je veux passer une commande", ["Que désirez-vous aujourd'hui ?"]],
    ["Je veux un (.*) de taille (.*)", ["Je vais préparer le %1 taille %2"]],
    ["(.*)(ville|adresse)", ["Nous sommes basés à Dakar"]],
    ["(.*)(aider|aidez)(.*)", ["Que puis-je faire pour vous aujourd'hui"]],
    ["(.*)merci(.*)", ["Je vous en prie, à bientôt"]]
]

# Function to get chatbot response
def chatbot_response(user_input):
    for pattern, responses in pairs:
        match = re.match(pattern, user_input, re.IGNORECASE)
        if match:
            response = responses[0]
            placeholders = re.findall(r"%(\d+)", response)
            for placeholder in placeholders:
                response = response.replace(f"%{placeholder}", match.group(int(placeholder)))
            return response
    return "Désolé, je ne comprends pas votre demande."

# Function to transcribe speech
def transcribe_speech(api, language):
    r = sr.Recognizer()

    try:
        import pyaudio
    except Exception as e:
        st.error(f"PyAudio installation issue: {e}")
        return f"PyAudio installation issue: {e}"

    try:
        with sr.Microphone() as source:
            st.info("Speak now...")
            r.adjust_for_ambient_noise(source)
            audio_text = r.listen(source)
            st.info("Audio captured, transcribing...")

            try:
                if api == "Google":
                    text = r.recognize_google(audio_text, language=language)
                elif api == "Sphinx":
                    text = r.recognize_sphinx(audio_text, language=language)
                else:
                    return "Selected API not supported."
                return text
            except sr.UnknownValueError:
                return "Sorry, I did not understand the audio."
            except sr.RequestError as e:
                return f"Could not request results from {api} service; {e}"
            except Exception as e:
                return f"An error occurred during transcription: {e}"
    except Exception as e:
        st.error(f"Microphone access issue: {e}")
        return f"Microphone access issue: {e}"

# Main function
def main():
    st.title("Speech-Enabled Chatbot")
    st.write("Click on the microphone to start speaking, and click again to stop:")

    # Initialize session state variables
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""

    # Select API
    api = st.selectbox("Select Speech Recognition API", ["Google", "Sphinx"])

    # Select language
    language = st.text_input("Enter language code (e.g., 'fr-FR' for French, 'en-US' for English, 'es-ES' for Spanish):", "fr-FR")

    # Button to start/stop recording
    if st.button("Start/Stop Recording"):
        if st.session_state.recording:
            st.session_state.recording = False
            st.session_state.transcription = transcribe_speech(api, language)
        else:
            st.session_state.recording = True

    # Display the transcription
    if not st.session_state.recording and st.session_state.transcription:
        st.write("Transcription: ", st.session_state.transcription)
        user_input = st.session_state.transcription
        response = chatbot_response(user_input)
        st.write("Chatbot: " + response)

        if st.button("Save Transcription"):
            with open("transcription.txt", "w") as f:
                f.write(st.session_state.transcription)
            st.success("Transcription saved to transcription.txt")

if __name__ == "__main__":
    main()
