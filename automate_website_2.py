import threading 
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import subprocess
from webdriver_manager.chrome import ChromeDriverManager
from find_cache import find_cached_links, build_google_search_cache
# WebDriver imports (service + options)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.edge.options import Options as EdgeOptions

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
import numpy as np

# Constants
ACTIONS = {
    'OPEN_WEBSITE': "open_website",
    'SCROLL': "scroll",
    'SCROLL_DUR': "scroll_duration",
    'SEARCH': "search",
    'WAIT': "wait", ## denotes active waiting time - inactive wait (think time)
    'ACTIVE_WAIT': "active_wait", ## drawn from pareto dist
    'CLICK': "click",
    'LOGIN': "login"
}

CSV_HEADERS = ['website', 'timestamp', 'action', 'duration', 'user']

WEBSITES = {
    'GOOGLE': "https://www.google.com",
    'GUARDIAN': "https://www.theguardian.com",
    'TIKTOK': "https://www.tiktok.com"
}

class WebsiteAutomator:
    def __init__(self, user_id, max_wait, min_wait, website, max_actions, caching, make_profile, browser_type=""):
        self.user_id = user_id
        self.max_wait = max_wait
        self.min_wait = min_wait
        self.website = website
        self.browser_type = browser_type
        self.max_actions = max_actions
        self.caching = caching
        self.make_profile = make_profile
        self.driver = self._setup_driver()
        self.csv_file = self._setup_logging()
    
    def _generate_inactive_OFF_time(self):
        # a = 1 # shape
        # b =  ## scale parameter
        # s = b*np.random.pareto(a, 1)
        alpha = 1.5
        k = 1
        s = (np.random.pareto(alpha) + 1) * k
        return s
    
    def get_firefox_profile(self, path):
        all_files = os.listdir(path)
        for f in all_files:
            if f.endswith(f".{self.user_id}"):
                return os.path.join(path, f)
        return None
        
    def _setup_driver(self):
        
        if self.browser_type=="chrome":
            return self._setup_chrome_driver()
        elif self.browser_type == "firefox":
            return self._setup_firefox_driver()
        elif self.browser_type == "edge":
            return self._setup_edge_driver()
        else:
            raise ValueError("Unknown browser type!! STOP NOW! Browser: {self.browser_type}")
    
    def _setup_edge_driver(self):
        
        edge_driver_path = "/Users/Patron/Documents/sarah/edgedriver_mac64_m1/msedgedriver"
        
        options = EdgeOptions()
        if self.make_profile == True:
            options.add_argument(f'user-data-dir=/Users/Patron/Library/Application Support/Microsoft Edge/{self.user_id}')
            options.add_argument('profile-directory=Default')
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        options.add_experimental_option("useAutomationExtension", False) 
        
        
        service = EdgeService(edge_driver_path)
        driver = webdriver.Edge(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        
        return driver
    
    def _setup_chrome_driver(self):
        
        options = ChromeOptions() 
        #'/Users/Patron/Library/Application Support/Google/Chrome'
        if self.make_profile == True:
            options.add_argument(f'user-data-dir=/Users/Patron/Library/Application Support/Google/Chrome/{self.user_id}')
            options.add_argument('profile-directory=Default')

        options.binary_location = "/Users/Patron/Documents/sarah/chrome-mac-arm64/Google Chrome for Testing.app" ## location for browser
        
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        options.add_experimental_option("useAutomationExtension", False) 
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        
        return driver
    
    def _setup_firefox_driver(self):
        
        options = FirefoxOptions() 
        if self.make_profile == True:
            path = '/Users/Patron/Library/Application Support/Firefox/Profiles'
            profile_path = self.get_firefox_profile(path)
            if profile_path == None:
                subprocess.run(["/Applications/Firefox.app/Contents/MacOS/firefox","-CreateProfile", self.user_id])
                profile_path = self.get_firefox_profile(path)
            print(f"------FIREFOX PROFILE={profile_path}--------")
            # options.add_argument = (f'user-data-dir={path}/{self.user_id}')
            # options.add_argument = ('profile-directory=Default')
            options.add_argument('-profile')
            options.add_argument(profile_path)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        service = FirefoxService(executable_path="/Users/Patron/Documents/sarah/geckodriver") ## path to driver
        driver = webdriver.Firefox(service=service, options=options)
        
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        return driver
    
        
    def _setup_logging(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = os.path.join(os.getcwd(), self.website.split('.')[1])
        
        os.makedirs(folder, exist_ok=True)
        
        csv_file = os.path.join(folder, f"{timestamp}_{self.website.split('.')[1]}_action_log.csv")
        
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            
        return csv_file
        
    def log_action(self, action, duration=-1, website=None):
        website_inside = None
        if website is None:
            website_inside = self.website
        else:
            website_inside = website
    
        with open(self.csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                website_inside,
                datetime.datetime.now().isoformat(timespec="microseconds"),
                action,
                duration,
                self.user_id
            ])
    
    def slow_scroll(self, distance, step=10, pause=0.02):
        start_time = time.time()
        current_position = int(self.driver.execute_script("return window.pageYOffset;"))
        target_position = int(current_position + distance)
        direction = 1 if distance > 0 else -1

        for pos in range(current_position, target_position, direction * step):
            self.driver.execute_script("window.scrollTo(0, arguments[0])", pos)
            sleep(pause)

        self.driver.execute_script("window.scrollTo(0, arguments[0])", target_position)
        return time.time() - start_time
        
    def browse_page(self):
       
        num_actions = random.randint(2, self.max_actions)
        total_scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(num_actions):
            
            choose = random.choice([ACTIONS['SCROLL'], ACTIONS['WAIT']])
            if choose == ACTIONS['SCROLL']:
                if i==0:
                    direction = "down"
                else:
                    direction = random.choice(['up', 'down'])
                
                ## scrolling
                self.log_action(action=ACTIONS['SCROLL'])
                random_scroll = random.randint(0, total_scroll_height) ### randomly pick from total scroll height
                
                if direction == 'up':
                    print("scrolling up")
                    random_scroll = -random_scroll
                else:
                    print("scrolling ucownp")
                    
                
                
                ## logging scroll duration
                scroll_dur = self.slow_scroll(random_scroll)
                self.log_action(action=ACTIONS['SCROLL_DUR'], duration=scroll_dur)
                
                # wait_time = random.randint(self.min_wait, self.max_wait) ## ACTIVE WAIT
                wait_time = self._generate_inactive_OFF_time()
                self.log_action(action=ACTIONS['WAIT'], duration=wait_time) 
                sleep(wait_time) 
            
            elif choose==ACTIONS["WAIT"]:
                # wait_time = random.randint(self.min_wait, self.max_wait) ## ACTIVE WAIT
                wait_time = self._generate_inactive_OFF_time()
                
                self.log_action(action=ACTIONS['WAIT'], duration=wait_time)
                sleep(wait_time)
    
    def automate_google(self, duration_sec):
        self.log_action(action=ACTIONS['OPEN_WEBSITE'])
        self.driver.get(WEBSITES['GOOGLE'])
        if self.caching == False:
            # Load search terms
            with open("websites_small.txt", "r", encoding="utf-8") as file:
                websites_list = [line.strip() for line in file if line.strip()]
            
            start_time = time.time()
            end_time = start_time + duration_sec
            
            while time.time() < end_time:
                
            
                # seraching for random website from the list
                random_website = random.choice(websites_list)
                print(f"Search: {random_website}")
                search_box = self.driver.find_element(By.NAME, "q")
                search_box.clear()
                
                for i in random_website:
                    search_box.send_keys(i)
                    sleep(0.5)
                search_box.send_keys(Keys.RETURN)
                self.log_action(ACTIONS['SEARCH'], duration=random_website)
                
                self.log_action(ACTIONS['ACTIVE_WAIT'],duration=6) ## dont change this one because we want to wait for all the links to show up
                sleep(6)
                
                # Browse results
                self.browse_page()
                
                # follow a random link on page
                results = self.driver.find_elements(By.TAG_NAME, "a")
                links = []
                for element in results: ## only pick among top 5 results
                    href = element.get_attribute("href")
                    
                    if href != None and "accounts" not in href and "support" not in href:
                        links.append(href)
                
                # links = links[:5] # only top 5/
                link_choose = random.choice(links)
                print(f"link: {link_choose}")
                try:
                    
                    self.log_action(action=ACTIONS['OPEN_WEBSITE'], website=link_choose)
                    self.driver.get(link_choose)
                    
                    self.browse_page()

                    ## go back to google search main page
                    self.driver.get(WEBSITES['GOOGLE'])
                    self.log_action(action=ACTIONS['OPEN_WEBSITE'])

                except:
                    print(f"Could not follow link:{link_choose}")
        else:
            # # Load search terms
            # with open("websites_small.txt", "r", encoding="utf-8") as file:
            #     websites_list = [line.strip() for line in file if line.strip()]
            cached_links = build_google_search_cache(log_dir="./google", website=self.website)
            start_time = time.time()
            end_time = start_time + duration_sec
            
            while time.time() < end_time:
                
            
                # seraching for random website from the list
                random_website = random.choice(list(cached_links.keys()))
                print(f"Search: {random_website}")
                search_box = self.driver.find_element(By.NAME, "q")
                search_box.clear()
                
                for i in random_website:
                    search_box.send_keys(i)
                    sleep(0.5)
                search_box.send_keys(Keys.RETURN)
                self.log_action(ACTIONS['SEARCH'])
                
                self.log_action(ACTIONS['ACTIVE_WAIT'],duration=6) ## dont change this one because we want to wait for all the links to show up
                sleep(6)
                
                # Browse results
                self.browse_page()
                
                # follow a random link on page
                results = self.driver.find_elements(By.TAG_NAME, "a")
                links = []
                for element in results: ## only pick among top 5 results
                    href = element.get_attribute("href")
                    
                    if href != None and "accounts" not in href and "support" not in href:
                        links.append(href)
                
                
                link_choose = random.choice(list(cached_links[random_website]))
                print(f"link: {link_choose}")
                try:
                    
                    self.log_action(action=ACTIONS['OPEN_WEBSITE'], website=link_choose)
                    self.driver.get(link_choose)
                    
                    self.browse_page()

                    ## go back to google search main page
                    self.driver.get(WEBSITES['GOOGLE'])
                    self.log_action(action=ACTIONS['OPEN_WEBSITE'])

                except:
                    print(f"Could not follow link:{link_choose}")
        
                

        
    def automate_guardian(self, duration_sec):
        
        self.log_action(action=ACTIONS['OPEN_WEBSITE'])
        self.driver.get(WEBSITES['GUARDIAN'])
        # there was no browsing here, adding now
        self.browse_page()
        start_time = time.time()
        end_time = start_time + duration_sec


        
        # Get article links
        data_links_dict = {}
        self.log_action(ACTIONS['ACTIVE_WAIT'],duration=5)
        sleep(5) ## don't change this wait otherwise we get 'cannot find element' error

        elements_with_data_link = self.driver.find_elements(By.CSS_SELECTOR, "[data-link-name]")
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
                for link in sub_links:
                    href = link.get_attribute("href")
                    if href:
                        data_links_dict.setdefault(data_link_name, []).append(href)
        
        
        for dln_name, hrefs in data_links_dict.items():
            if 'header' not in dln_name and 'skip' not in dln_name and 'secondary' not in dln_name and 'topbar' not in dln_name and 'footer' not in dln_name and 'keyword' not in dln_name: 
                print(f"\n--- data-link-name: {dln_name} ---")
                for href in hrefs:
                    print(f" href -> {href}")

        print(len(data_links_dict))
        
        self.log_action(ACTIONS["ACTIVE_WAIT"],duration=5) 
        sleep(5) ## don't change this either

        # # Filter out non-article links
        # keys_to_remove = {'header', 'skip', 'secondary', 'topbar', 'footer', 
        #                   'keyword', 'back to top', 'cookie', 'terms', 'privacy', 
        #                   'secure drop', 'complaints', 'nav2', 'subnav', 'us-news', 'Front'}
        
        # filtered_dict = {k: v for k, v in data_links_dict.items() 
        #                 if not any(sub in k for sub in keys_to_remove)}
        keys_to_keep = {'sports', 'most_viewed', 'most_popular', 'headlines','around-the-world'}
        filtered_dict = {k: v for k, v in data_links_dict.items() 
                         if any(sub in k for sub in keys_to_keep)}
        
        # Save links for reference
        with open("links.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(filtered_dict))
        if self.caching == True:
            links = find_cached_links(dir="./theguardian", website=self.website, output_file="curr_guardian_cache.txt")
        # Browse articles
        while time.time() < end_time and filtered_dict:
            links = random.choice(list(filtered_dict.values()))
            if links:
                link_choose = random.choice(links)
                self.driver.get(link_choose)
                self.log_action(action=ACTIONS['OPEN_WEBSITE'], website=link_choose)
                self.browse_page()

    def automate_tiktok(self, duration_sec):
        # Load cookies for login - uncomment this if you want to login
        # with open("tiktok_cookies.pkl", "rb") as cookie_file:
        #     cookies = pkl.load(cookie_file)
        
        # self.driver.get(WEBSITES['TIKTOK'])
        # self.log_action(action=ACTIONS['OPEN_WEBSITE'])
        
        # # for cookie in cookies:
        # #     self.driver.add_cookie(cookie)
        
        # # self.log_action(action=ACTIONS['LOGIN']) 
        
        # self.driver.refresh()
        # self.log_action(action=ACTIONS['OPEN_WEBSITE'])
        
        # Go to For You page
        self.log_action(action=ACTIONS['OPEN_WEBSITE'], website="https://www.tiktok.com/foryou")
        self.driver.get("https://www.tiktok.com/foryou")
        
        start_time = time.time()
        end_time = start_time + duration_sec
        video_count = 0
        
        while time.time() < end_time:
            try:
                self.log_action(action=ACTIONS['ACTIVE_WAIT'])
                
                wait = WebDriverWait(self.driver, 20) ## wait up to max 20 seconds, don't change
                video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
                
                print(f"Found video element: {video_element}")
                duration = self.driver.execute_script("return arguments[0].duration;", video_element)
                print(f"This Video's  duration: {duration}")
                if not duration or duration != duration: 
                    duration = 5  
                
                watch_time = random.uniform(0, duration) ## don't change
                video_count += 1
                print(f"Video #{video_count}: duration={duration:.2f}s, watching {watch_time:.2f}s")
                
                self.log_action(action=ACTIONS['WAIT'], duration=watch_time)
                sleep(watch_time)
                
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_DOWN)
                self.log_action(action=ACTIONS['SCROLL'])

                self.log_action(action=ACTIONS['ACTIVE_WAIT'], duration = 2)
                sleep(2) ## don't change
                
            except Exception as e:
                print(f"Error watching TikTok video: {str(e)}")
                
    
    def run(self, duration_minutes):
        duration_sec = duration_minutes * 60
        try:
            if self.website == WEBSITES['GOOGLE']:
                self.automate_google(duration_sec)
            elif self.website == WEBSITES['GUARDIAN']:
                self.automate_guardian(duration_sec)
            elif self.website == WEBSITES['TIKTOK']:
                self.automate_tiktok(duration_sec)
            
        finally:
            self.driver.quit()

def main():

    BROWSER = "chrome"
    CACHING = True
    TIME = 33
    MAKE_PROFILE = True
    automator_google = WebsiteAutomator(
        browser_type = BROWSER, ## using chrome for testing
        user_id="googleUser4",
        max_wait=5,
        min_wait=2,
        website=WEBSITES['GOOGLE'],
        max_actions=7,
        caching=CACHING,
        make_profile=MAKE_PROFILE
    )

    automator_tiktok = WebsiteAutomator(
        browser_type = BROWSER, ## using chrome for testing
        user_id="tiktokUser4",
        max_wait=5,
        min_wait=2,
        website=WEBSITES['TIKTOK'],
        max_actions=7,
        caching=CACHING,
        make_profile=MAKE_PROFILE
    )
    automator_guardian = WebsiteAutomator(
        browser_type = BROWSER, ## using chrome for testing
        user_id="guardianUser4",
        max_wait=5,
        min_wait=2,
        website=WEBSITES['GUARDIAN'],
        max_actions=7,
        caching=CACHING,
        make_profile=MAKE_PROFILE
    )
    
    t1 = threading.Thread(target=automator_google.run, args=(TIME,))
    t2 = threading.Thread(target=automator_tiktok.run, args=(TIME,))
    t3 = threading.Thread(target=automator_guardian.run, args=(TIME,))


    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

if __name__ == "__main__":
    main()