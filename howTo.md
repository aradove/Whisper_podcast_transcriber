
sudo apt update && sudo apt install ffmpeg
conda create --name whisper
conda activate whisper
conda install python
conda update ffmpeg

# windows
C:\ProgramData\miniconda3\Scripts\activate.bat C:\ProgramData\miniconda3
conda activate whisper
pip install streamlit

### and install cuda
https://developer.nvidia.com/cuda-12-1-0-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_local
### in a powershell admin prompt
python -m pip uninstall torch
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121



## install whisper
pip uninstall whisper
pip install git+https://github.com/openai/whisper.git 

# pytorch https://pytorch.org/ Cuda 11.6
conda install pytorch torchvision torchaudio cudatoolkit=11.6 -c pytorch -c conda-forge

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
export PATH="$HOME/.cargo/bin:$PATH"
pip install setuptools-rust

pip install git+https://github.com/openai/whisper.git 

whisper avsnitt\ 476v2.mp3 --language Swedish
