import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import sys
import random
import string
import os

# ========================
# 全局配置
# ========================
EMAIL_PREFIX = ""  # 邮箱前缀
EMAIL_PASSWORD = ""  # 邮箱密码
# ========================

def generate_random_string(min_length=3, max_length=5):
    length = random.randint(min_length, max_length)
    name = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    return name.capitalize()

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$"
    return ''.join(random.choice(chars) for _ in range(length))

def simulate_human_input(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def open_email_website():
    print("Starting browser...")
    driver2 = None
    try:
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver2 = uc.Chrome(options=options, use_subprocess=True)
        with open('stealth.min.js', 'r') as f:
            stealth_js = f.read()
        driver2.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_js
        })
        driver2.get("https://www.2925.com/#/")
        time.sleep(5)
        print("Logging into email...")
        try:
            username_input = WebDriverWait(driver2, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".el-input__inner[type='text']"))
            )
            simulate_human_input(username_input, EMAIL_PREFIX)
            time.sleep(1)
            
            password_input = driver2.find_element(By.CSS_SELECTOR, ".el-input__inner[type='password']")
            simulate_human_input(password_input, EMAIL_PASSWORD)
            time.sleep(1)
            
            login_button = WebDriverWait(driver2, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-button--primary"))
            )
            driver2.execute_script("arguments[0].click();", login_button)
            print("\nPlease check verification code manually...")
            input("Press Enter to close email window...") 
        finally:
            if driver2:
                driver2.quit()      
    except Exception as e:
        print(f"Email operation failed: {str(e)}")
        if driver2:
            driver2.quit()

def register_account():
    first_name = generate_random_string()
    last_name = generate_random_string()
    print(f"Using name: {first_name} {last_name}")
    email_suffix = generate_random_string(3, 6)
    email = f"{EMAIL_PREFIX}{email_suffix}@2925.com"
    password = generate_password()
    print(f"Using email: {email}")
    print("Starting browser...")
    options = uc.ChromeOptions()
    
    # 只保留核心配置
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-cache')
    options.add_argument('--disk-cache-size=1')
    
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        # 注入 stealth.js
        with open('stealth.min.js', 'r') as f:
            stealth_js = f.read()
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_js
        })
        
        try:
            print("Accessing login page...")
            driver.get("https://authenticator.cursor.sh/?client_id=client_01GS6W3C96KW4WRS6Z93JCE2RJ&redirect_uri=https%3A%2F%2Fcursor.com%2Fapi%2Fauth%2Fcallback&response_type=code&state=%257B%2522returnTo%2522%253A%2522%252Fsettings%2522%257D")
            time.sleep(8) 
        
            print("Entering registration...")
            try:
                driver.get("https://authenticator.cursor.sh/sign-up")   
            except Exception as e:
                print(f"Failed to enter registration: {str(e)}")
                time.sleep(5)
            print("Filling registration information...")
            firstname_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='given-name']"))
            )
            simulate_human_input(firstname_input, first_name)
            
            lastname_input = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='family-name']")
            simulate_human_input(lastname_input, last_name)
            
            email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            simulate_human_input(email_input, email)
            continue_button = driver.find_element(By.CSS_SELECTOR, "button[name='intent'][value='sign-up']")
            continue_button.click()
            print("\nPlease complete human verification...")
            print("Press Enter to continue after verification...")
            input()
            print("Entering password...")
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            simulate_human_input(password_input, password)
            next_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            next_button.click()
            
            print("\nPlease complete second human verification...")
            print("Press Enter to continue after verification...")
            input()
            open_email_website()
            print("\nPlease complete final human verification...")
            print("Press Enter to continue after verification...")
            input()
            account_info = {
                "email": email,
                "password": password
            }
            
            with open("cursor_account.json", "w") as f:
                json.dump(account_info, f, indent=2)
            print("Account information saved to cursor_account.json")
            config_path = os.path.join(os.getenv("APPDATA"), "Cursor", "config.json")
            if os.path.exists(config_path):
                os.remove(config_path)
            with open(config_path, "w") as f:
                json.dump(account_info, f, indent=2)
            print("Cursor configuration updated")
            
            print("\nRegistration complete, press Enter to close browser...")
            input()
            
        finally:
            if driver:
                driver.quit()
                
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        raise

def main():
    try:
        register_account()
    except Exception as e:
        print(f"Program execution error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
