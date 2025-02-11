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
    """生成随机字符串（字母）"""
    length = random.randint(min_length, max_length)
    name = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    return name.capitalize()

def generate_password(length=16):
    """生成随机密码"""
    chars = string.ascii_letters + string.digits + "!@#$"
    return ''.join(random.choice(chars) for _ in range(length))

def simulate_human_input(element, text):
    """模拟人类输入文本"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def open_email_website():
    """打开邮箱网站"""
    print("正在启动新的浏览器窗口...")
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
        
        print("访问邮箱登录页面...")
        driver2.get("https://www.2925.com/#/")
        time.sleep(5)
        
        print("登录邮箱...")
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
            
            print("\n请手动查看验证码...")
            input("按回车键关闭邮箱窗口...")
            
        finally:
            if driver2:
                driver2.quit()
                
    except Exception as e:
        print(f"邮箱操作失败: {str(e)}")
        if driver2:
            driver2.quit()

def register_account():
    """注册 Cursor 账号"""
    first_name = generate_random_string()
    last_name = generate_random_string()
    print(f"使用名字: {first_name} {last_name}")
    email_suffix = generate_random_string(3, 6)
    email = f"{EMAIL_PREFIX}{email_suffix}@2925.com"
    password = generate_password()
    print(f"使用邮箱: {email}")
    print("正在启动浏览器...")
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
    
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
    
        with open('stealth.min.js', 'r') as f:
            stealth_js = f.read()
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_js
        })
        
        try:
            print("正在访问登录页面...")
            driver.get("https://authenticator.cursor.sh/?client_id=client_01GS6W3C96KW4WRS6Z93JCE2RJ&redirect_uri=https%3A%2F%2Fcursor.com%2Fapi%2Fauth%2Fcallback&response_type=code&state=%257B%2522returnTo%2522%253A%2522%252Fsettings%2522%257D")
            time.sleep(8) 
        
            print("正在寻找注册链接...")
            try:
                # 尝试多种定位方式
                signup_link = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Sign up')]")) or
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.BrandedLink[href*='sign-up']")) or
                    EC.presence_of_element_located((By.LINK_TEXT, "Sign up"))
                )
                print("找到注册链接，准备点击...")
                
                # 使用 JavaScript 点击
                driver.execute_script("arguments[0].scrollIntoView(true);", signup_link)
                time.sleep(2)
                driver.execute_script("arguments[0].click();", signup_link)
                print("已点击注册链接")
                
                # 确保页面加载完成
                time.sleep(5)
                
            except Exception as e:
                print(f"点击注册链接时出错: {str(e)}")
                print("尝试备用方案...")
                # 备用方案：直接访问注册页面
                driver.get("https://authenticator.cursor.sh/sign-up")
                time.sleep(5)
            
            # 填写表单
            print("正在填写注册信息...")
            firstname_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='given-name']"))
            )
            simulate_human_input(firstname_input, first_name)
            
            lastname_input = driver.find_element(By.CSS_SELECTOR, "input[autocomplete='family-name']")
            simulate_human_input(lastname_input, last_name)
            
            email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            simulate_human_input(email_input, email)
            
            # 点击 Continue 按钮
            continue_button = driver.find_element(By.CSS_SELECTOR, "button[name='intent'][value='sign-up']")
            continue_button.click()
            
            print("\n请完成人机验证...")
            print("完成验证后请按回车键继续...")
            input()
            
            # 填写密码
            print("正在填写密码...")
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            simulate_human_input(password_input, password)
            next_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            next_button.click()
            
            print("\n请完成第二次人机验证...")
            print("完成验证后请按回车键继续...")
            input()
            open_email_website()
            print("\n请完成最后一次人机验证...")
            print("完成验证后请按回车键继续...")
            input()
            account_info = {
                "email": email,
                "password": password
            }
            
            with open("cursor_account.json", "w") as f:
                json.dump(account_info, f, indent=2)
            print("账号信息已保存到 cursor_account.json")
            config_path = os.path.join(os.getenv("APPDATA"), "Cursor", "config.json")
            if os.path.exists(config_path):
                os.remove(config_path)
            with open(config_path, "w") as f:
                json.dump(account_info, f, indent=2)
            print("Cursor 配置已更新")
            
            print("\n注册完成,按回车键关闭浏览器...")
            input()
            
        finally:
            if driver:
                driver.quit()
                
    except Exception as e:
        print(f"注册过程中出错: {str(e)}")
        raise

def main():
    try:
        register_account()
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 