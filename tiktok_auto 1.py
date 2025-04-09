from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random
import datetime
import csv
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-u", default="user1", help="Specify user agent id")
args = parser.parse_args()
USERID = args.u
WEBSITE = "https://www.tiktok.com/"
OPEN_WEBSITE = "open_website"
SCROLL = "scroll"
WAIT = "wait"
csv_headers=['website,timestamp,action','duration','user']
with open("tiktok_actions_log.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()
def log_action(website, action, duration, user_id, csv_file="tiktok_actions_log.csv"):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            website,
            datetime.datetime.now().isoformat(timespec="microseconds"),
            duration,
            action,
            user_id
        ])
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

# for logging in if needed
with open("tiktok_cookies.pkl", "rb") as cookie_file:
    cookies = pickle.load(cookie_file)
# print(cookies)
driver.get(WEBSITE)
for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()
try:
    videos_to_watch = 3 
    print(f"Will watch {videos_to_watch} videos...")
    log_action(
        website=WEBSITE,
        action=OPEN_WEBSITE,
        duration=-1,
        user_id=USERID  # default user
    )
    driver.get("https://www.tiktok.com/foryou")
    for i in range(videos_to_watch):
        wait = WebDriverWait(driver, 20)  # wait up to max 20 seconds
        video_element = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        print(f"Found video element: {video_element}")
        duration = driver.execute_script("return arguments[0].duration;", video_element)
        print(f"This Video's  duration: {duration}")
        if not duration or duration != duration: 
            duration = 5  
        watch_time = random.uniform(0, duration)
        print(f"Video #{i+1}: duration={duration:.2f}s, watching {watch_time:.2f}s")

        sleep(watch_time)
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ARROW_DOWN)
        log_action(
        website=WEBSITE,
        action=SCROLL,
        duration=-1,
        user_id=USERID  # default user
    )
        
        sleep(2)


finally:
    driver.quit()
