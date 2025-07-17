# Redeploy trigger
from flask import Flask, render_template, request
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    if request.method == "POST":
        data = request.form
        image_bytes = generate_image(
            data['origem'], data.get('local_coleta'), data['destino'],
            data.get('local_entrega'), data['preco'], data['produto'], data.get('restricao')
        )
        with open("static/output.jpg", "wb") as f:
            f.write(image_bytes.getbuffer())
        image_url = "/static/output.jpg"
    return render_template("index.html", image_url=image_url)

def generate_image(origem, coleta, destino, entrega, preco, produto, restricao):
    img = Image.new("RGB", (800, 1000), "white")
    draw = ImageDraw.Draw(img)

    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def draw_centered(text, y, size=40, color="black", bold=False):
        font = ImageFont.truetype(font_bold if bold else font_regular, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (800 - text_width) / 2
        draw.text((x, y), text, font=font, fill=color)

    draw.rectangle([(0, 140), (800, 200)], fill="black")
    draw_centered(origem.upper(), 150, 45, "white", True)
    if coleta:
        draw_centered(f"({coleta})", 210, 30)

    draw_centered("X", 280, 60, "red", True)

    draw.rectangle([(0, 350), (800, 410)], fill="black")
    draw_centered(destino.upper(), 360, 45, "white", True)
    if entrega:
        draw_centered(f"({entrega})", 420, 30)

    draw.rectangle([(275, 480), (525, 540)], fill="#00c853")
    draw_centered(preco, 490, 40, "black", True)

    draw_centered(produto.upper(), 560, 30, "red", True)
    if restricao:
        draw_centered(restricao.upper(), 650, 35, "#00c853", True)

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True, port=5000)
