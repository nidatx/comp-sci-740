from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random
import datetime
import csv
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-u", default="user1", help="Specify user agent id")
parser.add_argument("-max", default=10, help="max wait time during active wait")
parser.add_argument("-min", default=2, help="min wait time during active wait")

args = parser.parse_args()
USERID = args.u
MAX = args.max
MIN = args.min
WEBSITE = "https://www.google.com"
OPEN_WEBSITE = "open_website"
SCROLL = "scroll"
SEARCH = "search"
WAIT = "wait"
ACTIVE_WAIT = "active_wait" # not used
INACTIVE_WAIT = "inactive_wait"
CLICK="click"
CSV_FILE="google_actions_log.csv"
csv_headers=['website,timestamp,action','duration','user']
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()
def log_action(action, duration=-1, website=WEBSITE,  user_id=USERID, csv_file=CSV_FILE):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            website,
            datetime.datetime.now().isoformat(timespec="microseconds"),
            action,
            duration,
            user_id
        ])

# def find_links(driver):

#         return data_links_dict
# https://www.zenrows.com/blog/selenium-avoid-bot-detection#disable-automation-indicator-webdriver-flags
# create Chromeoptions instance 
options = webdriver.ChromeOptions() 
# adding argument to disable the AutomationControlled flag 
options.add_argument("--disable-blink-features=AutomationControlled") 
# exclude the collection of enable-automation switches 
options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
# turn-off userAutomationExtension 
options.add_experimental_option("useAutomationExtension", False) 
# setting the driver path and requesting a page 
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
# changing the property of the navigator value for webdriver to undefined 
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
with open("websites.txt", "r", encoding="utf-8") as file:
    websites_list = [line.strip() for line in file if line.strip()]

def slow_scroll(driver, distance, step=10, pause=0.02):
    current_position = driver.execute_script("return window.pageYOffset;")
    target_position = current_position + distance

    # Determine the direction of the scroll (+1 for downward, -1 for upward)
    direction = 1 if distance > 0 else -1

    for pos in range(current_position, target_position, direction * step):
        driver.execute_script("window.scrollTo(0, arguments[0])", pos)
        sleep(pause)

    driver.execute_script("window.scrollTo(0, arguments[0])", target_position)


try:
    driver.get(WEBSITE)
    log_action(
        action=OPEN_WEBSITE
    )
    page_html = driver.page_source
    wait_time = random.randint(2,5)
    log_action(action=INACTIVE_WAIT,duration=wait_time)
    random_website = random.choice(websites_list)
    print(f"Search: {random_website}")
    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    for i in random_website:
        search_box.send_keys(i)
    search_box.send_keys(Keys.RETURN)
    log_action(action="search")
    log_action(action=INACTIVE_WAIT,duration=6)
    sleep(6)
    num_of_actions = random.randint(2,6)
    print(f'performing {num_of_actions} actions...')
    total_scroll_height = driver.execute_script("return document.body.scrollHeight")
    print(f'total height: {total_scroll_height}')
    for i in range(num_of_actions):
        choose = random.choice([SCROLL, WAIT])
        # can be up or down
        if choose == SCROLL:
            print("going to scroll")
            if i == 0:
                direction = 'down'
            else:
                direction = random.choice(['up', 'down'])
            log_action(action=SCROLL)
            random_scroll = random.randint(0, total_scroll_height)
            
            if direction == 'up':
                print("scrolling up")
                random_scroll = -random_scroll
            else:
                print("scrolling ucownp")
                
            # driver.execute_script(f"window.scrollBy(0, {random_scroll});")
            slow_scroll(driver, random_scroll)
            wait_time = random.randint(2,10)
            log_action(action=WAIT,duration=wait_time)
            sleep(wait_time)
        elif choose == WAIT:
            wait_time = random.randint(2,10)
            log_action(action=WAIT,duration=wait_time)
            
            print(f"just waiting {wait_time}")
            sleep(wait_time)
    results = driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf > a")
    if not results:
        raise Exception("No search results found.")
    results2 = driver.find_elements(By.TAG_NAME, "a")
    # print(results)
    # print(results2)
    links = []
    for element in results2:
        if href != None and "accounts" not in href and "support" not in href:
            href = element.get_attribute("href")
            links.append(href)
        # print(href)
    print(f"LINKS: {links}")
    # links = list(filtered_dict.values())
    link_choose = random.choice(links)
    # link_choose = random.choice(link_choose)
    print(f"link: {link_choose}")
    log_action(action=open, website=link_choose)
    driver.get(link_choose)
    num_of_actions = random.randint(2,6)
    for _ in range(num_of_actions):
        choose = random.choice([SCROLL, WAIT])
        # can be up or down
        if choose == SCROLL:
            print("going to scroll")
            direction = random.choice(['up', 'down'])
            log_action(action=SCROLL)
            random_scroll = random.randint(0, total_scroll_height)
            if direction == 'up':
                print("scrolling up")
                random_scroll = -random_scroll
            else:
                print("scrolling ucownp")
                
            driver.execute_script(f"window.scrollBy(0, {random_scroll});")
            log_action(action=WAIT)
            wait_time = random.randint(2,10)
            sleep(wait_time)
        elif choose == WAIT:
            print("just waiting")
            log_action(action=WAIT)
            wait_time = random.randint(2,10)
            sleep(wait_time)

finally:
    driver.quit()
