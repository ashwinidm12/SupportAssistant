# voice_mic.py
import streamlit as st
import io

def render_whatsapp_mic():
    if "mic_key" not in st.session_state:
        st.session_state.mic_key = "micbtn"

    key = st.session_state.mic_key

    st.markdown(f"""
    <button id="mic-{key}" style="border:none;background:none;font-size:20px;cursor:pointer;">🎤</button>

    <script>
    let chunks = [];
    let mediaRecorder;
    const btn = document.getElementById("mic-{key}");

    btn.onclick = function() {{
        navigator.mediaDevices.getUserMedia({{audio:true}})
            .then(stream => {{
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                btn.textContent = "🔴";

                mediaRecorder.ondataavailable = e => chunks.push(e.data);

                mediaRecorder.onstop = e => {{
                    const blob = new Blob(chunks);
                    var file = new File([blob], "record.webm");
                    var dt = new DataTransfer();
                    dt.items.add(file);

                    document.querySelector('input[type="file"]').files = dt.files;
                    btn.textContent = "🎤";
                }};

                setTimeout(() => mediaRecorder.stop(), 2500);
            }});
    }};
    </script>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Voice", type=["webm"], label_visibility="collapsed")

    if uploaded:
        return _process_audio(uploaded)

    return None


def _process_audio(uploaded_file):
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
    except ImportError:
        return None

    try:
        data = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(data))
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)

        transcript = recognizer.recognize_google(audio_data)
        return transcript

    except Exception:
        return None
