from flask import Flask, render_template, request, url_for
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
    img = Image.open("static/base.jpg").convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    except:
        font_bold = font_regular = None

    def draw_centered(text, y, size=26, color="black", bold=False, shadow=True):
        try:
            font = ImageFont.truetype(font_bold if bold else font_regular, size)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) / 2
        if shadow:
            draw.text((x+1, y+1), text, font=font, fill="gray")
        draw.text((x, y), text, font=font, fill=color)

    y_offset = 320
    draw_centered(origem.upper(), y_offset, 30, "#1b5e20", True)
    if coleta:
        draw_centered(f"({coleta})", y_offset + 32, 22, "#444")

    draw_centered("⇅", y_offset + 70, 34, "#2e7d32", True)

    draw_centered(destino.upper(), y_offset + 115, 30, "#1b5e20", True)
    if entrega:
        draw_centered(f"({entrega})", y_offset + 147, 22, "#444")

    draw_centered(produto.upper(), y_offset + 190, 26, "black", True)

    draw.rectangle([(140, y_offset + 230), (img.width - 140, y_offset + 270)], fill="#a5d6a7")
    draw_centered(preco, y_offset + 235, 26, "#1b5e20", True, shadow=False)

    if restricao:
        draw_centered(restricao.upper(), y_offset + 290, 20, "#00c853", False)

    # Rodapé institucional
    draw.rectangle([(0, img.height - 40), (img.width, img.height)], fill="#1b5e20")
    try:
        font_footer = ImageFont.truetype(font_regular, 16)
    except:
        font_footer = ImageFont.load_default()
    text = "Basso Logística e Transportes • www.logbasso.com.br • (55) 99999-9999"
    bbox = draw.textbbox((0, 0), text, font=font_footer)
    text_width = bbox[2] - bbox[0]
    draw.text(((img.width - text_width) / 2, img.height - 30), text, font=font_footer, fill="white")

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True, port=5000)
