from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import auto_download_undetected_chromedriver
from auto_download_undetected_chromedriver import download_undetected_chromedriver
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class NknuSurveyFiller():
    def __init__(self):
        def get_ChromeOptions(): 
            options = uc.ChromeOptions()
            options.add_argument('--start_maximized')
            options.add_argument("--disable-extensions")
            options.add_argument('--disable-application-cache')
            options.add_argument('--disable-gpu')
            #options.add_argument('--headless') 
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
        download_undetected_chromedriver(self.browser_executable_path, undetected=True, arm=False, force_update=True, headless=True)
        self.browser_executable_path = os.path.abspath("chromedriver.exe")
        
        self.driver = uc.Chrome(options=get_ChromeOptions(), driver_executable_path=self.browser_executable_path, version_main=110)
        self.driver.get("https://sso.nknu.edu.tw/")
        self.wait = WebDriverWait(self.driver, 10, poll_frequency=1, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])

        
        self.account = ""
        self.password = ""
        
        print("請輸入學號:")
        self.account = input()
        print("請輸入密碼:")
        self.password = input()
        
        
    def login(self):
        account_block = self.driver.find_element(By.XPATH, "//input[@id='uLoginID']")
        password_block = self.driver.find_element(By.XPATH, "//input[@id='uPassword']")
        remember_button = self.driver.find_element(By.XPATH, "//input[@id='uKeepAlive_ssoLogin']")
        remember_button.click()
        account_block.send_keys(self.account)
        password_block.send_keys(self.password)
        
        login_button = self.driver.find_element(By.XPATH, "//input[@id='uLoginPassAuthorizationCode']")
        login_button.click()
    
    def fill_student_survey(self):
        self.driver.get("https://sso.nknu.edu.tw/StudentProfile/Survey/surveyIR.aspx") 
        survey_buttons = self.driver.find_elements(By.XPATH, "//label[text()='非常同意']")
        survey_submit = self.driver.find_element(By.XPATH, "//button[@class='btn btn-primary btn-lg']")
        for button in survey_buttons:
            button.click()
        survey_submit.click()
           
    def fill_teacher_survey(self):
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
                print("問卷填寫完成。")
                break
        
                   
NknuSurveyFiller = NknuSurveyFiller()
NknuSurveyFiller.login()
try:
    NknuSurveyFiller.fill_student_survey()
except:
    print("學生問卷填寫失敗。")

NknuSurveyFiller.fill_teacher_survey()

