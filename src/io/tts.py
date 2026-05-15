# import os
# import queue
# import numpy as np
# from kokoro_onnx import Kokoro
# from src.io.audio_utils import OrderedAudioQueue

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# kokoro = Kokoro(
#     os.path.join(BASE_DIR, "kokoro-v1.0.onnx"),
#     os.path.join(BASE_DIR, "voices-v1.0.bin")
# )

# VOICE = "af_heart"


# def synthesize_to_queue(sentence: str, audio_queue: OrderedAudioQueue, index: int = 0):
#     if not sentence.strip():
#         return

#     samples, sr = synthesize_sentence(sentence)
#     # print(f"[TTS] sentence='{sentence}'")  # debug
#     # print(f"[TTS] samples={len(samples)}, sr={sr}")  # debug

#     audio_queue.put(index, samples.astype(np.float32), sr)


# def synthesize_sentence(sentence: str):
#     return kokoro.create(
#         sentence,
#         voice=VOICE,
#         speed=1.0,
#         lang="en-us"
#     )


import os
import queue
import numpy as np
from kokoro_onnx import Kokoro
from src.io.audio_utils import OrderedAudioQueue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

kokoro = Kokoro(
    os.path.join(BASE_DIR, "kokoro-v1.0.onnx"),
    os.path.join(BASE_DIR, "voices-v1.0.bin")
)

VOICE = "af_heart"


def synthesize_to_queue(sentence: str, audio_queue: OrderedAudioQueue, index: int = 0):
    if not sentence.strip():
        return

    samples, sr = synthesize_sentence(sentence)
    audio_queue.put(index, samples.astype(np.float32), sr)


def synthesize_sentence(sentence: str):
    return kokoro.create(
        sentence,
        voice=VOICE,
        speed=1.0,
        lang="en-us"
    )

