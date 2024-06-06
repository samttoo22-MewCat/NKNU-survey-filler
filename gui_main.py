import sys
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import auto_download_undetected_chromedriver
from auto_download_undetected_chromedriver import download_undetected_chromedriver
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import tkinter as tk
from tkinter import ttk

class NknuSurveyFiller():
    def __init__(self):
        def get_ChromeOptions(): 
            options = uc.ChromeOptions()
            options.add_argument('--start_maximized')
            options.add_argument("--disable-extensions")
            options.add_argument('--disable-application-cache')
            options.add_argument('--disable-gpu')
            options.add_argument('--headless') 
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-notifications")
            options.add_argument("--incognito")
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--user-data-dir={}".format(os.path.abspath("profile1")))
            return options
        
        self.browser_executable_path = ""
        download_undetected_chromedriver(self.browser_executable_path, undetected=True, arm=False, force_update=True)
        self.browser_executable_path = os.path.abspath("chromedriver.exe")
        
        self.driver = uc.Chrome(options=get_ChromeOptions(), driver_executable_path=self.browser_executable_path, version_main=110)
        self.driver.get("https://sso.nknu.edu.tw/")
        self.wait = WebDriverWait(self.driver, 10, poll_frequency=1, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])

        self.account = ""
        self.password = ""
        
        self.root = tk.Tk()
        self.root.title("NKNU Survey Filler")
        self.root.geometry("400x300")
        self.progress_label = ttk.Label(self.root, text="Ready")
        self.progress_label.pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate')
        self.progress_bar.pack(pady=10)
        self.survey_label = ttk.Label(self.root, text="")
        self.survey_label.pack(pady=10)
        
        self.account_label = ttk.Label(self.root, text="請輸入學號:")
        self.account_label.pack(pady=5)
        self.account_entry = ttk.Entry(self.root)
        self.account_entry.pack(pady=5)
        
        self.password_label = ttk.Label(self.root, text="請輸入密碼:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        self.start_button = ttk.Button(self.root, text="開始填寫", command=self.start)
        self.start_button.pack(pady=10)
        
        self.root.mainloop()
        
    def start(self):
        self.account = self.account_entry.get()
        self.password = self.password_entry.get()
        self.login()
        self.fill_student_survey()
        self.fill_teacher_survey()
        
    def update_progress(self, text, value, survey_text=""):
        self.root.after(0, self.progress_label.config, {"text": text})
        self.root.after(0, self.progress_bar.config, {"value": value})
        self.root.after(0, self.survey_label.config, {"text": survey_text})
        self.root.update_idletasks()
        
    def login(self):
        self.update_progress("正在登入...", 10)
        print("正在登入...")
        account_block = self.driver.find_element(By.XPATH, "//input[@id='uLoginID']")
        password_block = self.driver.find_element(By.XPATH, "//input[@id='uPassword']")
        remember_button = self.driver.find_element(By.XPATH, "//input[@id='uKeepAlive_ssoLogin']")
        remember_button.click()
        account_block.send_keys(self.account)
        password_block.send_keys(self.password)
        
        login_button = self.driver.find_element(By.XPATH, "//input[@id='uLoginPassAuthorizationCode']")
        login_button.click()
        self.update_progress("登入成功", 20)
        print("登入成功")
    
    def fill_student_survey(self):
        self.update_progress("正在填寫學生問卷...", 30, "學生問卷")
        print("正在填寫學生問卷...")
        self.driver.get("https://sso.nknu.edu.tw/StudentProfile/Survey/surveyIR.aspx") 
        survey_buttons = self.driver.find_elements(By.XPATH, "//label[text()='非常同意']")
        survey_submit = self.driver.find_element(By.XPATH, "//button[@class='btn btn-primary btn-lg']")
        for button in survey_buttons:
            button.click()
        survey_submit.click()
        self.update_progress("學生問卷填寫完成", 60, "")
        print("學生問卷填寫完成")
           
    def fill_teacher_survey(self):
        self.update_progress("正在填寫教師問卷...", 70, "教師問卷")
        print("正在填寫教師問卷...")
        self.driver.get("https://sso.nknu.edu.tw/StudentProfile/Survey/Default.aspx")
        begin_survey_button = self.driver.find_element(By.XPATH, "//input[@value='開始填答']")
        begin_survey_button.click()
        while(True):
            try:
                survey_button = self.driver.find_element(By.XPATH, "//a[text()='評量填寫']")

                self.driver.execute_script("arguments[0].click();", survey_button)
                self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@value='5']")))
                five_stars = self.driver.find_elements(By.XPATH, "//input[@value='5']") 
                for f in five_stars:
                    f.click()
                submit_button = self.driver.find_element(By.XPATH, "//input[@value='填好送出']")
                submit_button.click()
                alert = self.driver.switch_to.alert
                alert.accept()
                self.driver.get("https://sso.nknu.edu.tw/StudentProfile/Survey/survey.aspx")
            except Exception as e:
                self.update_progress("教師問卷填寫完成", 100, "")
                print("問卷填寫完成。")
                sys.exit()
                
NknuSurveyFiller01 = NknuSurveyFiller()