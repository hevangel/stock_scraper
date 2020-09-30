from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(5)