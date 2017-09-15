# -*- coding: utf-8 -*-

import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

from selenium import webdriver
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#driver = webdriver.PhantomJS(executable_path=r'C:\Users\zlm\Documents\phantomjs-2.1.1-windows\bin\phantomjs.exe')
driver = webdriver.Chrome(executable_path='C:\Users\zlm\Documents\chromedriver/chromedriver.exe')
driver.maximize_window()

username = 'liminglives'
password = 'Liming012389'

#username = "liminglives"
#password = "liming012389"

url = 'https://login.tmall.com/?spm=875.7931836/B.a2226mz.1.mnuqgH&redirectURL=https%3A%2F%2Fwww.tmall.com%2F'
#url = 'https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F'

username_id = "TPL_username_1"
passwd_id = "TPL_password_1"
submit_id = "J_SubmitStatic"

#username_id = "loginname"
#passwd_id = "nloginpwd"
#submit_id = "loginsubmit"


#driver.set_page_load_timeout(30)
driver.get(url)

with open("tmalllogin.html", "w") as f:
	f.write(driver.page_source)

try:
    is_appeared = WebDriverWait(driver, 20).until(lambda x: x.find_element_by_id("J_Quick2Static"))
except Exception, e:
	print "========"
	print e
	sys.exit()
#driver.switch_to_frame(driver.find_element_by_name())

with open("tmalllogin2.html", "w") as f:
	f.write(driver.page_source)

#//*[@id="content"]/div/div[1]/div/div[2]/a
#//*[@id="J_QRCodeLogin"]/div[5]/a[1]
#J_QRCodeLogin > div.login-links > a.forget-pwd.J_Quick2Static

#driver.find_element_by_link_text("密码登录").click()
driver.find_element_by_id("J_Quick2Static").click()
driver.find_element_by_id(username_id).clear()
driver.find_element_by_id(passwd_id).clear()
driver.find_element_by_id(username_id).send_keys(username)
driver.find_element_by_id(passwd_id).send_keys(password)

driver.find_element_by_id(submit_id).click()


while True:
	if driver.current_url != url:
		print "wait"
		break
	time.sleep(1)

cookie="; ".join([item["name"] + "=" + item["value"] +"\n" for item in driver.get_cookies()])
print cookie