import streamlit as st
import google_colab_selenium as gs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from bs4 import BeautifulSoup

st.title("Twitter Scraper")

email = st.text_input("Email")
username = st.text_input("Username (if prompted)")
password = st.text_input("Password", type="password")
confirmation_code = st.text_input("Confirmation Code (if prompted)")

if st.button("Start Scraping"):
    driver = gs.Chrome()

    #@title Connexion
    driver.get('https://twitter.com/i/flow/login')
    time.sleep(3)
    login = driver.find_element(By.XPATH,'/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input')
    login.send_keys(email)
    next_page = driver.find_element(By.XPATH,'/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div/span/span').click()
    time.sleep(3)
    
    try:
        confirm_username = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
        confirm_username.send_keys(username)
        nnext_page = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div').click()
        time.sleep(3)
    except:
        st.write("Username confirmation page not found, continuing...")
        pass
    
    password_input = driver.find_element(By.XPATH,'/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    password_input.send_keys(password)
    final_page = driver.find_element(By.XPATH,'/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div').click()
    time.sleep(3)
    
    try:
        code_verify = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
        code_verify.send_keys(confirmation_code)
        home_page = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div').click()
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]')))
        time.sleep(3)
    except:
        st.write("Code confirmation page not found, continuing...")
        pass

    st.write("Scraping completed")
