from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import csv
import time
from bs4 import BeautifulSoup

# --- Configuration ---
START_URL = (
    "https://dbis.uni-regensburg.de/warpto?ubr_id=SBBPK&resource_id=9032"
    "&license_type=3&license_form=31&access_type=1&access_form=&access_id=32045"
)
USERNAME = "X240451"
PASSWORD = "AZoeypewc1#"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

# --- Setup WebDriver ---
options = Options()
# options.add_argument("--headless")  # Uncomment to run headless
options.add_argument("--disable-gpu")
service = ChromeService(executable_path=CHROMEDRIVER_PATH)

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

def extract_from_pre(pre_htmls):
    # Join all <pre> HTML blocks into one string for body
    all_text = []
    for pre_html in pre_htmls:
        soup = BeautifulSoup(pre_html, "html.parser")
        all_text.append(soup.get_text("\n"))
    full_text = "\n".join(all_text)
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    data = {'source':'','date':'','author':'','title':'','body':''}

    # 1. Source, Date, Title: as before
    for i, line in enumerate(lines):
        if line.startswith('Источник:'):
            data['source'] = line.replace('Источник:', '').strip()
        elif line.startswith('Дата выпуска:'):
            data['date'] = line.replace('Дата выпуска:', '').strip()
        elif line.startswith('Заглавие:'):
            data['title'] = line.replace('Заглавие:', '').strip()
            # The body is everything after this line
            data['body'] = '\n'.join(lines[i+1:]).strip()
            break

    # 2. Author: extract from HTML using BeautifulSoup
    # Find the "Автор:" label in the HTML and get the next <b> tag
    for pre_html in pre_htmls:
        pre_soup = BeautifulSoup(pre_html, "html.parser")
        found_author = False
        for tag in pre_soup.descendants:
            if tag.name == 'b' and found_author:
                data['author'] = tag.get_text(strip=True)
                break
            if tag.string and 'Автор:' in tag.string:
                found_author = True
        if data['author']:
            break

    return data

try:
    # 1. Navigate to the start URL
    driver.get(START_URL)

    # 2. Accept terms of use
    wait.until(
        EC.element_to_be_clickable((By.XPATH,
            "//input[@type='submit' and @value='Ich akzeptiere die Benutzungsbedingungen']"
        ))
    ).click()

    # 3. Login
    wait.until(EC.presence_of_element_located((By.XPATH,
        "/html/body/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div/div/form/table/tbody/tr[1]/td[2]/input"
    ))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.XPATH,
        "/html/body/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div/div/form/table/tbody/tr[2]/td[2]/input"
    ))).send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.XPATH,
        "/html/body/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div/div/form/table/tbody/tr[3]/td/input"
    ))).click()

    # 5. Enter without registration
    wait.until(EC.element_to_be_clickable((By.XPATH,
        "/html/body/form/table/tbody/tr[3]/td/input"
    ))).click()

    # 6. Go to artefact search
    wait.until(EC.element_to_be_clickable((By.XPATH,
        "/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr[2]/td/div[1]/a"
    ))).click()

    # 7. Enter author name
    ta = wait.until(EC.presence_of_element_located((By.XPATH,
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[1]/tbody/tr/td[1]/textarea"
    )))
    ta.clear()
    ta.send_keys('"Кирилл Дмитриев"')

    # 8. Select checkboxes
    xpaths_to_click = [
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[1]/input[4]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[1]/input[8]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[1]/input[12]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[1]/input[15]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[1]/input[16]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[1]/input[17]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[2]/input[1]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[2]/input[11]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[2]/input[10]",
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[2]/tbody/tr[2]/td[2]/input[3]",
    ]
    for xpath in xpaths_to_click:
        try:
            el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            el.click()
        except Exception:
            pass

    # 9. Set date
    dp = wait.until(EC.element_to_be_clickable((By.XPATH,
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/span[1]/input[1]"
    )))
    dp.clear(); dp.send_keys("01.01.2010")

    # 10. Click search
    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH,
        "/html/body/table[1]/tbody/tr[3]/td/table/tbody/tr[2]/td/form/table[1]/tbody/tr/td[3]//tr/td[2]"
    )))
    driver.execute_script("arguments[0].scrollIntoView(true);", search_btn)
    search_btn.click()

    # --- Scraping results ---
    csv_file = open('output.csv', 'w', newline='', encoding='utf-8')
    writer = csv.DictWriter(csv_file, fieldnames=['source', 'date', 'author', 'title', 'body'])
    writer.writeheader()
    time.sleep(1)

    cat_xpath = (
        "/html/body/table/tbody/tr[5]/td/table[2]/tbody/tr[2]/td/table/tbody/"
        "tr/td[1]/table/tbody/tr[1]/td/table/tbody/tr[position()>1]/td[1]/a"
    )
    categories = driver.find_elements(By.XPATH, cat_xpath)

    for cat_link in categories[:1]:
        cat_link.click()
        time.sleep(1)
        entry_xpath = (
            "/html/body/table/tbody/tr[5]/td/table/tbody/tr/td/form/table[4]"
            "/tbody/tr/td/dt/a"
        )
        entries = driver.find_elements(By.XPATH, entry_xpath)
        for entry in entries:
            entry.click()
            time.sleep(1)
            # --- Switch to the correct frame ---
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "fb")))
            pres = driver.find_elements(By.TAG_NAME, 'pre')
            print(f"Found {len(pres)} <pre> tags in 'fb' frame")
            if pres:
                pre_htmls = [p.get_attribute('outerHTML') for p in pres]
                data = extract_from_pre(pre_htmls)
                print("=== DEBUG EXTRACTED DATA ===")
                print(data)
                writer.writerow(data)
            else:
                print("No <pre> tag found in 'fb' frame!")
                writer.writerow({'source':'','date':'','author':'','title':'','body':''})
            driver.switch_to.default_content()
            driver.back()
            time.sleep(1)
        driver.back()
        time.sleep(1)

finally:
    try:
        csv_file.close()
    except Exception:
        pass
    driver.quit()
    print("Scraping complete. CSV saved as output.csv.")
