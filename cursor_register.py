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
from DrissionPage import ChromiumPage, ChromiumOptions
import pyautogui

# ========================
# 全局配置
# ========================
EMAIL_PREFIX = ""  # 邮箱前缀
EMAIL_PASSWORD = ""  # 邮箱密码
# ========================

def generate_random_string(min_length=4, max_length=8):
    length = random.randint(min_length, max_length)
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_password():
    return 'Aa1@' + generate_random_string(8, 12)

def simulate_human_input(element, text):
    for char in text:
        element.input(char)
        time.sleep(random.uniform(0.1, 0.3))

def simulate_smooth_mouse_movement(x, y, duration=1.0):
    start_x, start_y = pyautogui.position()
    control_points = [
        (start_x, start_y),  # 起点
        (start_x + (x - start_x) * 0.4 + random.randint(-100, 100), 
         start_y + (y - start_y) * 0.2 + random.randint(-50, 50)),  
        (start_x + (x - start_x) * 0.6 + random.randint(-100, 100), 
         start_y + (y - start_y) * 0.8 + random.randint(-50, 50)),
        (x, y)  # 终点
    ]
    steps = 50
    path = []
    for i in range(steps + 1):
        t = i / steps
        px = (1-t)**3 * control_points[0][0] + \
             3*t*(1-t)**2 * control_points[1][0] + \
             3*t**2*(1-t) * control_points[2][0] + \
             t**3 * control_points[3][0]
        py = (1-t)**3 * control_points[0][1] + \
             3*t*(1-t)**2 * control_points[1][1] + \
             3*t**2*(1-t) * control_points[2][1] + \
             t**3 * control_points[3][1]
        path.append((px, py))
    path = [(x + random.uniform(-2, 2), y + random.uniform(-2, 2)) for x, y in path]
    start_time = time.time()
    for point in path:
        elapsed = time.time() - start_time
        if elapsed < duration:
            pyautogui.moveTo(point[0], point[1], duration=duration/steps)
            time.sleep(random.uniform(0.001, 0.003))

def simulate_human_click(x, y):
    offset_x = random.randint(-2, 2)
    offset_y = random.randint(-2, 2)
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=random.uniform(0.2, 0.4))
    time.sleep(random.uniform(0.1, 0.2))
    pyautogui.click()
    move_away_x = x + random.randint(50, 100)
    move_away_y = y + random.randint(50, 100)
    pyautogui.moveTo(move_away_x, move_away_y, duration=random.uniform(0.2, 0.3))

def get_chrome_options():
    options = ChromiumOptions()
    options.set_argument('--no-sandbox')
    options.set_argument('--disable-dev-shm-usage')
    options.set_argument('--disable-gpu')
    options.set_argument('--window-position=0,0')
    options.set_argument('--window-size=1920,1080')
    options.set_argument('--disable-blink-features=AutomationControlled')
    options.set_argument('--disable-web-security')
    options.set_argument('--ignore-certificate-errors')
    options.set_argument('--disable-notifications')
    options.set_argument('--disable-popup-blocking')
    options.set_argument('--disable-logging')
    options.set_argument('--no-default-browser-check')
    options.set_argument('--no-first-run')
    options.set_argument('--disable-background-networking')
    return options

def get_latest_verification_code(driver):
    try:
        print("Waiting for email to load...")
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
        username_input = driver.ele('css:.el-input__inner[type="text"]')
        simulate_human_input(username_input, EMAIL_PREFIX)
        password_input = driver.ele('css:.el-input__inner[type="password"]')
        simulate_human_input(password_input, EMAIL_PASSWORD)     
        login_button = driver.ele('css:.el-button--primary')
        login_button.click()
        driver.wait.ele_exists('css:.el-table__row', timeout=10)
        print("Email login successful")
        return True
    except Exception as e:
        print(f"Email login failed: {str(e)}")
        return False

def switch_to_new_tab(driver, url):
    try:
        driver.new_tab(url)
        return True
    except Exception as e:
        print(f"Error switching to new tab: {str(e)}")
        return False

class CloudflareBypasser:
    def __init__(self, driver: ChromiumPage, max_retries=3, log=True):
        self.driver = driver
        self.max_retries = max_retries
        self.log = log

    def search_recursively_shadow_root_with_iframe(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.child().tag == "iframe":
                return ele.shadow_root.child()
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_iframe(child)
                if result:
                    return result
        return None

    def search_recursively_shadow_root_with_cf_input(self, ele):
        if ele.shadow_root:
            if ele.shadow_root.ele("tag:input"):
                return ele.shadow_root.ele("tag:input")
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_cf_input(child)
                if result:
                    return result
        return None
    
    def locate_cf_button(self):
        button = None
        eles = self.driver.eles("tag:input")
        for ele in eles:
            if "name" in ele.attrs.keys() and "type" in ele.attrs.keys():
                if "turnstile" in ele.attrs["name"] and ele.attrs["type"] == "hidden":
                    button = ele.parent().shadow_root.child()("tag:body").shadow_root("tag:input")
                    break
            
        if button:
            return button
        else:
            self.log_message("Basic search failed. Searching for button recursively.")
            ele = self.driver.ele("tag:body")
            iframe = self.search_recursively_shadow_root_with_iframe(ele)
            if iframe:
                button = self.search_recursively_shadow_root_with_cf_input(iframe("tag:body"))
            else:
                self.log_message("Iframe not found. Button search failed.")
            return button

    def log_message(self, message):
        if self.log:
            print(message)

    def click_verification_button(self):
        try:
            button = self.locate_cf_button()
            if button:
                self.log_message("Verification button found. Attempting to click.")
                button.click()
            else:
                self.log_message("Verification button not found.")

        except Exception as e:
            self.log_message(f"Error clicking verification button: {e}")

    def is_bypassed(self):
        try:
            title = self.driver.title.lower()
            return "just a moment" not in title
        except Exception as e:
            self.log_message(f"Error checking page title: {e}")
            return False

    def bypass(self):
        try_count = 0
        while not self.is_bypassed():
            if 0 < self.max_retries + 1 <= try_count:
                self.log_message("Exceeded maximum retries. Bypass failed.")
                break

            self.log_message(f"Attempt {try_count + 1}: Verification page detected. Trying to bypass...")
            self.click_verification_button()

            try_count += 1
            time.sleep(2)

        if self.is_bypassed():
            self.log_message("Bypass successful.")
            return True
        else:
            self.log_message("Bypass failed.")
            return False

def load_click_positions():
    try:
        with open('cloudflare_positions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_click_positions(positions):
    with open('cloudflare_positions.json', 'w') as f:
        json.dump(positions, f, indent=2)

def record_click_position():
    print("请在 5 秒内将鼠标移动到验证按钮位置,并确保这个是浏览器常用的位置，如果位置变化需要去配置文件删除...")
    time.sleep(5)
    x, y = pyautogui.position()
    return {'x': x, 'y': y}

def handle_cloudflare_verification(driver, max_attempts=1):
    success = False
    click_positions = load_click_positions()
    if not click_positions:
        print("未找到保存的点击位置，需要手动记录")
        click_positions = {
            'main_button': record_click_position(),
            'alternative_button': record_click_position()
        }
        save_click_positions(click_positions)
    initial_title = driver.title.lower()
    print("Attempting main verification button...")
    main_pos = click_positions['main_button']
    simulate_human_click(main_pos['x'], main_pos['y'])
    print("Clicked main verification button")
    time.sleep(2)
    verification_success = False
    for _ in range(5):
        current_title = driver.title.lower()
        if current_title != initial_title and "just a moment" not in current_title:
            print("Title changed, verifying success...")
            try:
                if driver.ele_exists('css:input[type="password"]'):
                    verification_success = True
                    print("Verification successful! Password input found.")
                    break
            except:
                pass
        time.sleep(1)
    
    if verification_success:
        success = True
    else:
        print("Main button failed. Waiting 5 seconds before trying alternative button...")
        time.sleep(5)     
        print("Trying alternative button...")
        alt_pos = click_positions['alternative_button']
        simulate_human_click(alt_pos['x'], alt_pos['y'])
        print("Clicked alternative button")        
        time.sleep(2)
        for _ in range(5):
            current_title = driver.title.lower()
            if current_title != initial_title and "just a moment" not in current_title:
                try:
                    if driver.ele_exists('css:input[type="password"]'):
                        success = True
                        print("Verification successful using alternative button!")
                        break
                except:
                    pass
            time.sleep(1)
    if not success:
        print("Automatic verification failed. Switching to manual verification...")
        input("Please complete verification manually and press Enter to continue...")
        try:
            if driver.ele_exists('css:input[type="password"]'):
                success = True
                print("Manual verification successful!")
        except:
            print("Manual verification failed or timed out")
    
    return success

def register_account():
    first_name = generate_random_string()
    last_name = generate_random_string()
    print(f"Using name: {first_name} {last_name}")
    email_suffix = generate_random_string(3, 6)
    email = f"{EMAIL_PREFIX}{email_suffix}@2925.com"
    password = generate_password()
    print(f"Using email: {email}")
    print("Starting browser...")  

    try:
        options = get_chrome_options()
        driver = ChromiumPage(addr_or_opts=options)
        print("Browser started in visible mode with headless configurations")        
        print("Accessing login page...")
        driver.get("https://authenticator.cursor.sh/sign-up")
        driver.wait.doc_loaded()
        time.sleep(2)
        print("Waiting for registration form...")
        driver.wait.ele_displayed('css:input[autocomplete="given-name"]', timeout=10)
        print("Filling registration information...")
        firstname_input = driver.ele('css:input[autocomplete="given-name"]')
        simulate_human_input(firstname_input, first_name)      
        lastname_input = driver.ele('css:input[autocomplete="family-name"]')
        simulate_human_input(lastname_input, last_name)  
        email_input = driver.ele('css:input[type="email"]')
        simulate_human_input(email_input, email)
        continue_button = driver.ele('css:button[name="intent"][value="sign-up"]')
        continue_button.click()
        print("\nWaiting for page transition (2 seconds)...")
        time.sleep(2)
        print("\nStarting Cloudflare verification...")
        if not handle_cloudflare_verification(driver):
            print("Cloudflare bypass failed after all attempts")
            print("Current page title:", driver.title)
            driver.get_screenshot('verification_failed.png')
            response = input("验证失败。是否需要更新点击位置？(y/n): ")
            if response.lower() == 'y':
                click_positions = {
                    'main_button': record_click_position(),
                    'alternative_button': record_click_position()
                }
                save_click_positions(click_positions)
                print("点击位置已更新，请重新运行程序")
                return
            
            input("Please complete verification manually and press Enter to continue...")
        print("\nWaiting for password input (up to 10 seconds)...")
        try:
            driver.wait.ele_displayed('css:input[type="password"]', timeout=10)
        except:
            print("Password input not found after timeout")
            print("Current page title:", driver.title)
            driver.get_screenshot('password_input_missing.png')
            input("Please check if the page has loaded correctly and press Enter to continue...")
        
        print("Entering password...")
        password_input = driver.ele('css:input[type="password"]')
        simulate_human_input(password_input, password)
        
        next_button = driver.ele('css:button[type="submit"]')
        next_button.click()

        print("\nChecking for post-password Cloudflare verification...")
        time.sleep(2) 
        
        if "just a moment" in driver.title.lower():
            print("Post-password Cloudflare verification detected...")
            if not handle_cloudflare_verification(driver):
                print("Post-password verification failed")
                input("Please complete verification manually and press Enter to continue...")
        
        if not switch_to_new_tab(driver, 'https://www.2925.com/#/mailList'):
            print("Failed to open email in new tab. Retrying...")
            try:
                driver.get('https://www.2925.com/#/mailList')
            except Exception as e:
                print(f"Failed to access email website: {str(e)}")
                print("Please open email website manually...")
                input("Press Enter after opening email website...")
        
        if not login_email(driver):
            print("Failed to login to email. Please login manually...")
            input("Press Enter after logging in...")
        
        print("\nPlease check verification code and complete verification manually...")
        input("Press Enter after verification is complete...")

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
        
    except Exception as e:
        print(f"Error during registration: {str(e)}")
    finally:
        if driver:
            driver.quit()

def locate_and_click_button(button_image_path: str, timeout: int = 10, confidence: float = 0.8) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateOnScreen(button_image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                simulate_smooth_mouse_movement(center.x, center.y, duration=random.uniform(0.8, 1.2))

                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.moveRel(random.randint(-2, 2), random.randint(-2, 2), duration=0.1)
                pyautogui.click()
                time.sleep(random.uniform(0.1, 0.3))
                simulate_smooth_mouse_movement(
                    center.x + random.randint(50, 200),
                    center.y + random.randint(50, 200)
                )
                
                print(f'Successfully clicked button: {button_image_path}')
                return True
                
        except pyautogui.ImageNotFoundException:
            time.sleep(0.5)
            
    print(f'Button not found: {button_image_path}')
    return False

def main():
    try:
        register_account()
    except Exception as e:
        print(f"Program execution error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
