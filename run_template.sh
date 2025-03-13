#!/bin/zsh

if [ ! -d "../sktaip_api_build/.venv" ]; then
    echo "Creating Python 3.10 virtual environment in .venv..."
    python3.10 -m venv ../sktaip_api_build/.venv
else
    echo "../sktaip_api_build/.venv already exists. Skipping creation."
fi

echo "Activating virtual environment..."
source ../sktaip_api_build/.venv/bin/activate

echo "Install sktaip_api-0.1.2"
pip install ../../agents_server_pkg/dist/sktaip_api-0.1.2-py3-none-any.whl

echo "Install requirements.txt"
pip install -r requirements.txt


export PYTHONPATH=$(pwd):$PYTHONPATH
if [ -f .env ]; then
    echo "Export ENV"
    export $(grep -v '^#' .env | xargs)
fi

cd ..
python template/react_agent/main.py


