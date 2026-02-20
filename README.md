# Speaker Assistant

A command-line AI assistant that connects to an LLM agent and speaks responses using Text-to-Speech (TTS). This is a text-only version of the voice-assistant project, designed for scenarios where you want to interact with an AI agent via text input and hear spoken responses.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Quick Start](#quick-start)
5. [Usage](#usage)
6. [Configuration](#configuration)
7. [Connecting to LLM](#connecting-to-llm)
8. [Requirements](#requirements)

## Overview

Speaker Assistant allows you to:

- Type text queries in the command line
- Send queries to a remote LLM agent (like LLaMA)
- Hear the AI's responses spoken aloud using Piper TTS

This is useful when:

- You want a hands-free experience (just listening)
- You're using a headless server
- You prefer typing but want audio feedback
- You want to integrate with other text-based systems

## Features

- **Command-line Interface**: Interactive or single-query mode
- **TTS Integration**: Uses Piper for natural-sounding speech synthesis
- **LLM Connectivity**: Connects to any HTTP-based LLM endpoint
- **Lightweight**: No microphone or audio recording dependencies

## Project Structure

```
speaker-assistant/
├── config/
│   └── config.env          # Configuration file
├── src/
│   ├── bin/
│   │   ├── cli.py          # Main Python CLI script
│   │   └── speak.sh        # Simple shell script for TTS only
│   ├── llm/
│   │   └── bin/            # LLaMA binaries (if running locally)
│   ├── tts/
│   │   ├── piper/          # Piper TTS binary
│   │   └── voice/          # TTS voice models
│   └── rag/                # RAG components (optional)
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
└── README.md             # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Assistant

Edit `config/config.env` to set your LLM endpoint and TTS settings:

```bash
# LLaMA endpoint (change IP/port to your server)
LAPTOP_IP="192.168.231.189"
PORT=8080
LLAMA_ENDPOINT="http://$LAPTOP_IP:$PORT/completion"

# Piper TTS settings
PIPER="../tts/piper/piper"
TTS_MODEL="../tts/voice/libritts_r/en_US-libritts_r-medium.onnx"
```

### 3. Run the Assistant

**Interactive Mode:**

```bash
cd src/bin
python cli.py
```

**Single Query Mode:**

```bash
cd src/bin
python cli.py "What is machine learning?"
```

## Usage

### Interactive Mode

Run without arguments to enter interactive mode:

```bash
$ python cli.py
==================================================
  Speaker Assistant - Interactive Mode
==================================================
Type 'exit' or 'quit' to stop.
Connected to LLM at: http://localhost:8080/completion
--------------------------------------------------

You: Tell me a joke

Assistant: Why did the programmer quit his job?
Because he didn't get arrays.

[Speaking response...]

You: exit
Goodbye!
```

### Single Query

Pass your query as arguments:

```bash
$ python cli.py "What is the capital of Italy?"
Query: What is the capital of Italy?
Thinking...
Assistant: The capital of Italy is Rome.

[Speaking response...]
```

### Custom LLM Endpoint

Specify a different LLM server:

```bash
$ python cli.py --url http://192.168.1.100:8080/completion "Hello!"
```

### TTS Only Mode

If you just want to speak text without connecting to an LLM:

```bash
# Using shell script
$ ./speak.sh "Hello, world!"

# Interactive TTS mode
$ ./speak.sh
🎤 Speaker Assistant - Interactive Mode
Type 'exit' or 'quit' to stop.
----------------------------------------
> Hello there!
[🔊 Speaking]: Hello there!
> exit
Goodbye!
```

## Configuration

### Environment Variables

| Variable         | Description             | Default                                                |
| ---------------- | ----------------------- | ------------------------------------------------------ |
| `LLAMA_ENDPOINT` | URL of the LLM server   | `http://localhost:8080/completion`                     |
| `PIPER`          | Path to Piper binary    | `../tts/piper/piper`                                   |
| `TTS_MODEL`      | Path to TTS voice model | `../tts/voice/libritts_r/en_US-libritts_r-medium.onnx` |

### Piper TTS Setup

1. Download Piper from: https://github.com/rhasspy/piper
2. Place the binary in `src/tts/piper/piper`
3. Download a voice model (e.g., en_US-libritts_r-medium)
4. Place the `.onnx` and `.onnx.json` files in `src/tts/voice/libritts_r/`

## Connecting to LLM

The assistant expects an HTTP server running LLaMA or compatible model with an endpoint that accepts JSON:

```json
POST /completion
Content-Type: application/json

{
    "prompt": "<|system|>You are helpful.<|user|>Hello<|assistant|>",
    "n_predict": 256
}
```

Response format:

```json
{
  "content": "Hello! How can I help you today?"
}
```

### Setting Up LLaMA Server

If you need to set up an LLaMA server:

```bash
# Using llama.cpp
./llama-server -m your-model.gguf --port 8080
```

## Requirements

- Python 3.8+
- Piper TTS binary
- LLaMA-compatible server running
- `aplay` (Linux) or compatible audio player for TTS output
- Python packages (from requirements.txt):
  - requests

## License

Same as the original voice-assistant project.

---

Built as a companion to the Voice Assistant project, focusing on the "speaking" half of the voice interaction pipeline.
