
import asyncio
import queue
import threading
import uuid
import re
from concurrent.futures import ThreadPoolExecutor

from src.agents.voice_agent import voice_agent
from src.io.stt import transcribe_streaming
from src.io.tts import synthesize_to_queue
from src.io.playback import start_playback_thread
from src.io.audio_utils import OrderedAudioQueue

SENTENCE_END = re.compile(r'(?<=[.!?,:;])\s')
# SENTENCE_END = re.compile(r'(?<=[.!?])\s')
executor = ThreadPoolExecutor(max_workers=3)  # synthesis threads
WORD_THRESHOLD = 6


def fire_tts(sentence: str, audio_queue: queue.Queue, futures: list, sentence_index: int):
    """Synthesize a sentence in a background thread."""
    if sentence.strip():
        f = executor.submit(synthesize_to_queue, sentence, audio_queue, sentence_index)
        futures.append(f)

def handle_chat_model_stream(event, token_buffer, full_reply, futures, audio_queue, sentence_index):
    chunk = event["data"]["chunk"]
    token = extract_token(chunk)

    if not token.strip():
        return token_buffer, full_reply, sentence_index

    token_buffer += token
    full_reply += token

    # Sentence boundary check
    parts = SENTENCE_END.split(token_buffer, maxsplit=1)
    if len(parts) > 1:
        sentence = parts[0].strip()
        token_buffer = parts[1]
        if sentence:
            fire_tts(sentence, audio_queue, futures, sentence_index)
            sentence_index += 1
    
    # Word threshold — boundary ka wait mat karo
    elif len(token_buffer.split()) >= WORD_THRESHOLD:
        sentence = token_buffer.strip()
        token_buffer = ""
        fire_tts(sentence, audio_queue, futures, sentence_index)
        sentence_index += 1

    return token_buffer, full_reply, sentence_index


def extract_token(chunk):
    if isinstance(chunk.content, str):
        return chunk.content
    elif isinstance(chunk.content, list):
        return "".join(
            block.get("text", "")
            for block in chunk.content
            if isinstance(block, dict)
        )
    return ""

TOOL_ANNOUNCEMENT_INDEX = -1

def process_tool_event(event, tool_announced, futures, audio_queue, sentence_index):
    tool_name = event["name"]
    print(f"\n[Tool: {tool_name}]")

    if not tool_announced:
        fire_tts("Let me check that for you.", audio_queue, futures, TOOL_ANNOUNCEMENT_INDEX)
        tool_announced = True
    return tool_announced


async def stream_response(user_text: str, config: dict, hss: bool = False, hqc: bool = False):
    audio_queue = OrderedAudioQueue()
    stop_event = threading.Event()
    futures = []  # track all synthesis futures
    sentence_index = 0  # counter

    # Start playback thread
    playback_thread = start_playback_thread(audio_queue, stop_event)

    token_buffer = ""
    full_reply = ""
    tool_announced = False

    async for event in voice_agent.astream_events(
        {"messages": [{"role": "user", "content": user_text}]},
        config=config,
        version="v2", 
        # hqc=hqc,
        # hss=hss
    ):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            tool_announced = False
            token_buffer, full_reply, sentence_index = handle_chat_model_stream(
                event, token_buffer, full_reply, futures, audio_queue, sentence_index
            )

        elif kind == "on_tool_start":
            tool_announced = process_tool_event(event, tool_announced, futures, audio_queue, sentence_index)

        elif kind == "on_tool_end":
            print(f"\n[Tool done]")

    if token_buffer.strip():
        fire_tts(token_buffer.strip(), audio_queue, futures, sentence_index)

    # Alag thread mein futures monitor karo
    for f in futures:
        f.result()

    # Tab sentinel
    audio_queue.put_sentinel()
    playback_thread.join()


def run():
    print("Voice Cursor started. Speak to interact.\n")

    workspace = input("Enter project path (or press Enter to skip): ").strip()
    if workspace:
        from src.workspace import workspace_manager
        result = workspace_manager.set(workspace)
        print(result)

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        # user_text = transcribe_streaming()
        user_text = input("Please enter your message:\nYou: ").strip()  # fallback to text input
        if not user_text.strip():
            continue

        print(f"\nYou: {user_text}")
        print("Cursor: ", end="")
        asyncio.run(stream_response(user_text, config))


if __name__ == "__main__":
    run()
