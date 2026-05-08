import threading
import numpy as np
import sounddevice as sd
import webrtcvad

from moonshine_voice import get_model_for_language
from moonshine_voice.transcriber import Transcriber

# ==========================================
# Audio Config
# ==========================================

SAMPLE_RATE = 16000
FRAME_MS = 30

FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480
FRAME_BYTES = FRAME_SAMPLES * 2  # int16 PCM

# ==========================================
# VAD Config
# ==========================================

SILENCE_TRIGGER = 20    # 20 x 30ms = 600ms silence
MIN_SPEECH_FRAMES = 5  # ignore tiny noises

# ==========================================
# Streaming STT
# ==========================================

def transcribe_streaming() -> str:

    print("🎙 Listening... Speak now")

    # WebRTC VAD
    vad = webrtcvad.Vad(2)

    # Load Moonshine model
    model_path, model_arch = get_model_for_language(
        wanted_language="en"
    )

    print(f"📦 Model path: {model_path}")
    print(f"🧠 Model arch: {model_arch}")

    # Create transcriber
    model = Transcriber(
        model_path=model_path,
        model_arch=model_arch
    )

    speech_frames = []
    silence_count = 0
    triggered = False

    result_text = ""
    completed = threading.Event()

    # ==========================================
    # Audio Callback
    # ==========================================

    def audio_callback(indata, frames, time_info, status):

        nonlocal speech_frames
        nonlocal silence_count
        nonlocal triggered
        nonlocal result_text

        if status:
            print(status)

        # float32 -> int16 PCM
        pcm_int16 = (
            indata[:, 0] * 32767
        ).astype(np.int16)

        pcm_bytes = pcm_int16.tobytes()

        # VAD requires exact frame size
        if len(pcm_bytes) != FRAME_BYTES:
            return

        # Detect speech
        is_speech = vad.is_speech(
            pcm_bytes,
            SAMPLE_RATE
        )

        # ==========================================
        # Speech Started
        # ==========================================

        if is_speech:

            if not triggered:
                print("🗣 Speech detected")

            triggered = True
            silence_count = 0

            speech_frames.append(
                indata[:, 0].copy()
            )

        # ==========================================
        # Silence after speech
        # ==========================================

        elif triggered:

            silence_count += 1

            # include trailing silence
            speech_frames.append(
                indata[:, 0].copy()
            )

            # End utterance
            if silence_count >= SILENCE_TRIGGER:

                if len(speech_frames) >= MIN_SPEECH_FRAMES:

                    print("⏳ Transcribing...")
                    print(f"Speech frames: {len(speech_frames)}, Silence frames: {silence_count}")

                    audio = np.concatenate(
                        speech_frames
                    ).astype(np.float32)

                    try:

                        # FINAL CORRECT API
                        transcript = model.transcribe_without_streaming(
                            audio
                        )

                        # SDK versions differ
                        if hasattr(transcript, "text"):
                            text = transcript.text.strip()
                        else:
                            text = str(transcript).strip()

                        print(f"\n[FINAL] {text}")

                        if text:
                            result_text = text
                            completed.set()

                    except Exception as e:
                        print(
                            f"❌ Transcription error: {e}"
                        )

                # Reset state
                speech_frames = []
                silence_count = 0
                triggered = False

    # ==========================================
    # Start Microphone Stream
    # ==========================================

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


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    text = transcribe_streaming();

    print("\n========================")
    print("FINAL TEXT:")
    print(text)
    print("========================")

# import threading
# import numpy as np
# import sounddevice as sd
# import webrtcvad
# from src.io.audio_utils import reduce_noise

# from moonshine_voice import get_model_for_language
# from moonshine_voice.transcriber import Transcriber

# # ==========================================
# # Audio Config
# # ==========================================

# SAMPLE_RATE = 16000
# FRAME_MS = 30

# FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480
# FRAME_BYTES = FRAME_SAMPLES * 2  # int16 PCM

# # ==========================================
# # VAD Config
# # ==========================================

# SILENCE_TRIGGER = 15    # 20 x 30ms = 600ms silence
# MIN_SPEECH_FRAMES = 5  # ignore tiny noises

# # ==========================================
# # Streaming STT
# # ==========================================

# def transcribe_streaming() -> str:

#     print("🎙 Listening... Speak now")

#     # WebRTC VAD
#     vad = webrtcvad.Vad(3)

#     # Load Moonshine model
#     model_path, model_arch = get_model_for_language(
#         wanted_language="en"
#     )

#     print(f"📦 Model path: {model_path}")
#     print(f"🧠 Model arch: {model_arch}")

#     # Create transcriber
#     model = Transcriber(
#         model_path=model_path,
#         model_arch=model_arch
#     )

#     speech_frames = []
#     silence_count = 0
#     triggered = False

#     result_text = ""
#     completed = threading.Event()

#     # ==========================================
#     # Audio Callback
#     # ==========================================

#     def audio_callback(indata, frames, time_info, status):

#         nonlocal speech_frames
#         nonlocal silence_count
#         nonlocal triggered
#         nonlocal result_text

#         if status:
#             print(status)

#         # float32 -> int16 PCM
#         pcm_int16 = (
#             indata[:, 0] * 32767
#         ).astype(np.int16)

#         pcm_bytes = pcm_int16.tobytes()

#         # VAD requires exact frame size
#         if len(pcm_bytes) != FRAME_BYTES:
#             return

#         # Detect speech
#         is_speech = vad.is_speech(
#             pcm_bytes,
#             SAMPLE_RATE
#         )

#         # ==========================================
#         # Speech Started
#         # ==========================================

#         if is_speech:

#             if not triggered:
#                 print("🗣 Speech detected")

#             triggered = True
#             silence_count = 0

#             speech_frames.append(
#                 indata[:, 0].copy()
#             )

#         # ==========================================
#         # Silence after speech
#         # ==========================================

#         elif triggered:

#             silence_count += 1

#             # include trailing silence
#             speech_frames.append(
#                 indata[:, 0].copy()
#             )

#             # End utterance
#             if silence_count >= SILENCE_TRIGGER:

#                 if len(speech_frames) >= MIN_SPEECH_FRAMES:

#                     print("⏳ Transcribing...")

#                     audio = np.concatenate(
#                         speech_frames
#                     ).astype(np.float32)
#                     audio = reduce_noise(audio, SAMPLE_RATE)

#                     try:

#                         # FINAL CORRECT API
#                         transcript = model.transcribe_without_streaming(
#                             audio
#                         )

#                         # SDK versions differ
#                         if hasattr(transcript, "text"):
#                             text = transcript.text.strip()
#                         else:
#                             text = str(transcript).strip()

#                         print(f"\n[FINAL] {text}")

#                         if text:
#                             result_text = text
#                             completed.set()

#                     except Exception as e:
#                         print(
#                             f"❌ Transcription error: {e}"
#                         )

#                 # Reset state
#                 speech_frames = []
#                 silence_count = 0
#                 triggered = False

#     # ==========================================
#     # Start Microphone Stream
#     # ==========================================

#     with sd.InputStream(
#         samplerate=SAMPLE_RATE,
#         channels=1,
#         dtype="float32",
#         blocksize=FRAME_SAMPLES,
#         callback=audio_callback,
#     ):

#         completed.wait(timeout=15)

#     if not completed.is_set():
#         print("\n[TIMEOUT] No speech detected")

#     return result_text


# # ==========================================
# # Main
# # ==========================================

# if __name__ == "__main__":

#     text = transcribe_streaming()

#     print("\n========================")
#     print("FINAL TEXT:")
#     print(text)
#     print("========================")

