import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome
options = Options()
options.add_argument("--headless=new")  # For Chrome 109+
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.tbmm.gov.tr/Yasama/Kanun-Teklifleri-Sonuc")
wait = WebDriverWait(driver, 100)

# Wait for page to load
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))

# Scroll to bottom to load all rows (if pagination is lazy-loaded)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# Collect rows
rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
data = []

for i, row in enumerate(rows):
    try:
        cells = row.find_elements(By.TAG_NAME, "td")
        summary_link = cells[4].find_element(By.TAG_NAME, "a")

        # Click into detail page
        driver.execute_script("arguments[0].click();", summary_link)
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(),'KANUN TEKLİFİ BİLGİLERİ')]")))

        detail = {}

        # --- General info ---
        def safe_xpath(label):
            try:
                return driver.find_element(By.XPATH, f"//td[contains(text(),'{label}')]/following-sibling::td").text.strip()
            except:
                return ""

        detail['Dönemi ve Yılı'] = safe_xpath("Dönemi ve Yasama Yılı")
        detail['Esas No'] = safe_xpath("Esas Numarası")
        detail['Başkanlığa Geliş Tarihi'] = safe_xpath("Başkanlığa Geliş Tarihi")
        detail['Başlık'] = safe_xpath("Teklifin Başlığı")
        detail['Özet'] = safe_xpath("Teklifin Özeti")
        detail['Son Durumu'] = safe_xpath("Son Durumu")

        # --- Komisyon Bilgileri ---
        try:
            komisyon_row = driver.find_element(By.XPATH, "//h3[contains(text(),'KANUN TEKLİFİ KOMİSYON BİLGİLERİ')]/following-sibling::table[1]/tbody/tr[1]")
            komisyon_cells = komisyon_row.find_elements(By.TAG_NAME, "td")
            detail['Komisyon'] = {
                "Tipi": komisyon_cells[0].text,
                "Adı": komisyon_cells[1].text,
                "Giriş Tarihi": komisyon_cells[2].text,
                "Çıkış Tarihi": komisyon_cells[3].text,
                "İşlem": komisyon_cells[4].text,
                "Karar Tarihi": komisyon_cells[5].text if len(komisyon_cells) > 5 else ""
            }
        except:
            detail['Komisyon'] = {}

        # --- İmza Sahipleri ---
        try:
            signature_rows = driver.find_elements(By.XPATH, "//h3[contains(text(),'KANUN TEKLİFİ İMZA SAHİPLERİ')]/following-sibling::table[1]/tbody/tr")
            signatures = []
            for row in signature_rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    signatures.append({
                        "Ad": cols[0].text,
                        "Parti": cols[1].text,
                        "Seçim Çevresi": cols[2].text,
                        "Durumu": cols[3].text if len(cols) > 3 else ""
                    })
            detail['İmza Sahipleri'] = signatures
        except:
            detail['İmza Sahipleri'] = []

        data.append(detail)

        # Go back to main page
        driver.back()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    except Exception as e:
        print(f"Error processing row {i}: {e}")
        continue

# Save JSON
with open("kanun_teklifleri.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

driver.quit()
print("Scraping completed and saved to kanun_teklifleri.json ✅")
