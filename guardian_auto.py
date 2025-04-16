from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random
import datetime
import time
import csv
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-u", default="user1", help="Specify user agent id")
args = parser.parse_args()
USERID = args.u
WEBSITE = "https://www.theguardian.com/us"
OPEN_WEBSITE = "open_website"
SCROLL = "scroll"
WAIT = "wait"
CLICK="click"

csv_headers=['website,timestamp,action','duration','user']

CHROME_BINARY = "/Users/Patron/Downloads/chrome-mac-arm64/Google Chrome for Testing.app"




def log_action(action, csv_file,duration=-1, website=WEBSITE,  user_id=USERID):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            website,
            datetime.datetime.now().isoformat(timespec="microseconds"),
            action,
            duration,
            user_id
        ])



def slow_scroll(driver, distance, step=10, pause=0.02):
    current_position = driver.execute_script("return window.pageYOffset;")
    target_position = current_position + distance

    # Determine the direction of the scroll (+1 for downward, -1 for upward)
    direction = 1 if distance > 0 else -1

    for pos in range(current_position, target_position, direction * step):
        driver.execute_script("window.scrollTo(0, arguments[0])", pos)
        sleep(pause)

    driver.execute_script("window.scrollTo(0, arguments[0])", target_position)


def run_guardian(folder_path,dur=3600):
    """
    folder_path: str -> folder path which states the timestamp at which we started running
    dur: str -> duration in seconds for how long we want to run the script
    """
    csv_name = f"{folder_path}/guardian_hp_actions_log.csv"
    with open(csv_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()


    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_BINARY ## using chrome for testing
    options.add_argument("--disable-blink-features=AutomationControlled")  # adding argument to disable the AutomationControlled flag 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) # exclude the collection of enable-automation switches 
    options.add_experimental_option("useAutomationExtension", False) # turn-off userAutomationExtension 
    
    driver = webdriver.Chrome(options=options) # setting the driver path and requesting a page 

    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # changing the property of the navigator value for webdriver to undefined 
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=dur)

    while datetime.datetime.now() < end_time:
    
        try:
            driver.get(WEBSITE)
            log_action(
                action=OPEN_WEBSITE,
                csv_file=csv_name
            )
            page_html = driver.page_source

            with open(f"{folder_path}/guardian_homepage.html", "w", encoding="utf-8") as f:
                f.write(page_html)
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
                    log_action(action=SCROLL,csv_file=csv_name)
                    random_scroll = random.randint(0, total_scroll_height)
                    
                    if direction == 'up':
                        print("scrolling up")
                        random_scroll = -random_scroll
                    else:
                        print("scrolling ucownp")
                        
                    # driver.execute_script(f"window.scrollBy(0, {random_scroll});")
                    slow_scroll(driver, random_scroll)
                    wait_time = random.randint(2,10)
                    log_action(action=WAIT,duration=wait_time,csv_file=csv_name)
                    sleep(wait_time)
                elif choose == WAIT:
                    wait_time = random.randint(2,10)
                    log_action(action=WAIT,duration=wait_time,csv_file=csv_name)
                    
                    print(f"just waiting {wait_time}")
                    sleep(wait_time)
                # sleep(2)
            data_links_dict = {}

            elements_with_data_link = driver.find_elements(By.CSS_SELECTOR, "[data-link-name]")
            for elem in elements_with_data_link:
                data_link_name = elem.get_attribute("data-link-name")
                if not data_link_name:
                    continue
                if elem.tag_name.lower() == "a":
                    href = elem.get_attribute("href")
                    if href:
                        data_links_dict.setdefault(data_link_name, []).append(href)
                else:
                    sub_links = elem.find_elements(By.CSS_SELECTOR, "a[href]")
                    if sub_links:
                        for link in sub_links:
                            href = link.get_attribute("href")
                            if href:
                                data_links_dict.setdefault(data_link_name, []).append(href)
                # sleep(0.5)
            for dln_name, hrefs in data_links_dict.items():
                if 'header' not in dln_name and 'skip' not in dln_name and 'secondary' not in dln_name and 'topbar' not in dln_name and 'footer' not in dln_name and 'keyword' not in dln_name: 
                    print(f"\n--- data-link-name: {dln_name} ---")
                    for href in hrefs:
                        print(f" href -> {href}")
                        # pass
                        
            print(len(data_links_dict))
            # data_links_dict = find_links(driver)
            sleep(5)
            keys_to_remove = {'header', 'skip', 'secondary', 'topbar', 'footer', 'keyword', 'back to top', 'cookie', 'terms', 'privacy', 'secure drop', 'complaints', 'nav2', 'subnav', 'us-news', 'Front'}

            filtered_dict = {k: v for k, v in data_links_dict.items() if not any(sub in k for sub in keys_to_remove)}
            print(f'FILTERED: {filtered_dict.keys()}')
            with open("links.txt", "w", encoding="utf-8") as f:
                f.write(json.dumps(filtered_dict))
            links = list(filtered_dict.values())
            link_choose = random.choice(links)
            link_choose = random.choice(link_choose)
            print(f"link: {link_choose}")
            log_action(action=open, website=link_choose,csv_file=csv_name)
            driver.get(link_choose)
            num_of_actions = random.randint(2,6)
            for _ in range(num_of_actions):
                choose = random.choice([SCROLL, WAIT])
                # can be up or down
                if choose == SCROLL:
                    print("going to scroll")
                    direction = random.choice(['up', 'down'])
                    log_action(action=SCROLL,csv_file=csv_name)
                    random_scroll = random.randint(0, total_scroll_height)
                    if direction == 'up':
                        print("scrolling up")
                        random_scroll = -random_scroll
                    else:
                        print("scrolling ucownp")
                        
                    driver.execute_script(f"window.scrollBy(0, {random_scroll});")
                    wait_time = random.randint(2,10)
                    log_action(action=WAIT,duration=wait_time,csv_file=csv_name)
                    sleep(wait_time)
                elif choose == WAIT:
                    print("just waiting")
                    wait_time = random.randint(2,10)
                    log_action(action=WAIT,duration=wait_time,csv_file=csv_name)
                    sleep(wait_time)
        except: 
            pass
        # finally:

        #     driver.quit()
        time.sleep(2)

