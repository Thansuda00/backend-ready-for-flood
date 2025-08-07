from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

def scrape_data():
    """ดึงข้อมูลจากเว็บและจัดกลุ่มตามอำเภอ"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    url = "https://chiangrai.thaiwater.net/wl"
    driver.get(url)
    time.sleep(5)  # Wait for JS to load data

    results = []
    has_next_page = True
    page_count = 0

    while has_next_page and page_count < 2:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table_rows = soup.find_all('tr', class_='jss214 jss216')
        for row in table_rows:
            columns = row.find_all('td')
            station_column = row.find('th', class_='jss221 jss223')
            if len(columns) >= 6 and station_column:
                try:
                    station = station_column.get_text(strip=True)
                    location = columns[0].get_text(strip=True)
                    water_level = float(columns[1].get_text(strip=True))
                    water_status = columns[3].get_text(strip=True)
                    timeWater = columns[6].get_text(strip=True) if len(columns) > 6 else ""
                    amphur = ""
                    idx = location.find("อ.")
                    if idx != -1:
                        amphur = location[idx+2:].strip()
                    results.append({
                        "Amphur": amphur,
                        "station": station,
                        "location": location,
                        "water_level": water_level,
                        "water_status_calc": water_status,
                        "time": timeWater
                    })
                except Exception as e:
                    results.append({"error": str(e)})
            else:
                results.append({"error": "ข้อมูลไม่ครบในแถวนี้"})
        try:
            next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next Page']")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)
            page_count += 1
        except Exception:
            has_next_page = False
    driver.quit()

    # Group by Amphur
    grouped = {}
    for item in results:
        amphur = item.get("Amphur", "ไม่ทราบอำเภอ")
        if amphur not in grouped:
            grouped[amphur] = []
        grouped[amphur].append(item)
    return grouped

# FastAPI app setup
app = FastAPI()

# Allow CORS for all origins (customize as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape")
def scrape_endpoint():
    data = scrape_data()
    return JSONResponse(content=data)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

