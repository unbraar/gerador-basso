from flask import Flask, render_template, request, send_file
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'spreadsheet' in request.files:
            file = request.files['spreadsheet']
            df = pd.read_excel(file)
            output_paths = []
            for _, row in df.iterrows():
                data = {
                    "Origem": row.get("Origem", ""),
                    "Local de Coleta": row.get("Local de Coleta", ""),
                    "Destino": row.get("Destino", ""),
                    "Local de Entrega": row.get("Local de Entrega", ""),
                    "Produto": row.get("Produto", ""),
                    "Preço": row.get("Preço", ""),
                    "Restrição": row.get("Restrição", ""),
                }
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                filename = os.path.join(UPLOAD_FOLDER, f"output_{timestamp}.jpg")
                generate_image(data, filename)
                output_paths.append(filename)
            # Por simplicidade, retorna apenas o último arquivo gerado
            return send_file(output_paths[-1], as_attachment=True)
        else:
            data = {
                "Origem": request.form['origem'],
                "Local de Coleta": request.form['coleta'],
                "Destino": request.form['destino'],
                "Local de Entrega": request.form['entrega'],
                "Produto": request.form['produto'],
                "Preço": request.form['preco'],
                "Restrição": request.form['restricao'],
            }
            filename = os.path.join(UPLOAD_FOLDER, "output.jpg")
            generate_image(data, filename)
            return send_file(filename, as_attachment=True)
    return render_template('index.html')

def generate_image(data, filename):
    img = Image.new("RGB", (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_path = "arial.ttf"
    font = ImageFont.truetype(font_path, size=40)
    y = 100
    for key, value in data.items():
        draw.text((50, y), f"{key.upper()}: {value}", fill=(0, 0, 0), font=font)
        y += 80
    img.save(filename)

if __name__ == '__main__':
    app.run(debug=True)
