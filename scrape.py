
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

'''
1. This script downloads the PDFs of the parliamentary periods 25 to 28 from the official website of the Turkish Parliament.
2. It also converts the PDFs to text files.

Requirements:
1. For pdf to text function, you must have pdftotext installed.
Use the command: "brew install poppler"

2. You must have the TPT data folder in the same directory as this script.

'''
def download_pdfs(donem, yasama_yili):
    base_url = "https://www5.tbmm.gov.tr"
    target_url = f"{base_url}/develop/owa/tutanak_dergisi_pdfler.birlesimler?v_meclis=1&v_donem={donem}&v_yasama_yili={yasama_yili}&v_cilt="
    save_folder = f"TPT/PDFs/{donem}-y{yasama_yili}_pdfs"
    os.makedirs(save_folder, exist_ok=True)

    try:
        response = requests.get(target_url, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")

        pdf_links = [
            urljoin(base_url, link.get("href"))
            for link in soup.find_all("a")
            if link.get("href") and link.get("href").endswith(".pdf")
        ]

        for i, pdf_url in enumerate(pdf_links):
            pdf_name = pdf_url.split("/")[-1]
            save_path = os.path.join(save_folder, pdf_name)

            if os.path.exists(save_path):
                print(f"[{i+1}/{len(pdf_links)}] Skipped (exists): {pdf_name}")
                continue

            res = requests.get(pdf_url, stream=True, verify=False)
            with open(save_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"[{i+1}/{len(pdf_links)}] ✅ Saved: {pdf_name}")

        print(f"✅ Done for {donem} / {yasama_yili}")
    except Exception as e:
        print(f"❌ Error for {donem} / {yasama_yili}: {e}")

def convert_pdfs_to_text(donem, yasama_yili):
    pdf_folder = f"TPT/PDFs/{donem}-y{yasama_yili}_pdfs"
    text_folder = f"TPT/TXTs/{donem}-y{yasama_yili}_txts"
    os.makedirs(text_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    for i, pdf_file in enumerate(pdf_files):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        text_file = pdf_file.replace(".pdf", ".txt")
        text_path = os.path.join(text_folder, text_file)

        if os.path.exists(text_path):
            print(f"[{i+1}/{len(pdf_files)}] Skipped (exists): {pdf_file}")
            continue

        try:
            os.system(f'pdftotext -layout -enc UTF-8 "{pdf_path}" "{text_path}"')
            print(f"[{i+1}/{len(pdf_files)}] ✅ Converted: {pdf_file}")
        except Exception as e:
            print(f"[{i+1}/{len(pdf_files)}] ❌ Error: {pdf_file} - {e}")

    print(f"✅ Done for {donem} / {yasama_yili}")


if __name__ == '__main__':
    # Download PDFs
    '''
    download_pdfs('d25', 1)
    download_pdfs('d25', 2)
    download_pdfs('d26', 1)
    download_pdfs('d26', 2)
    download_pdfs('d26', 3)
    download_pdfs('d27', 1)
    download_pdfs('d27', 2)
    download_pdfs('d27', 3)
    download_pdfs('d27', 4)
    download_pdfs('d27', 5)
    download_pdfs('d27', 6)
    download_pdfs('d28', 1)
    download_pdfs('d28', 2)
    '''
    # Convert PDFs to text
    
    '''
    convert_pdfs_to_text('d25', 1)
    convert_pdfs_to_text('d25', 2)
    convert_pdfs_to_text('d26', 1)
    convert_pdfs_to_text('d26', 2)
    convert_pdfs_to_text('d26', 3)
    convert_pdfs_to_text('d27', 1)
    convert_pdfs_to_text('d27', 2)
    convert_pdfs_to_text('d27', 3)
    convert_pdfs_to_text('d27', 4)
    convert_pdfs_to_text('d27', 5)
    convert_pdfs_to_text('d27', 6)
    convert_pdfs_to_text('d28', 1)
    convert_pdfs_to_text('d28', 2)
    '''
