#!/usr/bin/env python3
"""
Speaker Assistant CLI - Command-line interface to connect to LLM agent and speak responses

Usage:
    # Single query
    python cli.py "Your question here"

    # Interactive mode
    python cli.py

    # With custom Ollama endpoint
    python cli.py --url http://localhost:11434 "Question"

The script:
1. Takes text input from command line
2. Sends it to the Ollama endpoint (default: localhost:11434)
3. Speaks the LLM response using Piper TTS
"""

import sys
import os
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import json
import subprocess
import requests


def load_config():
    """Load configuration from config.env"""
    config_path = Path(__file__).resolve().parent.parent / "config" / "config.env"
    config = {}
    if config_path.exists():
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"')
    return config


def speak_text(text, piper_path, tts_model):
    """Speak the given text using Piper TTS"""
    if not text:
        return

    # Create a temporary file for the text
    text_file = Path(__file__).resolve().parent.parent / "audio" / "temp_speech.txt"
    text_file.parent.mkdir(exist_ok=True)

    with open(text_file, 'w') as f:
        f.write(text)

    # Use Piper to synthesize speech
    cmd = [
        piper_path,
        "--model", tts_model,
        "--input", str(text_file),
        "--output-raw"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()

        if process.returncode == 0:
            # Play the audio
            play_cmd = ["aplay", "-q", "-f", "S16_LE", "-r", "22050"]
            play_process = subprocess.Popen(
                play_cmd,
                stdin=subprocess.PIPE
            )
            play_process.communicate(input=output)
        else:
            print(f"Error in TTS: {error.decode()}", file=sys.stderr)
    except Exception as e:
        print(f"Error speaking text: {e}", file=sys.stderr)


def query_ollama(prompt, endpoint, model):
    """Send query to Ollama endpoint and get response"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 512
            }
        }
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        else:
            print(f"Error: Ollama endpoint returned {response.status_code}", file=sys.stderr)
            print(f"Response: {response.text}", file=sys.stderr)
            return None
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Ollama at {endpoint}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error querying Ollama: {e}", file=sys.stderr)
        return None


def interactive_mode(endpoint, model, piper_path, tts_model):
    """Interactive mode - continuous conversation"""
    print("=" * 50)
    print("  Speaker Assistant - Interactive Mode")
    print("=" * 50)
    print("Type 'exit' or 'quit' to stop.")
    print(f"Connected to Ollama at: {endpoint}")
    print(f"Model: {model}")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break

            print(f"Thinking...")

            # Query Ollama
            response = query_ollama(user_input, endpoint, model)

            if response:
                print(f"\nAssistant: {response}")

                # Speak the response
                print("[Speaking response...]")
                speak_text(response, piper_path, tts_model)
            else:
                print("Failed to get response from Ollama.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Speaker Assistant CLI - Connect to Ollama and speak responses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Interactive mode
    python cli.py

    # Single query
    python cli.py "What is the capital of France?"

    # With custom endpoint
    python cli.py --url http://192.168.1.100:11434 "Hello!"
        """
    )

    parser.add_argument(
        'query',
        nargs='*',
        help='Text to process (if no query provided, enters interactive mode)'
    )

    parser.add_argument(
        '--url',
        default='http://localhost:11434/api/generate',
        help='Ollama endpoint URL (default: http://localhost:11434/api/generate)'
    )

    parser.add_argument(
        '--model',
        default=None,
        help='Ollama model name (default: qwen2.5:1.5b-instruct-q4_0)'
    )

    parser.add_argument(
        '--piper',
        default=None,
        help='Path to Piper binary'
    )

    parser.add_argument(
        '--tts-model',
        default=None,
        help='Path to TTS model'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Get settings from config or CLI args
    endpoint = args.url
    model = args.model or config.get('MODEL', 'qwen2.5:1.5b-instruct-q4_0')
    piper_path = args.piper or config.get('PIPER', '../tts/piper/piper')
    tts_model = args.tts_model or config.get('TTS_MODEL', '../tts/voice/libritts_r/en_US-libritts_r-medium.onnx')

    # Resolve relative paths
    base_path = Path(__file__).resolve().parent.parent
    if not Path(piper_path).is_absolute():
        piper_path = base_path / piper_path
    if not Path(tts_model).is_absolute():
        tts_model = base_path / tts_model

    # Check if Piper exists
    if not Path(piper_path).exists():
        print(f"Error: Piper binary not found at {piper_path}", file=sys.stderr)
        sys.exit(1)

    if not Path(tts_model).exists():
        print(f"Error: TTS model not found at {tts_model}", file=sys.stderr)
        sys.exit(1)

    if args.query:
        # Single query mode
        query = ' '.join(args.query)
        print(f"Query: {query}")
        print("Thinking...")

        response = query_ollama(query, endpoint, model)

        if response:
            print(f"\nAssistant: {response}")
            print("\n[Speaking response...]")
            speak_text(response, str(piper_path), str(tts_model))
        else:
            print("Failed to get response from Ollama.")
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode(endpoint, model, str(piper_path), str(tts_model))


if __name__ == "__main__":
    main()
