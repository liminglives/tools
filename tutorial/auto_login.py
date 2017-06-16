# -*- coding: utf-8 -*-

import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

from selenium import webdriver
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class AutoLogin():
	def __init__(self, driver, url, usrename, password, username_html_id=None, passwd_html_id=None, submit_html_id=None):
		self._driver = driver
		self._url = url
		self._username = usrename
		self._password = password
		self._username_html_id = username_html_id
		self._password_html_id = passwd_html_id
		self._submit_html_id = submit_html_id
		self._wait_time = 10

	def get_driver(self):
		return self._driver

	def open_url(self):
		self._driver.maximize_window()
		self._driver.get(self._url)

	def wait_load(self):
	    if self._username_html_id is None:
	    	return True
		try:
			WebDriverWait(driver, 60).until(lambda x: x.find_element_by_id(self._username_html_id))
			return True
		except Exception, e:
			print e
			return False

	def _fill_username(self):
		username = self._driver.find_element_by_id(self._username_html_id)
		username.clear()
		username.click()
		username.send_keys(self._username)

	def _fill_password(self):
		password = self._driver.find_element_by_id(self._password_html_id)
		password.clear()
		password.click()
		password.send_keys(self._password)

	def simple_login(self):
		self._fill_username()
		self._fill_password()
		self._driver.find_element_by_id(self._submit_html_id).click()

	def set_wait_time(self, wait_time):
		self._wait_time = wait_time

	def wait(self):
		t = 0
		ret = False
		while True and t < self._wait_time:
			if self._driver.current_url != url:
				print "redict success"
				ret = True
				break
			time.sleep(1)
			t += 1
		return ret

	def get_cookies(self):
		return "; ".join([item["name"] + "=" + item["value"] +"\n" for item in self._driver.get_cookies()])

	def fill_username(self, find_element_method, element):
		if(find_element_method == "id"):		
			WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.ID, element)))#等待10s,每500ms查询一次,直到元素加载完毕或超过10s结束
			username = self._driver.find_element_by_id(element)

		elif(find_element_method == "name"):
			WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.NAME, element)))
			username = self._driver.find_element_by_name(element)

		elif(find_element_method == "xpath"):
			WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, element)))
			username = self._driver.find_element_by_xpath(element)
		else:
			print "find element error!"	

		username.clear()
		username.click()
		username.send_keys(self._username)

	def fill_password(self, find_element_method, element):
		if(find_element_method == "id"):
			WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.ID, element)))
			password = self._driver.find_element_by_id(element)

		elif(find_element_method == "name"):
			WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.NAME, element)))
			password = self._driver.find_element_by_name(element)

		elif(find_element_method == "xpath"):
			WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, element)))
			password = self._driver.find_element_by_xpath(element)
		else:
			print "find element error!"

		password.clear()
		password.click()
		password.send_keys(self._password)

	def click_element(self, find_element_method, element):
		if(find_element_method == "id"):
			self._driver.find_element_by_id(element).click()

		elif(find_element_method == "name"):
			self._driver.find_element_by_name(element).click()

		elif(find_element_method == "xpath"):
			self._driver.find_element_by_xpath(element).click()
		elif (find_element_method == "link_text"):
			self._driver.find_element_by_link_text(element).click()
		else:
			print "find element error!"   	

	def click_submit(self, find_element_method, element):
		if(find_element_method == "id"):
			WebDriverWait(self._driver, 5).until(EC.presence_of_element_located((By.ID, element)))
			self._driver.find_element_by_id(element).click()

		elif(find_element_method == "name"):
			WebDriverWait(self._driver, 5).until(EC.presence_of_element_located((By.NAME, element)))
			self._driver.find_element_by_name(element).click()

		elif(find_element_method == "xpath"):
			WebDriverWait(self._driver, 5).until(EC.presence_of_element_located((By.XPATH, element)))
			self._driver.find_element_by_xpath(element).click()
		else:
			print "find element error!"

	def switch_to_iframe(self, find_element_method, element):
		WebDriverWait(self._driver, 10).until(EC.presence_of_element_located((By.XPATH, element)))
		self._driver.switch_to_frame(self._driver.find_element_by_xpath(element))

	def save_page_source(self, filename):
		with open(filename, "w") as f:
			f.write(self._driver.page_source)


def login_jd():
	driver = webdriver.Chrome(executable_path='C:\Users\zlm\Documents\chromedriver/chromedriver.exe')
	url = "https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F"
	username = "liminglives"
	password = "liming012389"
	username_id = "loginname"
	passwd_id = "nloginpwd"
	submit_id = "loginsubmit"
	al = AutoLogin(driver, url, username, password, username_id, passwd_id, submit_id)
	al.open_url()
	al.wait_load()
	al.click_element("link_text", "账户登录")
	al.simple_login()
	al.wait()
	print al.get_cookies()
	print "success"

def login_360():
	driver = webdriver.Chrome(executable_path='C:\Users\zlm\Documents\chromedriver/chromedriver.exe')
	username = '18818213619'
	password = 'liming012389'
	al = AutoLogin(driver, "http://i.360.cn/login?src=pcw_so&destUrl=https%3A%2F%2Fwww.so.com%2F", username, password)
	al.open_url()
	al.save_page_source("360.html")
	al.fill_username("name", "account")
	al.fill_password("name", "password")
	al.click_submit("xpath", '//*[@id="loginWrap"]/div[1]/div/div/div[2]/form/p[5]/input')
	print al.get_cookies() 
	print "success..."

def login_baidu():
	driver = webdriver.Chrome(executable_path='C:\Users\zlm\Documents\chromedriver/chromedriver.exe')
	url = 'https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F'
	username = "liminglives"
	password = "liming"
	username_id = "TANGRAM__PSP_3__userName"
	password_id = "TANGRAM__PSP_3__password"
	submit_id = "TANGRAM__PSP_3__submit"
	al = AutoLogin(driver, url, username, password, username_id, password_id, submit_id)
	al.open_url()
	al.wait_load()
	al.simple_login()
	al.wait()
	print al.get_cookies()
	print "success"

if __name__ == "__main__":
	login_baidu()