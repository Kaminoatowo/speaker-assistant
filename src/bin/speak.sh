#!/bin/bash

# Speaker Assistant CLI - Text to Speech
# Usage: ./speak.sh "Your text here"
# Or interactive mode: ./speak.sh (without arguments)

# Load configuration
source ../../config/config.env

PIPER="$PIPER"
TTS_MODEL="$TTS_MODEL"

if [ -z "$PIPER" ] || [ -z "$TTS_MODEL" ]; then
    echo "Error: Configuration not loaded. Run from src/bin directory."
    exit 1
fi

# Function to speak text
speak() {
    local text="$1"
    if [ -z "$text" ]; then
        echo "Error: No text provided to speak."
        return 1
    fi
    echo "[🔊 Speaking]: $text"
    echo "$text" | "$PIPER" --model "$TTS_MODEL" --output-raw 2>/dev/null | aplay -q -f S16_LE -r 22050
}

# Interactive mode or single query
if [ $# -eq 0 ]; then
    echo "🎤 Speaker Assistant - Interactive Mode"
    echo "Type 'exit' or 'quit' to stop."
    echo "----------------------------------------"
    while true; do
        echo -n "> "
        read -r user_input
        if [ "$user_input" = "exit" ] || [ "$user_input" = "quit" ]; then
            echo "Goodbye!"
            break
        fi
        if [ -n "$user_input" ]; then
            speak "$user_input"
        fi
    done
else
    # Single query mode
    speak "$*"
fi
