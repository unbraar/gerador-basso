
from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd
import zipfile
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files["planilha"]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pasta_saida = os.path.join(UPLOAD_FOLDER, f"lote_{timestamp}")
    os.makedirs(pasta_saida, exist_ok=True)

    df = pd.read_excel(arquivo)

    for idx, row in df.iterrows():
        img = Image.new("RGB", (1080, 1350), "white")
        draw = ImageDraw.Draw(img)
        font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_bold, 40)
        y = 150
        for campo in ["origem", "coleta", "destino", "entrega", "produto", "preco", "restricao"]:
            texto = f"{campo.upper()}: {str(row.get(campo, '')).strip()}"
            draw.text((80, y), texto, font=font, fill="black")
            y += 100

        img_path = os.path.join(pasta_saida, f"imagem_{idx+1}.png")
        img.save(img_path)

    zip_path = os.path.join(UPLOAD_FOLDER, f"imagens_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for nome_img in os.listdir(pasta_saida):
            zipf.write(os.path.join(pasta_saida, nome_img), arcname=nome_img)

    return render_template("index.html", zip_url="/" + zip_path)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)
