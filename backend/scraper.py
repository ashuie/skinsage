import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


# loads all items of a given category of product and adds all labels and URLs to dataframe
def parse_page(str_type, type, driver):
    global df
    checkbox = driver.find_element(By.XPATH, "//li[@data-category_name='" + str_type +\
                                                "']/label/span[@class='ico']")
    checkbox.click()
    time.sleep(2)
    for category in type:
        category_checkbox = driver.find_element(By.XPATH, "//li[@data-category_name='" + category +\
                                                "']/label/span[@class='ico']")
        category_checkbox.click()
        scroll_btn = None
        time.sleep(2)
        while True:
            for i in range(3):
                driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
                time.sleep(2)
            try:
                scroll_btn = driver.find_element(By.XPATH, "//button[@class='btn btn-page-more']")
                scroll_btn.click()
            except NoSuchElementException:
                break
            time.sleep(3)    
        subpage_url = []
        items = driver.find_elements(By.XPATH, "//div[@class='unit-thumb']/a")
        for item in items:
            sub_url = item.get_attribute("href")
            subpage_url.append(sub_url)
        dic = {'Label': category, 'URL': subpage_url}
        df = pd.concat([df, pd.DataFrame(dic)], ignore_index=True)
        driver.execute_script("window.scrollTo(0,0)")
        time.sleep(2)
        category_checkbox.click()
        time.sleep(1)
    checkbox.click()

url = "https://global.oliveyoung.com/"
driver = webdriver.Chrome()
actions = ActionChains(driver)

driver.get(url)
driver.maximize_window()
time.sleep(3)

close_popup = driver.find_element(By.XPATH, "//button[@id='shopping-setting-close-window-today']")
close_popup.click()
time.sleep(2)

heading = driver.find_element(By.XPATH, "//a[@data-attr='GNB_PC_Skincare_click']")
subheading = driver.find_element(By.XPATH, "//a[@data-attr='공통^DRAW^Skincare']")
actions.move_to_element(heading).perform()
actions.move_to_element(subheading).perform()
subheading.click()
time.sleep(3)
show_more_items = driver.find_element(By.XPATH, "//button[@title='48unit view']")
show_more_items.click()
time.sleep(3)

df = pd.DataFrame(columns=['Label', 'URL'])
moisturizers = {"Toner": "", "Moisturizer": "", "Essence & Serum": "", "Cream":"", \
                "Face Mist": "", "Face Oil": "", "Spot Care": ""}
cleansers = {"Cleansing Foam": "", "Cleansing Oil": "", "Cleansing Water": "", \
             "Cleansing Tissue": "", "Cleansing Cream": "", "Facial Scrub": ""}

parse_page("Moisturizers", moisturizers, driver)
parse_page("Cleansers", cleansers, driver)

df_itemdesc = pd.DataFrame(columns=["brand", "name", "price", "rating", "skin type", "ingredients"])
df = pd.concat([df, df_itemdesc], axis = 1)

# parse individual products by URL and add info to dataframe
for i in range(len(df)):
    url = df.loc[i, "URL"]
    driver.get(url)
    time.sleep(3)
    try:
        df.loc[i, "brand"] = driver.find_element(By.XPATH, "//div[@class='prd-brand-info']/h3/a").get_attribute("textContent")
    except NoSuchElementException:
        df.loc[i, "brand"] = ""
        continue
    df.loc[i, "name"]  = driver.find_element(By.XPATH, "//div[@class='prd-brand-info']/dl/dt").get_attribute("textContent")
    df.loc[i, "price"]  = driver.find_element(By.XPATH, "//div[@class='prd-price-info']/dl/dt").get_attribute("textContent")
    df.loc[i, "rating"] = driver.find_element(By.XPATH, "//dl[@class='prd-rating-info']/dt/span").get_attribute("textContent")
    skin_types = driver.find_elements(By.XPATH, "//div[.//p[text()='Skin Type' and class='sub-title']]/ul/li/a")
    all_tags = []
    for tag in skin_types: 
        all_tags.append(tag.get_attribute("textContent") + ",")
    df.loc[i, "skin type"] = "".join(all_tags)
    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(1)
    ingredient_info = driver.find_element(By.XPATH, "//a[@data-attr='PD_specificItemPopup_click']")
    ingredient_info.click()
    time.sleep(1)
    try:
        df.loc[i, "ingredients"] = driver.find_element(By.XPATH, "//tr[.//th[text()='Ingredients']]/td").get_attribute("textContent")
    except NoSuchElementException:
        df.loc[i, "ingredients"]  = "No Info"
    time.sleep(1)
    
df.to_csv("./data/skincare.csv", encoding = "utf-8-sig", index = False)

driver.quit()