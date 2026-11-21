import io
import urllib.request
import zipfile

URL = "https://tranco-list.eu/top-1m.csv.zip"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
print("Downloading Tranco list...")
data = urllib.request.urlopen(req, timeout=120).read()

with zipfile.ZipFile(io.BytesIO(data)) as z:
    lines = z.read(z.namelist()[0]).decode().splitlines()[:60000]

with open("data/tranco_top.csv", "w") as f:
    f.write("\n".join(lines))

print(f"Saved {len(lines)} domains to data/tranco_top.csv")