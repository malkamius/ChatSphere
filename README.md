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
install.bat should handle setting up an environment under windows<br />
<br />
<br />
run_lmnode.bat should run the backend process that responds to requests<br />
run_webserver.bat should run the webserver that acts as an interface<br />
<br />
There are two .sql files with scripts to setup the databases in a mysql server.<br />
shared\config.py needs to be updated with the MySQL information<br />
