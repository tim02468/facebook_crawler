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


# ## Long lived token （執行一次就可以）

# 注意是user_token, 不是app_token
token = 'your_token'
graph = facebook.GraphAPI(access_token = token)
app_id = 'your_app_id'
app_secret = 'your_app_secret'
extended_token = graph.extend_access_token(app_id, app_secret)


# ## Get 250 posts

# 每次requests會得到25篇貼文，將requests轉為dict，paging key中是另一個dict裡面包含previous, next分別只上一頁和下一頁
response = requests.get('https://graph.facebook.com/v2.7/1455214321359069/feed?access_token=' + extended_token.get("access_token"))
json_data = json.loads(response.text)
# 先將前25篇存入feed_data
feed_data = list(json_data.get("data"))
# 往下翻9頁，並將結果存入feed_data
for i in range(1, 10):
    response = requests.get(json_data.get("paging").get("next"))
    json_data = json.loads(response.text)
    feed_data.extend(json_data.get("data"))
    print(len(feed_data)) # 全部篇數


# ## 取得 post id

post_id = list(i.get("id").split("_")[1] for i in feed_data)
len(post_id) #  總篇數


# ## Login facebook

# 使用selenium進行爬蟲，先登入FB
path = os.path.join(os.getcwd(), "geckodriver") # driver的位置要給對
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


# ## Function for picture href & download pictures

# get post href
def get_post_href(post_url, class_ = "_4-eo _2t9n"): # 發現主要照片連結位置被放在這個class
    driver.get(url)
    source = driver.page_source
    soup = bs(source, "html.parser")
    for link in soup.find_all(href = re.compile("facebook"), class_ = class_):
        if link.get("href") is not None:
            return link.get("href")
        else:
            class_ = "_4-eo _2t9n _50z9" # 有一些在這裡面
            for link in soup.find_all(href = re.compile("facebook"), class_ = class_):
                if link.get("href") is not None:
                    return link.get("href")
# get picture
def get_picture(post_url):
    link = get_post_href(post_url)
    if link is not None:
        driver.get(link)
        source = driver.page_source
        soup = bs(source, "html.parser")
        for pic in soup.find_all("img", {"class": "spotlight"}):
            return pic.get("src")
# get post's pictures (70%)，原因是分享的貼文沒辦法抓到圖片，或是同時貼文超過一張照片也沒辦法，或是照片大小格式特殊，這些要另外做處理有點麻煩，覺得用API去抓照片不是個好方法
for i in range(0, len(post_id)):
    url = "https://www.facebook.com/1455214321359069/posts/" + post_id[i]
    try:
        pic_link = get_picture(url)
        r = requests.get(pic_link, stream = True) # 下載圖片
        with open('pic2/'+str(i)+'.png', 'wb') as out_file: 
            shutil.copyfileobj(r.raw, out_file)
        del r
    except:
        print("post number: ", i, "can't save")

