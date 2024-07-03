python -m venv .env
call .env\Scripts\activate
pip install torch==2.3.0+cu121 --index=https://download.pytorch.org/whl/cu121
pip install torchvision --index=https://download.pytorch.org/whl/cu121
pip install torchaudio --index=https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
