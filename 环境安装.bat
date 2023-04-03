@echo off
chcp 65001

echo Creating virtual environment...
python -m venv picture2picture
echo Virtual environment created.

echo Activating environment...
call picture2picture\Scripts\activate.bat
echo Environment is activated.

python.exe -m pip install --upgrade pip

cd /d "C:\Users\Admin\Desktop\图片格式转化器"

pip install -r requirements.txt
