from pathlib import Path
from PIL import Image, ImageDraw

out = Path("../extension/icons")
out.mkdir(parents=True, exist_ok=True)

for size in (16, 32, 48, 128):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 4, fill=(109, 124, 255, 255))
    s = size
    shield = [(s*.5, s*.15), (s*.8, s*.28), (s*.76, s*.6), (s*.5, s*.85), (s*.24, s*.6), (s*.2, s*.28)]
    d.polygon(shield, fill=(255, 255, 255, 255))
    img.save(out / f"icon{size}.png")
print("Icons created")