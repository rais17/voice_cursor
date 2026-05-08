import heapq
import queue
import threading
import numpy as np
import scipy.signal as signal

SAMPLE_RATE = 24000  # consistent sample rate for all audio

def reduce_noise(audio, sample_rate):
    b, a = signal.butter(3, 0.05, btype='highpass', analog=False)
    return signal.filtfilt(b, a, audio)


class OrderedAudioQueue:
    def __init__(self):
        self._heap = []
        self._lock = threading.Lock()
        self._next_play = 0
        self._output_queue = queue.Queue()
        self._counter = 0  # tiebreaker

    def put(self, index: int, samples, sr: int = 24000):
        with self._lock:
            # Negative index = urgent, turant queue mein daalo
            if index < 0:
                self._output_queue.put((samples, sr))
                return
                
            heapq.heappush(self._heap, (index, self._counter, samples, sr))
            self._counter += 1
            while self._heap and self._heap[0][0] == self._next_play:
                _, _, chunk, sample_rate = heapq.heappop(self._heap)
                self._output_queue.put((chunk, sample_rate))
                self._next_play += 1

    def get(self, timeout=0.5):
        return self._output_queue.get(timeout=timeout)

    def put_sentinel(self):
        self._output_queue.put(None)