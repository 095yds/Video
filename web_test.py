import streamlit as st
import os, sys


@st.experimental_singleton
def installff():
    os.system('sbase install geckodriver')
    os.system('sudo apt install firefox')
    os.system(
        'ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')


_ = installff()
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)

browser.get('http://baidu.com')
st.write(browser.page_source)
