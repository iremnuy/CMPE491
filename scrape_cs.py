import os, re, time, random, html, csv
import requests, urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://www5.tbmm.gov.tr"
INDEX_URLS = [
    f"{BASE}/develop/owa/tutanak_dergisi_pdfler.meclis_donemleri?v_meclisdonem=0",
    f"{BASE}/develop/owa/tutanak_dergisi_pdfler_mmb.meclis_donemleri?v_meclisdonem=0",
]
# Senato (Cumhuriyet Senatosu) dönemi seed'leri: t01..t19
SENATE_CODES = [f"t{i:02d}" for i in range(1, 20)]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
}

EXTERNAL_SSD_PATH = "D:"
OUT_PDF_ROOT = os.path.join(EXTERNAL_SSD_PATH, "TPT", "PDFs", f"CS")
LOG_CSV = "tpt_download_log.csv"
os.makedirs(OUT_PDF_ROOT, exist_ok=True)

def get_soup(url, retries=3, sleep_base=0.8):
    last = None
    for k in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, verify=False, timeout=45)
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            last = e
        time.sleep(sleep_base*(1.6**k) + random.uniform(0, 0.4))
    raise last or RuntimeError(f"GET failed: {url}")

def safe_filename(name: str) -> str:
    name = html.unescape(name)
    name = re.sub(r"[^\w\-.]+", "_", name)
    return name.strip("._")

def discover_birlesimler_links():
    patterns = (
        "tutanak_dergisi_pdfler.birlesimler",
        "tutanak_dergisi_pdfler_mmb.birlesimler",
        "tutanak_dergisi_pdfler.birlesimler_diger_meclisler",
    )
    links = set()

    for idx in INDEX_URLS:
        try:
            soup = get_soup(idx)
        except Exception:
            continue
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "tutanak_dergisi_pdfler" in href and "birlesimler" in href:
                if any(p in href for p in patterns):
                    links.add(urljoin(BASE, href))

    # Senato (CS) t01..t19 seed linkleri
    for t_code in SENATE_CODES:
        senato_url = (
            f"{BASE}/develop/owa/tutanak_dergisi_pdfler.birlesimler_diger_meclisler"
            f"?v_meclis=7
            &meclis_kisa_adi=CS&diger_donem_adi={t_code}"
        )
        links.add(senato_url)

    return sorted(links)

PDF_PAT = re.compile(r"['\"]([^'\"\s<>]+\.pdf[^'\"<>]*)['\"]", re.IGNORECASE)

def extract_pdfs_from_birlesimler(url):
    soup = get_soup(url)
    html_text = str(soup)
    pdfs = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if ".pdf" in href.lower():
            pdfs.add(urljoin(url, href))

    for m in PDF_PAT.finditer(html_text):
        pdfs.add(urljoin(url, m.group(1)))

    for tag in soup.find_all(True):
        for val in tag.attrs.values():
            if isinstance(val, str) and ".pdf" in val.lower():
                pdfs.add(urljoin(url, val))

    qs = parse_qs(urlparse(url).query)
    bits = []
    for key in ("v_meclis", "v_donem"):
        v = qs.get(key, [""])[0]
        if v: bits.append(v)
    y = qs.get("v_yasama_yili", [""])[0]
    c = qs.get("v_cilt", [""])[0]
    if y: bits.append(f"y{y}")
    if c: bits.append(f"c{c}")
    meclis_kisa = qs.get("meclis_kisa_adi", [""])[0]
    diger_donem = qs.get("diger_donem_adi", [""])[0]
    if meclis_kisa: bits.append(meclis_kisa)          # örn: CS
    if diger_donem: bits.append(diger_donem)          # örn: t01

    folder = "_".join(bits) if bits else safe_filename(urlparse(url).path.split("/")[-1])
    return sorted(pdfs), (folder or "unknown")


def download_one(pdf_url, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    base = pdf_url.split("/")[-1]
    base = base.split("?")[0].split("#")[0] or "file.pdf"
    fpath = os.path.join(dest_dir, safe_filename(base))
    if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
        return ("skip", pdf_url, fpath, os.path.getsize(fpath))
    try:
        with requests.get(pdf_url, headers=HEADERS, stream=True, verify=False, timeout=120) as r:
            ctype = r.headers.get("Content-Type", "").lower()
            if r.status_code != 200 or ("pdf" not in ctype and not pdf_url.lower().endswith(".pdf")):
                return (f"bad:{r.status_code}", pdf_url, fpath, 0)
            tmp = fpath + ".part"
            with open(tmp, "wb") as out:
                for chunk in r.iter_content(1024 * 128):
                    if chunk: out.write(chunk)
            os.replace(tmp, fpath)
            return ("saved", pdf_url, fpath, os.path.getsize(fpath))
    except Exception as e:
        return (f"err:{e}", pdf_url, fpath, 0)

def write_log(rows):
    header = ["status", "pdf_url", "saved_path", "bytes", "folder", "source_page"]
    exists = os.path.exists(LOG_CSV)
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists: w.writerow(header)
        for r in rows: w.writerow(r)


def main(max_workers=4):
    print("➡️  Birleşimler sayfaları toplanıyor…")
    birlesimler_pages = discover_birlesimler_links()
    print(f"Found {len(birlesimler_pages)} collection pages.")

    jobs = []
    for bl in birlesimler_pages:
        pdfs, folder = extract_pdfs_from_birlesimler(bl)
        if not pdfs:
            continue
        dest = os.path.join(OUT_PDF_ROOT, folder)
        for u in pdfs:
            jobs.append((u, dest, bl))

    uniq = {}
    for u, d, bl in jobs:
        if u not in uniq:
            uniq[u] = (u, d, bl)
    jobs = list(uniq.values())
    print(f"➡️  İndirilecek benzersiz PDF sayısı: {len(jobs)}")

    rows = []
    if max_workers > 1:
        print(f"⬇️  {max_workers} number of workers…")
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = [ex.submit(download_one, u, d) for (u, d, _) in jobs]
            for i, fut in enumerate(as_completed(futs), 1):
                status, url, path, nbytes = fut.result()
                print(f"[{i}/{len(jobs)}] {status:10s} {os.path.basename(path)}")
                # source_page kaydı
                rows.append([status, url, path, nbytes, os.path.basename(os.path.dirname(path)), ""])
    else:
        print("⬇️  Downloading…")
        for i, (u, d, bl) in enumerate(jobs, 1):
            status, url, path, nbytes = download_one(u, d)
            print(f"[{i}/{len(jobs)}] {status:10s} {os.path.basename(path)}")
            rows.append([status, url, path, nbytes, os.path.basename(os.path.dirname(path)), ""])

    write_log(rows)
    print(f"🧾 Log: {LOG_CSV}")

if __name__ == "__main__":
    main(max_workers=4)
