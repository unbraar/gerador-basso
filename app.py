import os
from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import datetime

app = Flask(__name__)

FONT_BOLD = "static/Roboto-Bold.ttf"
FONT_REG = "static/Roboto-Regular.ttf"

def generate_image(data, filename):
    image = Image.new("RGB", (1080, 1080), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    # Central border
    draw.rectangle([100, 250, 980, 950], fill=(200, 255, 200), outline=(0, 100, 0))
    y = 270
    for label, value in data.items():
        text = f"{label.upper()}: {value}"
        font = ImageFont.truetype(FONT_BOLD if label in ["Origem", "Destino", "Preço"] else FONT_REG, size=36)
        draw.text((120, y), text, fill="black", font=font)
        y += 90
    image.save(filename)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" in request.files:
            df = pd.read_excel(request.files["file"])
            folder = "static/batch"
            os.makedirs(folder, exist_ok=True)
            for i, row in df.iterrows():
                data = row.to_dict()
                filename = os.path.join(folder, f"img_{i}.jpg")
                generate_image(data, filename)
            return send_file("static/batch.zip", as_attachment=True)
        else:
            data = {
                "Origem": request.form["origem"],
                "Local de Coleta": request.form["coleta"],
                "Destino": request.form["destino"],
                "Local de Entrega": request.form["entrega"],
                "Produto": request.form["produto"],
                "Preço": request.form["preco"],
                "Restrição": request.form["restricao"],
            }
            filename = "static/output.jpg"
            generate_image(data, filename)
            return render_template("index.html", image_url=filename)
    return render_template("index.html", image_url=None)

if __name__ == "__main__":
    app.run(debug=True)
