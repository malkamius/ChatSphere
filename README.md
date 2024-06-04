# ChatSphere
 
Submit chats to a database where a background process handles running them against an LLM

# Dependencies
 You may need to install the cuda 12.1 framework from <br />
 https://developer.nvidia.com/cuda-downloads?target_os=Windows <br />
# Python environment
Create a virtual environment (optional but recommended): <br />
<br />
This keeps your installations and project separate from your main Python installation. <br />
<br />
<br />
On a command line go to where you want to create the python environment <br />
python -m venv myenv <br />
From the same command line run  <br />
myenv\Scripts\activate.bat <br />
<br />
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 <br />
pip install transformers accelerate bitsandbytes <br />
pip install Flask <br />

navigate to the chatsphere-py folder on the command line <br />
python background.py <br />
