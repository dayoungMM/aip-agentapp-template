#!/bin/zsh

if [ ! -d ".venv" ]; then
    echo "Creating Python 3.10 virtual environment in .venv..."
    python3.10 -m venv .venv
    chmod 777 .venv
else
    echo ".venv already exists. Skipping creation."
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Install adxp_cli-0.1.2"
pip install sktaip-api

echo "Install requirements.txt"
pip install -r requirements.txt


export PYTHONPATH=$(pwd):$PYTHONPATH
if [ -f .env ]; then
    echo "Export ENV"
    export $(grep -v '^#' .env | xargs)
fi

adxp-cli agent run --host 127.0.0.1 --port 28080


