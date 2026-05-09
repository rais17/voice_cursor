import threading
import numpy as np
import sounddevice as sd
import webrtcvad

from moonshine_voice import get_model_for_language
from moonshine_voice.transcriber import Transcriber
# from src.io.audio_utils import is_speaking

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)
FRAME_BYTES = FRAME_SAMPLES * 2

SILENCE_TRIGGER = 20
MIN_SPEECH_FRAMES = 5

# ==========================================
# Model ek baar load karo — module level
# ==========================================
print("Loading Moonshine model...")
_model_path, _model_arch = get_model_for_language(wanted_language="en")
_model = Transcriber(model_path=_model_path, model_arch=_model_arch)
print("Model loaded.")


def transcribe_streaming() -> str:
    print("🎙 Listening... Speak now")

    vad = webrtcvad.Vad(2)

    speech_frames = []
    silence_count = 0
    triggered = False
    result_text = ""
    completed = threading.Event()

    def audio_callback(indata, frames, time_info, status):
        # if is_speaking.is_set():
        #     return 
        nonlocal speech_frames, silence_count, triggered, result_text

        if status:
            print(status)

        pcm_int16 = (indata[:, 0] * 32767).astype(np.int16)
        pcm_bytes = pcm_int16.tobytes()

        if len(pcm_bytes) != FRAME_BYTES:
            return

        is_speech = vad.is_speech(pcm_bytes, SAMPLE_RATE)
        print(f"is_speech: {is_speech}, triggered: {triggered}, silence_count: {silence_count}")

        if is_speech:
            if not triggered:
                print("🗣 Speech detected")
            triggered = True
            silence_count = 0
            speech_frames.append(indata[:, 0].copy())

        elif triggered:
            silence_count += 1
            speech_frames.append(indata[:, 0].copy())

            if silence_count >= SILENCE_TRIGGER:
                if len(speech_frames) >= MIN_SPEECH_FRAMES:
                    print("⏳ Transcribing...")
                    audio = np.concatenate(speech_frames).astype(np.float32)

                    try:
                        transcript = _model.transcribe_without_streaming(audio)
                        text = transcript.text.strip() if hasattr(transcript, "text") else str(transcript).strip()
                        print(f"\n[FINAL] {text}")
                        if text:
                            result_text = text
                            completed.set()
                    except Exception as e:
                        print(f"❌ Transcription error: {e}")

                speech_frames = []
                silence_count = 0
                triggered = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=FRAME_SAMPLES,
        callback=audio_callback,
    ):
        completed.wait(timeout=15)

    if not completed.is_set():
        print("\n[TIMEOUT] No speech detected")

    return result_text