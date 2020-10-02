import json
import os
import re
import time
from threading import Thread
import sys, traceback
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from db import *
from fuzzywuzzy import fuzz
from datetime import datetime
import msvcrt
import requests
import random
import inspect

def is_internet_connected():
    try:
        requests.get('http://google.com', timeout=3)
        return True
    except Exception:
        # print(type(e))
        # print("Connection Error")
        return False


def wait_internet_connection(f):
    def f2(*args):
        while True:
            print('Checking internet connection')
            if is_internet_connected():
                break
            else:
                print("Trying again to connect.")
        print('connected')
        f(*args)
    return f2


def wait_until_connected():
    internet_error = False
    while True:
        print('\rChecking internet connection \t', end='')
        if is_internet_connected():
            if internet_error:
                print('\r\t\tsleep for network')
                time.sleep(4)
            break
        else:
            internet_error = True
            print("\r\t\t\t\tTrying again to connect. \t", end='')
    print('connected')



def dec_get(f):
    def custom_get(*args):
        driver = args[0]
        f(driver, args[1])
        try:
            driver.execute_script(f"document.title = 'prog {sys.argv[3]} ' + document.title")
        except:
            pass
    return custom_get


# webdriver.Chrome.get = wait_internet_connection(webdriver.Chrome.get)
webdriver.Chrome.get = dec_get(webdriver.Chrome.get)
temp = None
class CustomEx(Exception):
    pass


def validate_email(email, group_num=0):
    match = re.search(
        r'(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))'
        r'@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))',
        email)
    if match:
        return match.group(group_num)
    return ''


class FindMissing:
    def __init__(self, rows, suffix):
        self.rows = rows
        self.advance_print(f'Num of rows found {len(self.rows)}')
        self.close = False
        if not self.rows:
            self.advance_print("No rows, returning.")
            return
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-ssl-errors=yes')
        self.options.add_argument('--ignore-certificate-errors')
        self.cd_google = webdriver.Chrome(options=self.options)
        self.cd_web = webdriver.Chrome(options=self.options)
        self.cd_web.set_page_load_timeout(120)
        self.cd_maps = webdriver.Chrome(options=self.options)
        wait_until_connected()
        self.cd_google.get('https://www.google.com/')
        wait_until_connected()
        self.cd_maps.get("https://www.google.com/maps")
        
        self.total_processed = 0
        self.total_found = 0
        self.max_tries = 3
        self.wait_time = 0.5
        self.TITLE_THRESHOLD = 70
        
        #self.fh = open(f'out_{suffix}.txt', 'w')
        self.name = suffix
        try:
            # self.solve_maps()
            # self.solve_web()
            self.start_scraping()
            self.close = True
            # self.__del__()
        except Exception as e:
            self.advance_print(f'Exception {type(e)}|{e}')
            print(f'Exception traceback in thread {suffix}', end='\nEnd traceback \n')
            traceback.print_exc(file=sys.stdout)
        self.advance_print('done', suffix)
        self.advance_print('\a')
        time.sleep(1)
        self.advance_print('\a')
        time.sleep(1)
        self.advance_print('\a')
        time.sleep(1)
        self.advance_print('\a')
        time.sleep(1)
        self.advance_print('\a')

    def advance_print(self, *args, **kwargs):
        #kwargs['file'] = self.fh
        try:
            print(*args, **kwargs)
            #self.fh.flush()
        except Exception as e:
            try:
                print(*[str(a).encode('utf-8') for a in args], **kwargs)
            except Exception as e2:
                print(f'Error in print,\ne: {type(e)}|{e}\ne2: {type(e2)}|{e2}')

    def get_txt_by_xpath(self, xpath, driver, element=None, wait_time=None):
        value = ''
        for _ in range(self.max_tries):
            value = driver.execute_script(f"""
           //console.log(arguments);
            parent = document;
            if(arguments[1]){{
                parent = arguments[1];
            }}
            //console.log(parent, 'parent');
            node = document.evaluate(arguments[0], parent, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
            //console.log(node, arguments);
            if(node){{
             node.scrollIntoView({{
             behavior: 'auto',
             block: 'center',
             inline: 'center'
             }});
             return node.innerText;
            }}
            return '';
            """, xpath, element)
            if not value.strip():
                time.sleep(wait_time or self.wait_time)
            else:
                break
        # debug_print(["get_txt_by_xpath", value])
        return value.strip()

    def get_attr_by_xpath(self, xpath: str, attr: str, driver, element=None, wait_time=None):
        value = ''
        for _ in range(self.max_tries):
            value = driver.execute_script(f"""
           //console.log(arguments);
            parent = document;
            if(arguments[1]){{
                parent = arguments[1];
            }}
            //console.log(parent, 'parent');
            node = document.evaluate(arguments[0], parent, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
            //console.log(node);
            if(node){{
             node.scrollIntoView({{
             behavior: 'auto',
             block: 'center',
             inline: 'center'
             }});
             let attr = node.getAttribute(arguments[2])
             return attr? attr: '';
            }}
            return '';
            """, xpath, element, attr)
            if not value.strip():
                time.sleep(wait_time or self.wait_time)
            else:
                break
        # debug_print(["get_attr_by_xpath", value])
        return value.strip()

    def __del__(self):
        if self.close:
            print("closing... ")
            self.cd_web.quit()
            self.cd_maps.quit()
            self.cd_google.quit()
        else:
            
            try:
                if not self.cd_google:
                    return
                global temp
                temp = [self.cd_google, self.cd_maps, self.cd_web]
                self.cd_google.execute_script(f"document.title = 'prog {self.name} google'")
                self.cd_web.execute_script(f"document.title = 'prog {self.name} web'")
                self.cd_maps.execute_script(f"document.title = 'prog {self.name} maps'")
            except:
                self.advance_print("Could not give titles")
        #self.fh.close()
        pass
    
    def solve_maps(self):
        for c, row in enumerate(self.rows):
            print(f'Inside solve_maps {self.name}. {datetime.now()}. ID = {row[0]}. {round(c*100/len(self.rows))} %')
            title = row[1].strip()
            id_ = row[0]
            self.total_processed += 1
            # if self.total_processed == 50:
            #     self.__del__()
            #     break
            results = {
                "VERIFICATIONLINK": json.loads(row[2]),
                "LATITUDE": "",
                "LONGITUDE": "",
                'FOUND_TITLE': row[3],
                "STATUS": row[4]
            }
            self.advance_print("initials:", results)
            self.advance_print(f"Processing {id_} -> {title} <-")
            map_count = 0
            while True:
                try:
                    self.do_map_stuff(results['FOUND_TITLE'] or title, results)
                    break
                except tuple(obj for _, obj in inspect.getmembers(exceptions) if inspect.isclass(obj)):
                    if map_count == 3:
                        raise
                    self.advance_print("Got exception in map")
                    self.cd_maps.quit()
                    self.cd_maps = webdriver.Chrome(options=self.options)
                    self.cd_maps.get("https://www.google.com/maps")
                    map_count += 1

            
            if any([results[k] for k in results if (k != "STATUS" and k != "DESCRIPTION")]):
                results["STATUS"] = "Partially completed"
                self.total_found += 1
            else:
                results["STATUS"] += " (maps verified)"
            self.advance_print(json.dumps(results, indent=4))
            results["VERIFICATIONLINK"] = json.dumps(results["VERIFICATIONLINK"])
            query = (
                f'''update master set {",".join([f"`{k}` = '{escape_single_quote(v)}'" for k, v in results.items()])}'''
                f''' where id = {id_};''')
            q_count = 0
            d_e = CustomEx('data base')
            while q_count <= 10:
                try:
                    run_query(query, 'db.db')
                    break
                except OperationalError as o_e:
                    d_e = o_e
                    q_count += 1
                    time.sleep(5)
            else:
                raise d_e

    def solve_web(self):
        for c, row in enumerate(self.rows):
            print(f'Inside solve_web {self.name}. {datetime.now()}. ID = {row[0]}. {round(c*100/len(self.rows))} %')
            title = row[1].strip()
            id_ = row[0]
            self.total_processed += 1
            # if self.total_processed == 50:
            #     self.__del__()
            #     break
            results = {
                "VERIFICATIONLINK": json.loads(row[2]),
                "EMAIL": '',
                "WEBSITE": row[3],
                "TWITTER": "",
                "FACEBOOK": "",
                "LINKEDIN": "",
                "INSTAGRAM": "",
                "YOUTUBE": "",
                "LOGOS/IMAGES": "",
                "STATUS": row[4]
            }
            self.advance_print("initials:", results)
            self.advance_print(f"Processing {id_} -> {title} <-")
            w_count = 0
            load = True
            while w_count < 3:
                try:
                    self.do_website_stuff(results['WEBSITE'], results, load)
                    break
                except exceptions.UnexpectedAlertPresentException:
                    try:
                        self.cd_web.switch_to.alert.accept()
                        load = False
                    except:
                        self.advance_print("Getting UnexpectedAlertPresentException")
                except Exception:
                    pass
                self.advance_print('exception in cd_web')
                w_count += 1

            
            if any([results[k] for k in results if (k != "STATUS" and k != "DESCRIPTION")]):
                results["STATUS"] = "Partially completed"
                self.total_found += 1
            else:
                results["STATUS"] += " (web verified)"
            self.advance_print(json.dumps(results, indent=4))
            results["VERIFICATIONLINK"] = json.dumps(results["VERIFICATIONLINK"])
            query = (
                f'''update master set {",".join([f"`{k}` = '{escape_single_quote(v)}'" for k, v in results.items()])}'''
                f''' where id = {id_};''')
            q_count = 0
            d_e = CustomEx('data base')
            while q_count <= 10:
                try:
                    run_query(query, 'db.db')
                    break
                except OperationalError as o_e:
                    d_e = o_e
                    q_count += 1
                    time.sleep(5)
            else:
                raise d_e

    def start_scraping(self):
        for c, row in enumerate(self.rows):
            print(f'{c}/{len(self.rows)} - Inside program {self.name}. {datetime.now()}. ID = {row[0]}. {round(c*100/len(self.rows), 3)} %')
            title = row[1].strip()
            id_ = row[0]
            self.total_processed += 1
            # if self.total_processed == 50:
            #     self.__del__()
            #     break
            results = {
                "VERIFICATIONLINK": [],
                "FOUND_TITLE": "",
                "DESCRIPTION": title,
                "TAGLINE": "",
                "ADDRESS": "",
                "LATITUDE": "",
                "LONGITUDE": "",
                "PHONE": "",
                "EMAIL": "",
                "WEBSITE": "",
                "TWITTER": "",
                "FACEBOOK": "",
                "LINKEDIN": "",
                "INSTAGRAM": "",
                "YOUTUBE": "",
                "LOGOS/IMAGES": "",
                "HOURS": "",
                "CATEGORY": "",
                "TAGS(KEYWORDS)": "",
                # "CITY": "",
                # "STATE": "",
                "STATUS": ""
            }

            self.advance_print(f"Processing {id_} -> {title} <-")
            self.method_1(results, title)
            map_count = 0
            while True:
                try:
                    self.do_map_stuff(results['FOUND_TITLE'] or title, results)
                    break
                except tuple(obj for _, obj in inspect.getmembers(exceptions) if inspect.isclass(obj)):
                    if map_count == 3:
                        raise
                    self.advance_print("Got exception in map")
                    self.cd_maps.quit()
                    self.cd_maps = webdriver.Chrome(options=self.options)
                    self.cd_maps.get("https://www.google.com/maps")
                    map_count += 1

            self.method2(title, results)
            if results['WEBSITE']:
                w_count = 0
                load = True
                while w_count < 3:
                    try:
                        self.do_website_stuff(results['WEBSITE'], results, load)
                        break
                    except exceptions.UnexpectedAlertPresentException:
                        try:
                            self.cd_web.switch_to.alert.accept()
                            load = False
                        except:
                            self.advance_print("Getting UnexpectedAlertPresentException")
                    except Exception:
                        pass
                    self.advance_print('exception in cd_web')
                    w_count += 1

            if all([results[k] for k in results if k != "STATUS"]):
                results["STATUS"] = "All completed"
                self.total_found += 1
            elif any([results[k] for k in results if (k != "STATUS" and k != "DESCRIPTION")]):
                results["STATUS"] = "Partially completed"
                self.total_found += 1
            else:
                results["STATUS"] = "Not found"
            self.advance_print(json.dumps(results, indent=4))
            results["VERIFICATIONLINK"] = json.dumps(results["VERIFICATIONLINK"])
            query = (
                f'''update master set {",".join([f"`{k}` = '{escape_single_quote(v)}'" for k, v in results.items()])}'''
                f''' where id = {id_};''')
            q_count = 0
            d_e = CustomEx('data base')
            while q_count <= 10:
                try:
                    run_query(query, 'db.db')
                    break
                except OperationalError as o_e:
                    d_e = o_e
                    q_count += 1
                    time.sleep(5)
            else:
                raise d_e
            # self.save_screenshot(id_, results['WEBSITE'])
            # input('Enter to cont for next iteration...')

    def save_screenshot(self, id_, web_url):
        os.makedirs('images', exist_ok=True)
        self.cd_google.save_screenshot(rf'images/{id_}-google.png')
        self.cd_maps.save_screenshot(rf'images/{id_}-maps.png')
        if web_url:
            try:
                element_png = self.cd_web.find_element_by_xpath("//body").screenshot_as_png
                with open(rf'images/{id_}-web.png', "wb") as file:
                    file.write(element_png)
                # self.cd_web.save_screenshot(rf'images/{id_}-web.png')
            except:
                try:
                    self.cd_web.save_screenshot(rf'images/{id_}-web.png')
                except:
                    pass

    def check_captcha(self, driver: webdriver.Chrome, url):
        response = True
        while driver.current_url.startswith('https://www.google.com/sorry/index?continue='):
            driver.execute_script(f"document.title = 'prog {sys.argv[3]} ' + document.title")
            minutes = random.randrange(5, 15)
            print(f'Solve the captacha and enter in {minutes} min\a')
            response = False
            for i in range(60*minutes, 0, -1):
                print(f"\r (time left {i} s)", sep='', end='', flush=True)
                time.sleep(1)
                if msvcrt.kbhit():
                    msvcrt.getch()
                    # print()
                    break
            wait_until_connected()
            driver.get(url)
        return response



    def method_3(self, results: dict, title):
        self.advance_print('Using method 3')
        side_elements = self.cd_google.find_elements_by_xpath('//*[@id="rhs"]/div')
        for side_e in side_elements:
            title_txt = self.get_txt_by_xpath('.//*[@data-attrid="title"]', self.cd_google, element=side_e, wait_time=1)
            if fuzz.ratio(title_txt.lower(), title.lower()) < self.TITLE_THRESHOLD:
                self.advance_print(f'Title not match in method3 {[title_txt.lower(), title.lower()]}')
                continue
            web_url = self.get_attr_by_xpath('//a[@data-attrid="visit_official_site" or (@class="ab'
                                             '_button" and text()="Website")]', 'href', self.cd_google, element=side_e,
                                             wait_time=0.5)
            if web_url and not results['WEBSITE']:
                self.advance_print(f'Got web_url: {web_url}')
                results['WEBSITE'] = web_url
            if not results['FOUND_TITLE']:
                results['FOUND_TITLE'] = title_txt
            prop_elements = side_e.find_elements_by_xpath("//div[@class='Z1hOCe']")
            soc_elements = side_e.find_elements_by_xpath("//g-link/a")
            for e in prop_elements:
                e_text = e.text
                if "Address" in e_text and not results['ADDRESS']:
                    results['ADDRESS'] = re.sub(r'address(:?)\s*', '', e_text, flags=re.I)
                    self.advance_print(f"Got address: {results['ADDRESS']}")
                elif "Hours" in e_text and not results['HOURS']:
                    results['HOURS'] = re.sub(r"hours(:?)\s*", '', e_text, flags=re.I)
                    self.advance_print(f"Got hours: {results['HOURS']}")
                elif "Phone" in e_text and not results['PHONE']:
                    results['PHONE'] = re.sub(r"phone(:?)\s*", '', e_text, flags=re.I)
                    self.advance_print(f"Got phone: {results['PHONE']}")
                elif "Motto" in e_text and not results['TAGLINE']:
                    results['TAGLINE'] = re.sub(r"motto(:?)\s*", '', e_text, flags=re.I)
                    self.advance_print(f"Got results['TAGLINE']: {results['TAGLINE']}")

            for e in soc_elements:
                s_link = e.get_attribute('href')
                if "facebook" in s_link and not results["FACEBOOK"]:
                    results["FACEBOOK"] = s_link
                elif "twitter" in s_link and not results['TWITTER']:
                    results['TWITTER'] = s_link
                elif "youtube" in s_link and not results["YOUTUBE"]:
                    results["YOUTUBE"] = s_link
                elif "instagram" in s_link and not results['INSTAGRAM']:
                    results['INSTAGRAM'] = s_link
                elif 'linkedin' in s_link and not results['LINKEDIN']:
                    results['LINKEDIN'] = s_link
            self.advance_print(f'Socials: {results["FACEBOOK"]}, {results["TWITTER"]}, {results["YOUTUBE"]}, {results["INSTAGRAM"]},'
                  f' {results["LINKEDIN"]}')
            try:
                category = side_e.find_element_by_xpath("//div[@data-attrid='kc:/local:one line summary']").text
                match = re.match(r"^([\S\s]+)in[\S\s]+", category)
                if match:
                    results["CATEGORY"] = match.group(1).strip()
            except exceptions.NoSuchElementException:
                category = self.get_txt_by_xpath("//div[@data-attrid='subtitle']", driver=self.cd_google, element=side_e)
                results["CATEGORY"] = category
        if results['FOUND_TITLE']:
            results["VERIFICATIONLINK"].append(self.cd_google.current_url)
    
    def handle_conn_break(self, driver, url):
        while True:
            try:
                # //*[@id="main-message"]/h1/span[.='This site can’t be reached']
                driver.find_element_by_xpath("//input[@name='q']")
                print('\r\t\t\tresults might be there available\t')
                return True
            except exceptions.NoSuchElementException:
                print('\r\t\t\tNo results\t')
                wait_until_connected()
                driver.get(url)
                return False

    def method_1(self, results: dict, title):
        self.advance_print('Using method 1')
        self.check_captcha(self.cd_google, "https://www.google.com/")
        wait_until_connected()
        q_input_e = self.cd_google.find_element_by_xpath("//input[@name='q']")    
        self.cd_google.execute_script("arguments[0].value = ''", q_input_e)
        q_input_e.send_keys(title + Keys.ENTER)
        time.sleep(2)
        count = 1
        while not all([self.check_captcha(self.cd_google, "https://www.google.com/"), self.handle_conn_break(self.cd_google, "https://www.google.com/")]):
            self.advance_print(f'captcha was found {count}')
            if count >= 3:
                count = 0
                print('closing prev driver.')
                self.cd_google.quit()
                self.cd_google = webdriver.Chrome(options=self.options)
                self.cd_google.get("https://www.google.com/")
                print('new driver set.')
            q_input_e = self.cd_google.find_element_by_xpath("//input[@name='q']")    
            self.cd_google.execute_script("arguments[0].value = ''", q_input_e)
            q_input_e.send_keys(title + Keys.ENTER)
            time.sleep(2)
            count += 1
        self.cd_google.execute_script(f"document.title = 'prog {self.name}' + document.title;")
        t_elements = self.cd_google.find_elements_by_xpath('//*[@data-attrid="title"]')
        for t_e in t_elements:
            if t_e.text == "See results about":
                t_elements.remove(t_e)
        if not t_elements:
            self.advance_print("Title not found, skipping method 1")
            return
        elif len(t_elements) > 1:
            self.method_3(results, title)
            return
            # raise CustomEx
            # self.advance_print("Please Check out the browser, titles are more than 1")
            # input("Returning.. enter to cont..\a\a\a\a")

        else:
            t_e_text = t_elements[0].text.strip().lower()
            if fuzz.ratio(t_e_text, title.lower()) < self.TITLE_THRESHOLD:
                self.advance_print(f'Title not match in method1 {[t_e_text.lower(), title.lower()]}')
                return
        try:
            web_url = self.cd_google.find_element_by_xpath('//a[@data-attrid="visit_official_site" or (@class="ab'
                                                           '_button" and text()="Website")]').get_attribute('href')
            self.advance_print(f'Got web_url: {web_url}')
            results['WEBSITE'] = web_url
        except exceptions.NoSuchElementException:
            pass
        results['FOUND_TITLE'] = t_e_text
        prop_elements = self.cd_google.find_elements_by_xpath("//div[@class='Z1hOCe']")
        soc_elements = self.cd_google.find_elements_by_xpath("//g-link/a")
        for e in prop_elements:
            e_text = e.text
            if "Address" in e_text:
                results['ADDRESS'] = re.sub(r'address(:?)\s*', '', e_text, flags=re.I)
                self.advance_print(f"Got address: {results['ADDRESS']}")
            elif "Hours" in e_text:
                results['HOURS'] = re.sub(r"hours(:?)\s*", '', e_text, flags=re.I)
                self.advance_print(f"Got hours: {results['HOURS']}")
            elif "Phone" in e_text:
                results['PHONE'] = re.sub(r"phone(:?)\s*", '', e_text, flags=re.I)
                self.advance_print(f"Got phone: {results['PHONE']}")
            elif "Motto" in e_text:
                results['TAGLINE'] = re.sub(r"motto(:?)\s*", '', e_text, flags=re.I)
                self.advance_print(f"Got results['TAGLINE']: {results['TAGLINE']}")

        for e in soc_elements:
            s_link = e.get_attribute('href')
            if "facebook" in s_link:
                results["FACEBOOK"] = s_link
            elif "twitter" in s_link:
                results['TWITTER'] = s_link
            elif "youtube" in s_link:
                results["YOUTUBE"] = s_link
            elif "instagram" in s_link:
                results['INSTAGRAM'] = s_link
            elif 'linkedin' in s_link:
                results['LINKEDIN'] = s_link
        self.advance_print(f'Socials: {results["FACEBOOK"]}, {results["TWITTER"]}, {results["YOUTUBE"]}, {results["INSTAGRAM"]},'
              f' {results["LINKEDIN"]}')
        try:
            category = self.cd_google.find_element_by_xpath("//div[@data-attrid='kc:/local:one line summary']").text
            match = re.match(r"^([\S\s]+)in[\S\s]+", category)
            if match:
                results["CATEGORY"] = match.group(1).strip()
        except exceptions.NoSuchElementException:
            category = self.get_txt_by_xpath("//div[@data-attrid='subtitle']", driver=self.cd_google)
            results["CATEGORY"] = category
        results["VERIFICATIONLINK"].append(self.cd_google.current_url)

    def do_website_stuff(self, website_url: str, results, load):
        if not website_url.strip():
            return
        # results['WEBSITE'] = website_url
        if load:
            try:
                self.advance_print('loading page')
                wait_until_connected()
                self.cd_web.get(website_url)
                self.advance_print('load complete')
            except exceptions.TimeoutException:
                self.advance_print('Load timeout')
                pass
        else:
            self.advance_print('not loading page')
        if not is_internet_connected() and load:
            self.advance_print('Retrying web')
            wait_until_connected()
            return self.do_website_stuff(website_url, results, load)
        count = 0
        before_html = 'before'
        after_html = 'after'
        while True:
            self.advance_print("Waiting for page to load")
            try:
                before_html = self.cd_web.execute_script('return document.querySelector("html").outerHTML')

                after_html = self.cd_web.execute_script('return document.querySelector("html").outerHTML')
                self.advance_print(len(before_html), len(after_html))
            except:
                pass
            time.sleep(2)
            if before_html == after_html or count > 7:
                break
            count += 1
        email_eles = self.cd_web.find_elements_by_xpath(
            "//*[contains(., '@') and not(*[contains(., '@')]) and not(self::style) and not(self::script)]")
        emails = []
        for email_e in email_eles:
            email = validate_email(email_e.text)
            if email and email not in emails:
                self.advance_print('Email in text', email)
                emails.append(email)
        for email_e in self.cd_web.find_elements_by_xpath("//a[contains(@href, 'mailto')]"):
            email = self.get_attr_by_xpath('.', 'href', self.cd_web, element=email_e).replace("mailto:", "")
            if email and email not in emails:
                self.advance_print('Email in href', email)
                emails.append(email)
        results['EMAIL'] = json.dumps(emails)
        desc = self.get_attr_by_xpath("//meta[@name='description' or @property='og:description']", 'content',
                                      self.cd_web)
        if desc:
            results['DESCRIPTION'] = desc
        img_try = 0
        while not results["LOGOS/IMAGES"] and img_try < 3:
            logo_elements = self.cd_web.find_elements_by_xpath(
                "//img[@*[contains(translate(., 'LOGO', 'logo'), 'logo')]]") or self.cd_web.find_elements_by_xpath("//img")
            for l_e in logo_elements:
                logo_src = l_e.get_attribute("src")
                self.advance_print(f'logo src = {logo_src}')
                results["LOGOS/IMAGES"] = logo_src
                if logo_src:
                    break
            img_try += 1
            time.sleep(1)
        if not results["LOGOS/IMAGES"]:
            results["LOGOS/IMAGES"] = ''
        if website_url not in results["VERIFICATIONLINK"]: 
            results["VERIFICATIONLINK"].append(website_url)
        social_keys = ['TWITTER', 'FACEBOOK', 'LINKEDIN', 'INSTAGRAM', 'YOUTUBE']
        for key in social_keys:
            if not results[key]:
                results[key] = self.get_attr_by_xpath(
                    f"//a[contains(translate(@href,'{key}','{key.lower()}'),'{key.lower()}')]", "href",
                    driver=self.cd_web, wait_time=0)
                if results[key]:
                    self.advance_print(f'Found {key}: {results[key]}')

    def do_map_stuff(self, title, results):
        if not title:
            self.advance_print('no title in map')
            return
        # self.check_captcha(self.cd_maps, "https://www.google.com/maps")
        wait_until_connected()
        q_input_e = self.cd_maps.find_element_by_xpath("//input[@name='q']")
        self.cd_maps.execute_script(f"""
        inp_f = arguments[0];
        inp_f.value = arguments[1];
        inp_f.dispatchEvent(new Event("input"));
        """, q_input_e, title)
        time.sleep(2)
        self.cd_maps.execute_script("""
        document.querySelector("#searchbox-searchbutton").click();
        document.title = 'prog {self.name}' + document.title;
        """)
        time.sleep(2)
        # self.check_captcha(self.cd_maps, "https://www.google.com/maps")
        # q_input_e.send_keys(title + Keys.ENTER)
        # while self.handle_conn_break(self.cd_maps, "https://www.google.com/maps"):
        #     self.advance_print(f'maps connection break')
        #     q_input_e = self.cd_maps.find_element_by_xpath("//input[@name='q']")    
        #     self.cd_maps.execute_script("arguments[0].value = ''", q_input_e)
        #     q_input_e.send_keys(title + Keys.ENTER)
        h3_text = self.get_txt_by_xpath("//h1[contains(@class ,'section-hero-header-title-title')]", self.cd_maps,
                                        wait_time=2)
        self.advance_print(f"Got title maps", [h3_text, title])
        if fuzz.ratio(title.lower(), h3_text.lower()) >= self.TITLE_THRESHOLD:
            directions_url = self.cd_maps.current_url
            match = re.search(
                r"/@(-?\d+\.\d+),(-?\d+\.\d+)", directions_url)
            if match:
                results['LATITUDE'] = match.group(1)
                results['LONGITUDE'] = match.group(2)
            results["VERIFICATIONLINK"].append(directions_url)
        else:
            self.advance_print('Did not found in maps')

    def method2(self, title, results):
        if results['WEBSITE']:
            return
        self.advance_print('Using method 2')
        web_links_elements = self.cd_google.find_elements_by_xpath("//div[@class='r']/a")
        for web_link_e in web_links_elements:
            search_title = self.get_txt_by_xpath('./h3', self.cd_google, web_link_e, wait_time=0.5)
            web_url = (self.get_attr_by_xpath('.', "href", self.cd_google, web_link_e) or 'nothing.com ').split()[
                0].strip()
            titles_match_ratio = fuzz.ratio(title, search_title)
            url_title_match_ratio = fuzz.ratio(web_url.replace('//', '').split('/')[0],
                                               title)
            self.advance_print(f'titles_match_ratio: {titles_match_ratio}, url_title_match_ratio: {url_title_match_ratio}')
            if url_title_match_ratio >= 30 and titles_match_ratio >= self.TITLE_THRESHOLD:
                self.advance_print(f'web url found using both', web_url)
                results['WEBSITE'] = web_url
                if not results['FOUND_TITLE']:
                    results['FOUND_TITLE'] = search_title
                return
            elif titles_match_ratio > 95:
                self.advance_print(f'web url found using titles_match_ratio only', web_url)
                results['WEBSITE'] = web_url
                if not results['FOUND_TITLE']:
                    results['FOUND_TITLE'] = search_title
                return
        self.advance_print('Not found in method 2')



rows = run_query(f"select ID, TITLE from master where STATUS is NULL and ID >= {sys.argv[1]} and Id <= {sys.argv[2]};",
                 "db.db")[2]
# rows = run_query(f"select ID, TITLE, VERIFICATIONLINK, FOUND_TITLE, STATUS from master where  status = 'Not found' and ID >= {sys.argv[1]} and Id < {sys.argv[2]};",
#                  "db.db")[2]
# rows = run_query(f"select t.* from (select ID, TITLE,VERIFICATIONLINK, WEBSITE, STATUS, `LOGOS/IMAGES` from master where WEBSITE != '' and EMAIL = '[]') as t where t.`LOGOS/IMAGES` = 'data:image/png;base64,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'",
#                  "db.db")[2]
FindMissing(rows, sys.argv[3])



