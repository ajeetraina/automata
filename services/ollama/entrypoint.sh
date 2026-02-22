#!/bin/bash
ollama serve &
OLLAMA_PID=$!
until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do sleep 2; done
echo "Ollama ready!"
MODEL="llama3.3:70b"
if ! ollama list | grep -q "$MODEL"; then
    echo "Pulling $MODEL..."
    ollama pull $MODEL
fi
wait $OLLAMA_PID
