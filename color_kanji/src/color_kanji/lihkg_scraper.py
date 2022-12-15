# Importing modules
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import random
import string
import webdriver_manager

# Functions
def init_driver() -> WebDriver:
    """
    Initialize the driver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(
        options=options, service=ChromeService(ChromeDriverManager().install())
    )
    return driver


def random_string() -> str:
    """
    Generate a random string.
    """
    length = random.randrange(10, 20)
    return "".join(random.choices(string.ascii_lowercase, k=length))


def init_context(driver: WebDriver) -> WebElement:
    """
    Initialize the LIHKG context.
    """
    driver.get("https://lihkg.com/thread/2256553/page/1")
    body = WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    element_id = random_string()
    driver.execute_script(
        'a = document.createElement("a"); a.id = arguments[1];'
        'a.target = "_blank"; arguments[0].appendChild(a)',
        body,
        element_id,
    )
    context = driver.find_element(By.ID, element_id)
    return context


# Main function
def main():
    """
    Main function.
    """
    driver = init_driver()
    context = init_context(driver)
    print(context)


if __name__ == "__main__":
    main()
