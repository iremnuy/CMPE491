from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import json
import time

options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

# Step 1: Open form page
driver.get("https://www.tbmm.gov.tr/yasama/kanun-teklifleri")

wait = WebDriverWait(driver, 100)

# Step 2: Set "Dönemi ve Yasama Yılı" dropdown
Select(wait.until(EC.presence_of_element_located((By.ID, "donem")))).select_by_visible_text("Son Dönem Tüm Yasama Yılları")

# Optional: Set other dropdowns if needed
# Select(driver.find_element(By.ID, "grup")).select_by_visible_text("Tüm Gruplar")

# Step 3: Click "Sorgula"
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

# Step 4: Wait for results
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))

# Now parse rows
rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

bills = []
for row in rows:
    try:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 5:
            link = cols[4].find_element(By.TAG_NAME, "a").get_attribute("href")
            bills.append({
                "Başlık": cols[0].text,
                "Esas No": cols[1].text,
                "Tarihi": cols[2].text,
                "Durum": cols[3].text,
                "Detay Linki": link
            })
    except Exception as e:
        print(f"[!] Row error: {e}")
        continue

# Save or explore links further
with open("teklifler.json", "w", encoding="utf-8") as f:
    json.dump(bills, f, ensure_ascii=False, indent=2)

driver.quit()
print("✅ Başarılı! Kanun teklifleri JSON dosyasına kaydedildi.")
