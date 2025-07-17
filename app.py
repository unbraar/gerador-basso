from flask import Flask, render_template, request, send_file, url_for
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    if request.method == "POST":
        try:
            data = request.form
            image_bytes = generate_image(
                data['origem'], data.get('local_coleta'), data['destino'],
                data.get('local_entrega'), data['preco'], data['produto'], data.get('restricao')
            )
            os.makedirs("static", exist_ok=True)
            with open("static/output.jpg", "wb") as f:
                f.write(image_bytes.getbuffer())
            image_url = url_for('static', filename='output.jpg')
        except Exception as e:
            return f"Erro ao gerar imagem: {e}", 500
    return render_template("index.html", image_url=image_url)

def generate_image(origem, coleta, destino, entrega, preco, produto, restricao):
    img = Image.new("RGB", (800, 1100), "white")
    draw = ImageDraw.Draw(img)

    try:
        logo = Image.open("static/logo.jpg").convert("RGBA")
        logo = logo.resize((250, 250))
        img.paste(logo, (int((800 - logo.width) / 2), 20))
    except:
        pass

    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def draw_centered(text, y, size=40, color="black", bold=False):
        try:
            font = ImageFont.truetype(font_bold if bold else font_regular, size)
        except IOError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (800 - text_width) / 2
        draw.text((x, y), text, font=font, fill=color)

    offset = 290
    draw.rectangle([(0, offset), (800, offset + 60)], fill="black")
    draw_centered(origem.upper(), offset + 10, 45, "white", True)
    if coleta:
        draw_centered(f"({coleta})", offset + 70, 30)

    draw_centered("X", offset + 130, 60, "red", True)

    draw.rectangle([(0, offset + 200), (800, offset + 260)], fill="black")
    draw_centered(destino.upper(), offset + 210, 45, "white", True)
    if entrega:
        draw_centered(f"({entrega})", offset + 270, 30)

    draw.rectangle([(275, offset + 330), (525, offset + 390)], fill="#00c853")
    draw_centered(preco, offset + 340, 40, "black", True)

    draw_centered(produto.upper(), offset + 420, 30, "red", True)
    if restricao:
        draw_centered(restricao.upper(), offset + 500, 35, "#00c853", True)

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True, port=5000)
