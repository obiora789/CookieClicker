from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import threading
import time
import dotenv
import os

new_file = dotenv.find_dotenv()
dotenv.load_dotenv(new_file)

COOKIE_URL = "https://orteil.dashnet.org/cookieclicker/"
CHROME_DRIVER_PATH = os.getenv("CHROME_PATH")    # Path to chrome driver
MILLION = 10 ** 6
DELAY_PERIOD = 5
NEW_DELAY = 4.77
SERVICE = Service(executable_path=CHROME_DRIVER_PATH)   # Selenium service


def larger_numbers(x):
    """Converts large numbers such as a million into 10^6"""
    if 'million' in x:
        return float(x.strip('million')) * MILLION
    else:
        return x


with webdriver.Chrome(service=SERVICE) as driver:
    driver.get(url=COOKIE_URL)
    time.sleep(DELAY_PERIOD * 2)
    language_list = driver.find_element(By.ID, "prompt").text
    if "English" in language_list:
        click_english = driver.find_element(By.ID, "langSelect-EN")
        click_english.click()
    else:
        pass
    time.sleep(DELAY_PERIOD - 3)
    cookie = driver.find_element(By.ID, "bigCookie")
    time_left = False


    def sleep_time(minutes: int):
        """Monitors the time and stops the game once the time is up."""
        global time_left
        timeout = time.time() + (60 * minutes)
        while time.time() < timeout:
            time_left = True
            cookie.click()
            if time.time() >= timeout:
                time_left = False

    def check_for_upgrade(wait):
        """Checks to see the maximum upgrade everytime it's run and clicks it."""
        number_of_upgrades = 1
        while time_left:
            cookie_amount = driver.find_element(By.ID, "cookies")
            number_of_cookies = int(cookie_amount.text.split(" ")[0].replace(",", ""))
            for index in range(number_of_upgrades, 0, -1):
                int_prices = [int(larger_numbers(upgrade_price.text.replace(",", "")))
                              for upgrade_price in driver.find_elements(By.CLASS_NAME, "price")
                              if upgrade_price.text != ""]
                number_of_upgrades = len(int_prices)
                if number_of_upgrades > 3:
                    number_of_upgrades = len(int_prices) - 2
                upgrade_container = driver.find_element(By.ID, f'product{index}')
                if index < 0 or index > len(int_prices) - 2:
                    pass
                elif number_of_cookies > int_prices[index] and index <= len(int_prices) - 3:
                    driver.execute_script("arguments[0].click()", upgrade_container)
                    print(int_prices, int_prices[index])
                    break
            time.sleep(wait*2.5)


    if __name__ == "__main__":
        t1 = threading.Thread(target=sleep_time, args=(DELAY_PERIOD,))
        t2 = threading.Thread(target=check_for_upgrade, args=(NEW_DELAY,))
    #    Split the threads
        t1.start()
        t2.start()
    #    join these threads
        t1.join()
        t2.join()
        cookies_per_sec = driver.find_element(By.ID, 'cookiesPerSecond').text
        print(f"{cookies_per_sec.split(' ')[2]} cookies/second")
