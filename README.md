# Voice Cursor

Voice Cursor is an AI coding assistant that operates via voice, helping developers interact with their codebase using natural language. It leverages advanced voice recognition and synthesis technologies to provide a seamless user experience.

## Features
- Voice-activated coding assistance
- Real-time speech-to-text transcription
- Text-to-speech synthesis for responses
- Integration with popular AI models and tools

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd voice-cursor
   ```

2. **Install Dependencies**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the root directory and add the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_uri
   ```

4. **Configure Audio Devices**
   Update `FFMPEG_PATH` and `MIC_DEVICE` in `src/config/__init__.py` to match your system's configuration.

## Project Structure

The project is organized as follows:

- `src/` - Contains the source code for Voice Cursor.
  - `agents/` - Houses the AI agent logic.
  - `config/` - Configuration files and environment setup.
  - `io/` - Handles input/output operations like audio processing.
  - `prompt/` - Contains prompt templates and system messages.
  - `tools/` - Utility tools used by the AI agent.
  - `types/` - Type definitions for better code clarity.
- `README.md` - Project documentation.

## Usage

Run the application using:
```bash
python src/main.py
```

Speak into your microphone when prompted. The system will transcribe your speech and provide AI-driven responses.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [OpenAI](https://openai.com/)
- [Langchain](https://langchain.com/)
- [Kokoro](https://kokoro.com/)