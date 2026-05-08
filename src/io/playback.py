import queue
import threading
import numpy as np
import sounddevice as sd
from src.io.audio_utils import SAMPLE_RATE, OrderedAudioQueue


def playback_worker(audio_queue: OrderedAudioQueue, stop_event: threading.Event):
    stream = None
    current_sr = None

    while not stop_event.is_set():
        try:
            item = audio_queue.get(timeout=0.5)
            if item is None:
                break
            chunk, sr = item

            # Sr change hone par stream recreate karo
            if stream is None or sr != current_sr:
                if stream:
                    stream.close()
                stream = sd.OutputStream(
                    samplerate=sr,
                    channels=1,
                    dtype='float32',
                    device=3
                )
                stream.start()
                current_sr = sr

            stream.write(chunk)
        except queue.Empty:
            continue

    if stream:
        stream.close()


def start_playback_thread(audio_queue: OrderedAudioQueue, stop_event: threading.Event) -> threading.Thread:
    """
    Starts the playback thread and returns it.
    """
    thread = threading.Thread(
        target=playback_worker,
        args=(audio_queue, stop_event),
        daemon=True
    )
    thread.start()
    return thread
