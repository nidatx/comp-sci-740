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
import pickle as pkl
import os
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("-u", default="user1", help="Specify user agent id")
parser.add_argument("-v", default=2, help="Videos to watch")
parser.add_argument("-n", default=6, help="max number of actions e.g. waits and scrolls")
parser.add_argument("-max", default=10, help="max wait time during active wait")
parser.add_argument("-min", default=2, help="min wait time during active wait")
parser.add_argument("-website", help="website to automate, in EXACTLY this format: https://www.theguardian.com, https://www.google.com, https://www.tiktok.com")
# parser.add_argument("-csv", help="action log will be stored here. keep format same: {website}_action_log.csv: guardian_action_log.csv, google_action_log.csv, tiktok_actions_log.csv")
args = parser.parse_args()
# arguments:
USERID = str(args.u)
MAX = int(args.max)
MIN = int(args.min)
WEBSITE = str(args.website)
# CSV_FILE = str(args.csv)
VIDEOS_TO_WATCH = args.v
MAX_NUM_OF_ACTIONS = args.n
# constants:
OPEN_WEBSITE = "open_website"
SCROLL = "scroll"
SCROLL_DUR = "scroll_duration"

SEARCH = "search"
WAIT = "wait"
ACTIVE_WAIT = "active_wait" # not used
INACTIVE_WAIT = "inactive_wait"
CLICK="click"
LOGIN = "login"
csv_headers=['website','timestamp','action','duration','user']
GOOGLE = "https://www.google.com"
GUARDIAN = "https://www.theguardian.com"
TIKTOK = "https://www.tiktok.com"



def log_action(action, csv_file, duration=-1, website=WEBSITE, user_id=USERID):
    '''
    function for logging action: usage is just log_action({action_string}). action strings are defined above as constants
    '''
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            website,
            datetime.datetime.now().isoformat(timespec="microseconds"),
            action,
            duration,
            user_id
        ])

# i tried using some techniques to avoid detection by websites that we're using selenium. idk if this works
# https://www.zenrows.com/blog/selenium-avoid-bot-detection#disable-automation-indicator-webdriver-flags
# create Chromeoptions instance 




def slow_scroll(driver, distance, step=10, pause=0.02):
    '''
    slow scroll to extend active wait time
    '''
    start_time = time.time()
    current_position = int(driver.execute_script("return window.pageYOffset;"))
    target_position = int(current_position + distance)

    # Determine the direction of the scroll (+1 for downward, -1 for upward)
    direction = 1 if distance > 0 else -1

    for pos in range(current_position, target_position, direction * step):
        driver.execute_script("window.scrollTo(0, arguments[0])", pos)
        sleep(pause)

    driver.execute_script("window.scrollTo(0, arguments[0])", target_position)
    return time.time() - start_time
    
def browse_page(driver, max, min, csv_file):
    MAX = max
    MIN = min
    num_of_actions = random.randint(2,MAX_NUM_OF_ACTIONS)
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
            log_action(action=SCROLL, csv_file=csv_file)
            random_scroll = random.randint(0, total_scroll_height)
            
            if direction == 'up':
                print("scrolling up")
                random_scroll = -random_scroll
            else:
                print("scrolling ucownp")
                
            # driver.execute_script(f"window.scrollBy(0, {random_scroll});")
            scroll_dur = duration=slow_scroll(driver, random_scroll)
            log_action(action=SCROLL_DUR, csv_file=csv_file, duration=scroll_dur)
            
            wait_time = random.randint(MIN,MAX)
            log_action(action=WAIT,duration=wait_time, csv_file=csv_file)
            sleep(wait_time)
        elif choose == WAIT:
            wait_time = random.randint(MIN,MAX)
            log_action(action=WAIT,csv_file=csv_file, duration=wait_time)
            
            print(f"just waiting {wait_time}")
            sleep(wait_time)
def automate(website, full_duration, max, min):
    # MAX = max
    # MIN = min
    

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = os.path.join(os.getcwd(), website.split('.')[1])
    CSV_FILE = os.path.join(folder, f"{timestamp}_{website.split('.')[1]}_action_log.csv")
    print(f"FOLDER: {folder}")
    print(f"CSV_NAME: {CSV_FILE}")
    
    options = webdriver.ChromeOptions()
    options.binary_location = "/Users/Patron/Downloads/chrome-mac-arm64/Google Chrome for Testing.app" ## using chrome for testing
    options.add_argument("--disable-blink-features=AutomationControlled")  # adding argument to disable the AutomationControlled flag 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) # exclude the collection of enable-automation switches 
    options.add_experimental_option("useAutomationExtension", False) # turn-off userAutomationExtension 
    
    driver = webdriver.Chrome(options=options) # setting the driver path and requesting a page 

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # changing the property of the navigator value for webdriver to undefined
    
    
    os.makedirs(folder, exist_ok=True)
    
    # write header for csv
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
    
    
    
    # strings we can google
    if website == GOOGLE:
        with open("websites.txt", "r", encoding="utf-8") as file:
            websites_list = [line.strip() for line in file if line.strip()]
    
    if website == TIKTOK:
        # for logging in if needed
        with open("tiktok_cookies.pkl", "rb") as cookie_file:
            cookies = pkl.load(cookie_file)
        # print(cookies)
        driver.get(website)
        log_action(action=OPEN_WEBSITE, csv_file=CSV_FILE)
        for cookie in cookies:
            driver.add_cookie(cookie)
        log_action(action=LOGIN)
        driver.refresh()
        log_action(action=OPEN_WEBSITE, csv_file=CSV_FILE)

        try:
            # videos_to_watch = VIDEOS_TO_WATCH
            # print(f"Will watch {videos_to_watch} videos...")
            log_action(
                website="https://www.tiktok.com/foryou",
                action=OPEN_WEBSITE,
                csv_file=CSV_FILE
            )
            driver.get("https://www.tiktok.com/foryou")
            while datetime.datetime.now() < end_time:
                wait = WebDriverWait(driver, 20)  # wait up to max 20 seconds
                video_element = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
                log_action(
                action=INACTIVE_WAIT,
                csv_file=CSV_FILE
                )
                print(f"Found video element: {video_element}")
                duration = driver.execute_script("return arguments[0].duration;", video_element)
                print(f"This Video's  duration: {duration}")
                if not duration or duration != duration: 
                    duration = 5  
                watch_time = random.uniform(0, duration)
                print(f"Video #{i+1}: duration={duration:.2f}s, watching {watch_time:.2f}s")
                log_action(
                action=WAIT,
                duration=watch_time,
                csv_file=CSV_FILE
                )
                sleep(watch_time)
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_DOWN)
                log_action(
                website=website,
                action=SCROLL,
                csv_file=CSV_FILE
                )
                
            sleep(2)
            log_action(
                action=INACTIVE_WAIT,
                duration=2,
                csv_file=CSV_FILE
            )
        except:
            pass
        # finally:
        #     driver.quit()
    else:
        try:
            driver.get(website)
            log_action(
                action=OPEN_WEBSITE,
                csv_file=CSV_FILE
            )
            if website == GOOGLE:
                wait_time = random.randint(2,5)
                log_action(action=INACTIVE_WAIT,csv_file=CSV_FILE,duration=wait_time)
                random_website = random.choice(websites_list)
                print(f"Search: {random_website}")
                search_box = driver.find_element(By.NAME, "q")
                search_box.clear()
                for i in random_website:
                    search_box.send_keys(i)
                    sleep(0.5)
                search_box.send_keys(Keys.RETURN)
                log_action(action=SEARCH,
                           csv_file=CSV_FILE)
                log_action(action=INACTIVE_WAIT,duration=6,
                           csv_file=CSV_FILE)
                sleep(6)
            
            # user scrolls up and down randomly or waits randomly for random durations
            browse_page(driver, max, min,csv_file=CSV_FILE)
            if website == GUARDIAN:
                # get article links
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
                log_action(action=INACTIVE_WAIT,  csv_file=CSV_FILE, duration=5)
                keys_to_remove = {'header', 'skip', 'secondary', 'topbar', 'footer', 'keyword', 'back to top', 'cookie', 'terms', 'privacy', 'secure drop', 'complaints', 'nav2', 'subnav', 'us-news', 'Front'}

                filtered_dict = {k: v for k, v in data_links_dict.items() if not any(sub in k for sub in keys_to_remove)}
                print(f'FILTERED: {filtered_dict.keys()}')
                with open("links.txt", "w", encoding="utf-8") as f:
                    f.write(json.dumps(filtered_dict))
                links = list(filtered_dict.values())
                links = random.choice(links)
            
            elif website == GOOGLE:
                results2 = driver.find_elements(By.TAG_NAME, "a")
                # print(results)
                # print(results2)
                links = []
                for element in results2:
                    href = element.get_attribute("href")
                    if href != None and "accounts" not in href and "support" not in href:
                        links.append(href)
            
            
            link_choose = random.choice(links)
            print(f"link: {link_choose}")
            log_action(action=OPEN_WEBSITE, csv_file=CSV_FILE, website=link_choose)
            driver.get(link_choose)
            
            browse_page(driver, max, min,csv_file=CSV_FILE)

        finally:
            if website == GUARDIAN:
                pass
            else:
                driver.quit()

automate("https://www.google.com",20,5,1)