"""Contact sheet of book figures (for checking): contact.py out.png pattern..."""
import sys, glob
from PIL import Image
out = sys.argv[1]; files = []
for p in sys.argv[2:]:
    files += sorted(glob.glob(p))
ims = []
for f in files:
    im = Image.open(f).convert("RGB"); im.thumbnail((900, 520)); ims.append(im)
cols = 3; W = 900; H = 520
S = Image.new("RGB", (W * cols, H * ((len(ims) + cols - 1) // cols)), "white")
for k, im in enumerate(ims):
    S.paste(im, ((k % cols) * W, (k // cols) * H))
S.save(out); print(len(ims), "images")
