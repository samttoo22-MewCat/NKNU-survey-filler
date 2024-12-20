import os
import traceback

try:
    
    import sys
    from time import sleep
    from seleniumbase import Driver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import *
    import tkinter as tk
    from tkinter import ttk
    import signal
    import threading
    import ddddocr
    
except:
    input("初始化程式中發生錯誤，請按 Enter 關閉程式")
    sys.exit()
sys.stderr = open('error_log.txt', 'w')

class NknuSurveyFiller():
    def __init__(self):
        def get_ChromeOptions(): 
            options = Options()
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
        signal.signal(signal.SIGINT, self.signal_handler)
        self.browser_executable_path = os.path.abspath("chromedriver.exe")
        self.driver = Driver(headless=False, disable_gpu=True,
                no_sandbox=True, agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36',
                uc=True, chromium_arg="--disable-extensions"
                )
        
        self.wait = WebDriverWait(self.driver, 10, poll_frequency=1, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        
        self.root = tk.Tk()
        self.root.title("NKNU Survey Filler")
        self.root.geometry("400x300")
        self.progress_label = ttk.Label(self.root, text="")
        self.progress_label.pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate')
        self.progress_bar.pack(pady=10)
        self.survey_label = ttk.Label(self.root, text="請輸入學號及密碼")
        self.survey_label.pack(pady=10)
        
        self.account_label = ttk.Label(self.root, text="請輸入學號:")
        self.account_label.pack(pady=5)
        self.account_entry = ttk.Entry(self.root)
        self.account_entry.pack(pady=5)
        
        self.password_label = ttk.Label(self.root, text="請輸入密碼:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        self.start_submit_button = ttk.Button(self.root, text="開始填寫", command=self.start)
        self.start_submit_button.pack(pady=5)
        
        
        self.account = ""
        self.password = ""
        self.ocr = ddddocr.DdddOcr()
        self.ocr.set_ranges(0)
        
        self.root.mainloop()
        self.driver.quit()
        
    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C! Closing ChromeDriver...')
        self.driver.quit()
        sys.exit(0)

     
    def start(self):
        print("開始填寫...")
        self.update_progress("開始填寫...", 5)
        def _start():
            self.driver.get("https://sso.nknu.edu.tw/")
            self.account = self.account_entry.get()
            self.password = self.password_entry.get()
            
            self.fill_verification_code()
            self.login()
            
            self.fill_student_survey()
            self.fill_teacher_survey()
        
        threading.Thread(target=_start).start()
              
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
        login_button_with_auth = self.driver.find_element(By.XPATH, "//input[@id='uLogin']")
        login_button_with_auth.click()
        login_button.click()

        
        try:
            #self.wait.until(EC.alert_is_present())

            pop_up_cancel_button = self.driver.find_element(By.XPATH, "//button[@id='ctl00_ctl26_btQuestionnaire_Skip']")
            pop_up_cancel_button.click()
            self.update_progress("登入成功", 20)
            print("登入成功")
    
        except Exception as e:
            print(e)   
            print(traceback.format_exc())
            
            self.update_progress("登入失敗，請確認學號及密碼是否正確", 10)
            sys.exit(0)
    
    def fill_verification_code(self):
        verification_code_img = self.driver.find_element(By.XPATH, "//div[@class='form-inline']")
        verification_code_img = verification_code_img.find_element(By.TAG_NAME, "img")

        # 確定圖片儲存的路徑
        save_path = 'verification_code.png'  # 可以根據需要修改檔案名稱和路徑

        # 下載圖片
        verification_code_img.screenshot(save_path)
        
        print(f"驗證碼圖片已成功儲存為 {save_path}")

        image = open(f"{save_path}", "rb").read()
        result = self.ocr.classification(image)
        print(f"驗證碼為: {result}")

        verification_code_input = self.driver.find_element(By.XPATH, "//div[@class='form-inline']/input")
        verification_code_input.send_keys(result)

    def fill_student_survey(self):
        self.update_progress("正在填寫學生問卷...", 30, "學生問卷")
        print("正在填寫學生問卷...")
        self.driver.get("https://sso.nknu.edu.tw/StudentProfile/Survey/surveyIR.aspx") 

        try:
            pop_up_cancel_button = self.driver.find_element(By.XPATH, "//button[text()='下次再填']")
            pop_up_cancel_button.click()
        except:
            pass

        try:
            pop_up_enter_button = self.driver.find_element(By.XPATH, "//input[@value='進入']")
            pop_up_enter_button.click()
        except:
            pass

        survey_buttons = self.driver.find_elements(By.XPATH, "//label[text()='非常同意']")
        survey_submit = self.driver.find_element(By.XPATH, "//button[@class='btn btn-primary btn-lg']")
        for button in survey_buttons:
            button.click()
        survey_submit.click()
        try:
            pop_up_enter_button = self.driver.find_element(By.XPATH, "//button[text()='確 定']")
            pop_up_enter_button.click()
        except:
            pass
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
                self.update_progress("問卷填寫完成。", 100, "")
                print("問卷填寫完成。")
                sys.exit()
      

NknuSurveyFiller01 = NknuSurveyFiller()
