"""Make the PDF's links to the decks and code pages relative to the PDF itself, so they keep working when
the book folder (PDF + decks/ + code/) is moved or shared. Chrome writes absolute file:// links."""
import sys
from pathlib import Path
import pypdf
from pypdf.generic import NameObject, TextStringObject

pdf = Path(sys.argv[1])
base = "file://" + str(pdf.parent.resolve()) + "/"
r = pypdf.PdfReader(str(pdf)); w = pypdf.PdfWriter(clone_from=r)
n = 0
for page in w.pages:
    for a in page.get("/Annots") or []:
        o = a.get_object()
        act = o.get("/A")
        if act and "/URI" in act and str(act["/URI"]).startswith(base):
            act[NameObject("/URI")] = TextStringObject(str(act["/URI"])[len(base):])
            n += 1
w.write(str(pdf))
print(f"relinked {n} links in {pdf.name}")
