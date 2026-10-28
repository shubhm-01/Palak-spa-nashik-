from html.parser import HTMLParser
from pathlib import Path
import re
import sys

html_path = Path("index.html")
if not html_path.exists():
    sys.exit("FAIL: index.html is missing")
html = html_path.read_text(encoding="utf-8")

class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.title = False
        self.lang = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang") == "en"
        if tag == "title":
            self.title = True
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href", "").startswith("#"):
            self.links.append(attrs["href"][1:])

parser = SiteParser()
parser.feed(html)
parser.close()

checks = {
    "document declares English language": parser.lang,
    "page title exists": "<title>" in html and "</title>" in html,
    "description metadata exists": 'name="description"' in html,
    "responsive viewport exists": 'name="viewport"' in html,
    "WhatsApp contact link exists": "https://wa.me/917541946172" in html,
    "phone contact link exists": "tel:+917541946172" in html,
    "Google Maps directions exist": "maps.app.goo.gl/G5SvuWVS5JEeSsjZ8" in html,
    "services section exists": 'id="services"' in parser.ids,
    "pricing section exists": 'id="pricing"' in parser.ids,
    "booking section exists": 'id="booking"' in parser.ids,
    "FAQ section exists": 'id="faq"' in parser.ids,
    "booking form has required validation": 'id="booking-form"' in html and 'required' in html,
    "sitemap exists": Path("sitemap.xml").exists(),
    "robots file exists": Path("robots.txt").exists(),
}
missing_anchors = sorted(set(parser.links) - parser.ids)
for label, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + label)
if missing_anchors:
    print("FAIL: missing internal anchors: " + ", ".join(missing_anchors))
else:
    print("PASS: internal anchor links resolve")
if not all(checks.values()) or missing_anchors:
    sys.exit(1)
print("All static-site checks passed.")
