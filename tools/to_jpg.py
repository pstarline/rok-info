"""Usage: python3 tools/to_jpg.py <slug>  -- converts static/img/<slug>/N.png to N.jpg and removes the png."""
import sys, os
from PIL import Image
d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'img', sys.argv[1])
for f in sorted(os.listdir(d)):
    if f.endswith('.png'):
        Image.open(os.path.join(d, f)).convert('RGB').save(os.path.join(d, f[:-4] + '.jpg'), quality=84, optimize=True)
        os.remove(os.path.join(d, f))
print(sorted(os.listdir(d)))
