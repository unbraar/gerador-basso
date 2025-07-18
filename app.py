
from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd
import zipfile
import io
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def desenhar_imagem(origem, coleta, destino, entrega, preco, produto, restricao):
    img = Image.new("RGB", (1080, 1350), "white")
    draw = ImageDraw.Draw(img)
    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_bold, 40)
    y = 150
    for label, value in [("ORIGEM", origem), ("COLETA", coleta), ("DESTINO", destino),
                         ("ENTREGA", entrega), ("PRODUTO", produto), ("PREÇO", preco), ("RESTRIÇÃO", restricao)]:
        if value:
            draw.text((80, y), f"{label}: {value}", font=font, fill="black")
            y += 100
    return img

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form
        imagem = desenhar_imagem(
            data['origem'], data.get('local_coleta'), data['destino'],
            data.get('local_entrega'), data['preco'], data['produto'], data.get('restricao')
        )
        img_path = os.path.join(UPLOAD_FOLDER, "output.jpg")
        imagem.save(img_path)
        return render_template("index.html", image_url=f"/{img_path}")
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files["planilha"]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pasta_saida = os.path.join(UPLOAD_FOLDER, f"lote_{timestamp}")
    os.makedirs(pasta_saida, exist_ok=True)

    df = pd.read_excel(arquivo)

    for idx, row in df.iterrows():
        imagem = desenhar_imagem(
            row.get("origem", ""), row.get("coleta", ""), row.get("destino", ""),
            row.get("entrega", ""), row.get("preco", ""), row.get("produto", ""), row.get("restricao", "")
        )
        img_path = os.path.join(pasta_saida, f"imagem_{idx+1}.png")
        imagem.save(img_path)

    zip_path = os.path.join(UPLOAD_FOLDER, f"imagens_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for nome_img in os.listdir(pasta_saida):
            zipf.write(os.path.join(pasta_saida, nome_img), arcname=nome_img)

    return render_template("index.html", zip_url="/" + zip_path)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)
