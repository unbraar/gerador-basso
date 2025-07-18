from flask import Flask, render_template, request, send_file, url_for
from PIL import Image, ImageDraw, ImageFont
import io, os, pandas as pd, zipfile
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_image(origem, coleta, destino, entrega, preco, produto, restricao, index=None):
    img = Image.open(f"{STATIC_FOLDER}/base.jpg").convert("RGB")
    draw = ImageDraw.Draw(img)
    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def font(size=24, bold=False):
        try: return ImageFont.truetype(font_bold if bold else font_regular, size)
        except: return ImageFont.load_default()

    def draw_centered_boxed(text, y, width=img.width-100, height=40, bg="#dcedc8", color="black", fsize=24, bold=True):
        box_x = (img.width - width) // 2
        draw.rectangle([box_x, y, box_x+width, y+height], fill=bg, outline="#a5d6a7")
        f = font(fsize, bold)
        bbox = draw.textbbox((0, 0), text, font=f)
        tx = (img.width - (bbox[2] - bbox[0])) // 2
        draw.text((tx, y + (height - (bbox[3] - bbox[1])) // 2), text, font=f, fill=color)

    y = 310
    draw_centered_boxed(origem.upper(), y, bg="#c8e6c9", fsize=26)
    if coleta: draw_centered_boxed(f"COLETA: {coleta}", y+50, bg="#e0f2f1", fsize=20, bold=True)
    draw_centered_boxed(destino.upper(), y+110, bg="#c8e6c9", fsize=26)
    if entrega: draw_centered_boxed(f"ENTREGA: {entrega}", y+160, bg="#e0f2f1", fsize=20, bold=True)
    draw_centered_boxed(f"PRODUTO: {produto}", y+220, bg="#fffde7", fsize=22, bold=False)
    draw_centered_boxed(f"VALOR: {preco}", y+275, bg="#a5d6a7", fsize=26, bold=True)
    if restricao: draw_centered_boxed(restricao.upper(), y+330, bg="#f1f8e9", fsize=18, bold=False)

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    if request.method == "POST" and 'origem' in request.form:
        data = request.form
        image_bytes = generate_image(
            data['origem'], data.get('local_coleta'), data['destino'],
            data.get('local_entrega'), data['preco'], data['produto'], data.get('restricao')
        )
        with open(f"static/output.jpg", "wb") as f:
            f.write(image_bytes.getbuffer())
        image_url = url_for('static', filename='output.jpg')
    return render_template("index.html", image_url=image_url)

@app.route("/upload", methods=["POST"])
def upload():
    if 'planilha' not in request.files: return "Nenhum arquivo enviado.", 400
    file = request.files['planilha']
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filepath = os.path.join(UPLOAD_FOLDER, f"lote_{timestamp}.xlsx")
    file.save(filepath)
    df = pd.read_excel(filepath)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for i, row in df.iterrows():
            img_bytes = generate_image(
                str(row.get("origem", "")), str(row.get("local_coleta", "")),
                str(row.get("destino", "")), str(row.get("local_entrega", "")),
                str(row.get("preco", "")), str(row.get("produto", "")), str(row.get("restricao", "")), i
            )
            zf.writestr(f"imagem_{i+1}.jpg", img_bytes.getvalue())
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="imagens_basso.zip")

if __name__ == "__main__":
    app.run(debug=True)
