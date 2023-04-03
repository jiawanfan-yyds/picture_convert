from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from PIL import Image
import os
import subprocess
import time
import urllib.parse
import sys

app = Flask(__name__)

# 设置上传文件保存的文件夹路径
upload_folder = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = upload_folder.replace('\\', '/')

# 设置输出文件夹路径
output_folder = os.path.join(os.getcwd(), 'output')
app.config['OUTPUT_FOLDER'] = output_folder.replace('\\', '/')

@app.route('/')
def index():
    return render_template('index.html', timestamp=int(time.time()))

@app.route('/convert', methods=['POST'])
def convert():
    # 获取所需参数
    output_format = request.form['output_format']
    output_folder = request.form['output_folder']
    timestamp = request.form['timestamp']

    # 检查输出路径是否存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取上传的文件
    input_files = request.files.getlist('input_files')

    # 处理每个上传的文件
    output_files = []
    for file in input_files:
        # 拼接输入和输出文件路径
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], timestamp + '_' + file.filename)
        output_filename = os.path.splitext(os.path.basename(file.filename))[0] + '.' + output_format
        output_path = os.path.join(output_folder, output_filename)

        # 保存上传的文件到指定路径
        file.save(input_path)

        # 如果是png格式的图片，转换为jpg格式并加上白色背景
        if file.filename.endswith('.png') and output_format == 'jpg':
            with Image.open(input_path) as image:
                image = image.convert('RGBA')
                background = Image.new('RGBA', image.size, (255, 255, 255))
                image = Image.alpha_composite(background, image)
                image = image.convert('RGB')
                image.save(output_path, quality=95)
        else:
            # 使用FFmpeg将文件转换为所需格式并保存到指定路径
            subprocess.call(['ffmpeg', '-i', input_path, output_path])

        # 添加输出文件路径到列表中
        output_file = os.path.splitext(file.filename)[0] + '.' + output_format
        output_path = os.path.join(output_folder, output_file)
        output_files.append(output_file)

        # 删除上传的文件
        try:
            os.remove(input_path)
        except FileNotFoundError:
            pass

    # 渲染 result.html 模板，并显示实际的输出路径
    return render_template('result.html', output_files=output_files)


@app.route('/output/<path:folder>')
def output(folder):
    output_folder = os.path.join(app.config['OUTPUT_FOLDER'], folder)
    output_files = os.listdir(output_folder)
    output_files = [os.path.abspath(os.path.join(output_folder, f)) for f in output_files]
    output_files = [urllib.parse.quote(f) for f in output_files]  # 对文件名进行URL编码
    return render_template('result.html', files=[f'file://{f}' for f in output_files])


if __name__ == '__main__':
    app.run(debug=True)
