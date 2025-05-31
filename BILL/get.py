import requests

url = "https://www.tbmm.gov.tr/Yasama/Kanun-Teklifleri-Sonuc-Sayfa"

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.tbmm.gov.tr/Yasama/Kanun-Teklifleri-Sonuc",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

cookies = {
    "_ga": "GA1.1.2102747157.1748591250",
    # Add additional cookies from your cURL here if necessary
    "X-CSRF-TOKEN-TBMM.WEB.Mvc.Prod": "CfDJ8MbbvRkNkLBNrMqr5h58IooKBhh_556hmovgw2X9_XHh-7LsaN363nWTuB5hY3MZ-Wih5YYhO6cspdHUYvVxRpYlv8coC_JnV3WIqP3Qasp6g8qpmWGn-vFX7kgPqSJrIjPLTC0rKe79GlsCK7rbr4c",
    # ... You can add the rest of the cookies you used above for full session fidelity
}

params = {
    "draw": "1",
    "columns[0][data]": "donemiVeYasamaYili",
    "columns[0][name]": "donemiVeYasamaYili",
    "columns[0][searchable]": "true",
    "columns[0][orderable]": "true",
    "columns[0][search][value]": "",
    "columns[0][search][regex]": "false",
    "columns[1][data]": "esasNo",
    "columns[1][name]": "esasNo",
    "columns[1][searchable]": "true",
    "columns[1][orderable]": "true",
    "columns[1][search][value]": "",
    "columns[1][search][regex]": "false",
    "columns[2][data]": "baskanligaGelisTarihi",
    "columns[2][name]": "baskanligaGelisTarihi",
    "columns[2][searchable]": "true",
    "columns[2][orderable]": "true",
    "columns[2][search][value]": "",
    "columns[2][search][regex]": "false",
    "columns[3][data]": "onergeninOzeti",
    "columns[3][name]": "onergeninOzeti",
    "columns[3][searchable]": "true",
    "columns[3][orderable]": "false",
    "columns[3][search][value]": "",
    "columns[3][search][regex]": "false",
    "start": "0",
    "length": "10",
    "search[value]": "",
    "search[regex]": "false",
    "DonemYasamaYili": "00000000-0000-0000-0000-000000000000",
    "TaksimNo": "0",
    "TeklifSicil": "00000000-0000-0000-0000-000000000000",
    "IlkImzaSahibi": "false",
    "SonDurumu": "00000000-0000-0000-0000-000000000000",
    "EsasNumarasi": "",
    "BaslangicTarihi": "",
    "BitisTarihi": "",
    "MetinArama": "",
    "IcerikArama": "",
    "DonemYasamaYillari": "",
    "KanunGruplari": "",
    "TeklifSahibiMillletvekilleri": "",
    "SonDurumlar": "",
    "DataTableVMProp[draw]": "0",
    "DataTableVMProp[start]": "0",
    "DataTableVMProp[length]": "0",
    "DataTableVMProp[search][value]": "",
    "DataTableVMProp[search][regex]": "false",
    "_": "1748592408092"
}

response = requests.get(url, headers=headers, cookies=cookies, params=params)

print("Status Code:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type"))

try:
    data = response.json()
    print("✅ Successfully parsed JSON!")
    print(data)
except Exception as e:
    print("❌ Failed to parse JSON:")
    print(response.text[:500])
