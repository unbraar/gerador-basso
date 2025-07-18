
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "static"
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, "output")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def generate_image(data, filename):
    # Criação da imagem base
    img = Image.new("RGB", (1080, 1080), "white")
    draw = ImageDraw.Draw(img)

    # Fontes
    FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    # Logo
    logo_path = "static/logo_basso.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((280, 90))
        img.paste(logo, (int((1080 - 280) / 2), 30), logo)

    # Caixa central com sombra
    box_x0, box_y0, box_x1, box_y1 = 80, 150, 1000, 930
    shadow_color = (0, 100, 0, 100)
    draw.rectangle([box_x0+4, box_y0+4, box_x1+4, box_y1+4], fill=(0, 100, 0, 40))
    draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=(200, 255, 200, 240))

    # Campos com ícones simulados
    campos = [
        ("Origem", data.get("origem", ""), "🛫"),
        ("Local de Coleta", data.get("local_coleta", ""), "📍"),
        ("Destino", data.get("destino", ""), "🛬"),
        ("Local de Entrega", data.get("local_entrega", ""), "🏁"),
        ("Produto", data.get("produto", ""), "📦"),
        ("Preço", data.get("preco", ""), "💰"),
        ("Restrição", data.get("restricao", ""), "⚠️"),
    ]

    y = box_y0 + 40
    for label, value, icon in campos:
        if value:
            draw.rectangle([box_x0 + 20, y - 10, box_x1 - 20, y + 60], fill=(255,255,255), outline="white", width=3)
            txt = f"{icon} {label.upper()}: {value}"
            font = ImageFont.truetype(FONT_BOLD if label in ["Origem", "Destino", "Preço"] else FONT_REG,  size=40)
            draw.text((box_x0 + 40, y), txt, font=font, fill="black")
            y += 80

    output_path = os.path.join(OUTPUT_FOLDER, filename)
    img.save(output_path, "JPEG")
    return output_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = {
            "origem": request.form.get("origem"),
            "local_coleta": request.form.get("local_coleta"),
            "destino": request.form.get("destino"),
            "local_entrega": request.form.get("local_entrega"),
            "preco": request.form.get("preco"),
            "produto": request.form.get("produto"),
            "restricao": request.form.get("restricao"),
        }
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"output_{timestamp}.jpg"
        generate_image(data, filename)
        return render_template("index.html", image_url=f"/static/output/{filename}")
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["planilha"]
    if file.filename.endswith(".xlsx"):
        df = pd.read_excel(file)
        zip_name = f"lote_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        temp_img_paths = []

        for i, row in df.iterrows():
            data = row.to_dict()
            filename = f"img_{i+1}.jpg"
            path = generate_image(data, filename)
            temp_img_paths.append(path)

        import zipfile
        zip_path = os.path.join(OUTPUT_FOLDER, zip_name)
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_path in temp_img_paths:
                zipf.write(file_path, os.path.basename(file_path))
        return render_template("index.html", zip_url=f"/static/output/{zip_name}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
