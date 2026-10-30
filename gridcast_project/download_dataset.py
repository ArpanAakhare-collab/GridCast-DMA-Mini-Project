"""Download the official UCI Individual Household Electric Power Consumption dataset."""
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile
import io

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
URL = "https://archive.ics.uci.edu/static/public/235/individual+household+electric+power+consumption.zip"

try:
    print("Downloading the official UCI dataset (about 20 MB compressed)...")
    request = Request(URL, headers={"User-Agent": "GridCast-DMA-Student-Project/1.0"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()
    with ZipFile(io.BytesIO(payload)) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith("household_power_consumption.txt")]
        if not names:
            raise RuntimeError("The expected household_power_consumption.txt file was not found in the archive.")
        target = DATA / "household_power_consumption.txt"
        with archive.open(names[0]) as source, target.open("wb") as out:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    print(f"Dataset saved to: {target}")
except Exception as exc:
    print(f"Automatic download failed: {exc}")
    print("Open the UCI dataset page and download its ZIP manually:")
    print("https://archive.ics.uci.edu/dataset/235/individualhouseholdelectricpowerconsumption")
    print("Extract household_power_consumption.txt into the project's data/ folder.")
    raise SystemExit(1)
