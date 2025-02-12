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
import re

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

def get_chrome_options():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--mute-audio')
    options.add_argument('--no-service-autorun')
    user_data_dir = os.path.join(os.getcwd(), 'chrome_profile')
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-client-side-phishing-detection')
    
    return options

def get_latest_verification_code(driver):
    try:
        print("Waiting for email to load...")
        # Wait for the first email to be clickable
        first_email = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".el-table__row"))
        )
        first_email.click()    
        email_content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".mail-content"))
        )
        content_text = email_content.text
        verification_code = re.search(r'\b\d{6}\b', content_text)
        
        if verification_code:
            code = verification_code.group(0)
            print(f"Found verification code: {code}")
            return code
        else:
            print("Verification code not found in email")
            return None
            
    except Exception as e:
        print(f"Error getting verification code: {str(e)}")
        return None

def login_email(driver):
    try:
        print("Logging into email...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".el-input__inner[type='text']"))
        )
        username_input = driver.find_element(By.CSS_SELECTOR, ".el-input__inner[type='text']")
        simulate_human_input(username_input, EMAIL_PREFIX)
        password_input = driver.find_element(By.CSS_SELECTOR, ".el-input__inner[type='password']")
        simulate_human_input(password_input, EMAIL_PASSWORD)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-button--primary"))
        )
        driver.execute_script("arguments[0].click();", login_button)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".el-table__row"))
        )
        print("Email login successful")
        return True
        
    except Exception as e:
        print(f"Email login failed: {str(e)}")
        return False

def switch_to_new_tab(driver, url):
    try:
        original_window = driver.current_window_handle
        print(f"Opening new tab: {url}")
        driver.execute_script(f"window.open('{url}', '_blank');")
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return True
    except Exception as e:
        print(f"Error switching to new tab: {str(e)}")
        return False

def register_account():
    first_name = generate_random_string()
    last_name = generate_random_string()
    print(f"Using name: {first_name} {last_name}")
    email_suffix = generate_random_string(3, 6)
    email = f"{EMAIL_PREFIX}{email_suffix}@2925.com"
    password = generate_password()
    print(f"Using email: {email}")
    print("Starting browser...")  
    options = get_chrome_options()
    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        with open('stealth.min.js', 'r') as f:
            stealth_js = f.read()
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_js
        })
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': False})       
        print("Accessing login page...")
        driver.get("https://authenticator.cursor.sh/sign-up")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
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
        input("Press Enter to continue after verification...")
        
        print("Entering password...")
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        simulate_human_input(password_input, password)
        
        next_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        next_button.click()
        
        print("\nPlease complete second human verification...")
        input("Press Enter to continue after verification...")
        
        # Open email in new tab
        if not switch_to_new_tab(driver, 'https://www.2925.com/#/mailList'):
            print("Failed to open email in new tab. Retrying...")
            try:
                driver.get('https://www.2925.com/#/mailList')
            except Exception as e:
                print(f"Failed to access email website: {str(e)}")
                print("Please open email website manually...")
                input("Press Enter after opening email website...")
        
        # Try to login to email
        if not login_email(driver):
            print("Failed to login to email. Please login manually...")
            input("Press Enter after logging in...")
        
        print("\nPlease check verification code and complete verification manually...")
        input("Press Enter after verification is complete...")
        
        # Switch back to registration tab
        driver.switch_to.window(driver.window_handles[0])
        
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

def main():
    try:
        register_account()
    except Exception as e:
        print(f"Program execution error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
