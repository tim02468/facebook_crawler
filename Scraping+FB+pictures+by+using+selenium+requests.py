import facebook
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys
import shutil
import time
import json
import re
from random import randint


# ## Login facebook

path = os.path.join(os.getcwd(), "geckodriver")
driver = webdriver.Firefox(executable_path = path)
driver.get("https://www.facebook.com")
assert "Facebook" in driver.title
user = "user_account"
passw = "user_password"
elem = driver.find_element_by_id("email")
elem.clear()
elem.send_keys(user)
elem = driver.find_element_by_id("pass")
elem.clear()
elem.send_keys(passw)
elem.send_keys(Keys.RETURN)


# ## 往下滑動社團照片頁面，讓隱藏資料出現

driver.get("https://www.facebook.com/groups/frontbird/photos/")
photo_link = list()
for i in range(10): # 向下滑動10次
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')  
    time.sleep(2)                      
source = driver.page_source
soup = bs(source, "html.parser")
for data in soup.find_all(class_ = "uiMediaThumb uiScrollableThumb uiMediaThumbLarge"):
    photo_link.append(data.get("href"))


# ## 進入每個連結中抓取照片

def get_picture(link):
    driver.get(link)
    source = driver.page_source
    soup = bs(source, "html.parser")
    for pic in soup.find_all("img", {"class": "spotlight"}):
        return pic.get("src")
    
for i in range(0, len(photo_link)):
    if i == 50:
        time.sleep(randint(1, 9))
    pic_link = get_picture(photo_link[i])
    try:
        r = requests.get(pic_link, stream = True)
        with open('pic2/'+str(i)+'.png', 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)
        del r     
    except:
        print("image: ", i, "can't be saved.")

