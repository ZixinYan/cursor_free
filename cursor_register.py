import time
import json
import sys
import random
import string
import os
from curl_cffi import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc
import subprocess
import psutil

def generate_password(length=16):
    """生成随机密码"""
    chars = string.ascii_letters + string.digits + "!@#$"
    return ''.join(random.choice(chars) for _ in range(length))

def wait_for_element(driver, by, value, timeout=10):
    """等待元素出现并返回"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"等待元素超时: {value}")
        return None

def wait_for_captcha(driver):
    """等待用户完成人机验证"""
    print("等待人机验证出现...")
    time.sleep(5) 
    
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']"))
        )
        
        print("检测到人机验证，正在处理...")
        
        driver.switch_to.frame(iframe)
        
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']"))
        )
        checkbox.click()
        
        driver.switch_to.default_content()
        
        print("等待验证完成...")
        max_wait = 60 
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")
                if not iframes:
                    print("人机验证完成！")
                    return True
                error_messages = driver.find_elements(By.CSS_SELECTOR, ".error-message, .error-text")
                if error_messages and any(msg.is_displayed() for msg in error_messages):
                    print("验证出现错误，请重试")
                    return False
                    
            except:
                pass
            time.sleep(2)
            
        print("验证超时，请重试")
        return False
        
    except Exception as e:
        print(f"处理人机验证时出错: {str(e)}")
        return False

def simulate_human_input(element, text):
    """模拟人类输入文本"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def simulate_mouse_movement(driver, element):
    """模拟真实的鼠标移动"""
    try:
        action = ActionChains(driver)
    
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        
        viewport_width = driver.execute_script('return window.innerWidth;')
        viewport_height = driver.execute_script('return window.innerHeight;')
        
        element_rect = element.rect
        element_x = element_rect['x'] + element_rect['width'] // 2
        element_y = element_rect['y'] + element_rect['height'] // 2
        
        start_x = viewport_width // 2
        start_y = viewport_height // 2
        
        points = []
        num_points = random.randint(2, 4)
        for _ in range(num_points):
            x = start_x + (element_x - start_x) * random.random()
            y = start_y + (element_y - start_y) * random.random()
            x = max(0, min(x, viewport_width))
            y = max(0, min(y, viewport_height))
            points.append((int(x), int(y)))
        
        action.move_by_offset(-2000, -2000).perform()  
        action.move_by_offset(start_x, start_y).perform()
        current_x, current_y = start_x, start_y
        for x, y in points:
            offset_x = x - current_x
            offset_y = y - current_y
            action.move_by_offset(offset_x, offset_y)
            action.pause(random.uniform(0.1, 0.2))
            current_x, current_y = x, y   
        action.move_to_element(element)
        action.pause(random.uniform(0.3, 0.5))
        action.perform()
        
        time.sleep(random.uniform(0.2, 0.5))
        
    except Exception as e:
        print(f"鼠标移动失败，使用直接点击: {str(e)}")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)

def add_random_scroll(driver):
    """添加随机滚动行为"""
    scroll_amount = random.randint(50, 200)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(random.uniform(0.5, 1))
    driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
    time.sleep(random.uniform(0.3, 0.7))

def create_stealth_js():
    """创建 stealth.min.js 文件"""
    js_content = '''
    (function(){
    const elude=function(){const t=window.chrome;const e=window.navigator;const n=function(){};const o=function(){return true};const r=function(){return false};const i=function(){return""};const c=function(){return[]};const a=function(){return{}};const f=function(){return 2};const l=function(){return 24};const u=function(){return 8};const s=function(){return 10};const d=function(){return 0};const w=function(){return 1};const g=function(){return"zh-CN"};const p=function(){return["zh-CN","zh"]};const m=function(){return"Asia/Shanghai"};const h=function(){return"Win32"};const v=function(){return"Windows"};const y=function(){return"Windows NT 10.0; Win64; x64"};const b=function(){return"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"};const C=function(){return undefined};const x=function(){return true};const E=function(){return false};const N=function(){return""};const S=function(){return[]};const T=function(){return{}};const k=function(){return 2};const L=function(){return 24};const M=function(){return 8};const O=function(){return 10};const P=function(){return 0};const R=function(){return 1};Object.defineProperty(e,"languages",{get:p});Object.defineProperty(e,"plugins",{get:c});Object.defineProperty(e,"webdriver",{get:C});Object.defineProperty(e,"platform",{get:h});Object.defineProperty(e,"userAgent",{get:b});Object.defineProperty(e,"appVersion",{get:y});Object.defineProperty(window,"chrome",{get:function(){return{app:{isInstalled:false},runtime:{}}}});Object.defineProperty(window,"navigator",{get:function(){return e}});};if(document.readyState!=="loading"){elude()}else{document.addEventListener("DOMContentLoaded",function(){elude()})}})();
    '''
    
    with open('stealth.min.js', 'w') as f:
        f.write(js_content)

def click_button_with_retry(driver, selector, selector_type=By.CSS_SELECTOR, max_retries=3):
    """尝试点击按钮，带重试机制"""
    for i in range(max_retries):
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((selector_type, selector))
            )
            action = ActionChains(driver)
            action.move_to_element(button)
            action.pause(random.uniform(0.3, 0.7))
            action.perform()
            time.sleep(random.uniform(0.5, 1))
            button.click()
            return True
        except Exception as e:
            print(f"点击按钮失败 (尝试 {i+1}/{max_retries}): {str(e)}")
            time.sleep(1)
    return False

def handle_turnstile(driver):
    """处理 Turnstile 人机验证"""
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='challenges.cloudflare.com']"))
        )
        driver.switch_to.frame(iframe)
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox'], .turnstile-checkbox"))
        )
        action = ActionChains(driver)
        action.move_to_element(checkbox)
        action.pause(random.uniform(0.3, 0.7))
        action.click()
        action.perform()
        driver.switch_to.default_content()
        time.sleep(3)
        return True
    except Exception as e:
        print(f"处理验证失败: {str(e)}")
        driver.switch_to.default_content()
        return False

def get_verification_code(email):
    """从2925.com获取验证码"""
    print("正在启动新的浏览器窗口...")
    driver2 = None
    try:
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        driver2 = uc.Chrome(
            options=options,
            use_subprocess=True,
            driver_executable_path=None,
            browser_executable_path=None,
            suppress_welcome=True
        )
        print("访问邮箱登录页面...")
        driver2.get("https://www.2925.com/#/")
        time.sleep(5)
        print("登录邮箱...")
        try:
            username_input = WebDriverWait(driver2, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".el-input__inner[type='text']"))
            )
            simulate_human_input(username_input, "ygnzxydlz")
            time.sleep(1)
            
            password_input = driver2.find_element(By.CSS_SELECTOR, ".el-input__inner[type='password']")
            simulate_human_input(password_input, "Y123+zx456")
            time.sleep(1)
            
            login_button = WebDriverWait(driver2, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-button--primary"))
            )
            driver2.execute_script("arguments[0].click();", login_button)
            print("\n请手动查看验证码...")    
        except Exception as e:
            print(f"邮箱操作失败: {str(e)}")
            if driver2:
                try:
                    driver2.save_screenshot("email_error.png")
                    print("错误截图已保存到 email_error.png")
                except:
                    pass
            raise
    except Exception as e:
        print(f"获取验证码失败: {str(e)}")
        if driver2:
            driver2.quit()
        return None

def kill_cursor_process():
    """关闭所有 Cursor 进程"""
    print("正在关闭 Cursor...")
    for proc in psutil.process_iter(['name']):
        try:
            if 'cursor' in proc.info['name'].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    time.sleep(2)  # 等待进程完全关闭

def start_cursor():
    """启动 Cursor"""
    print("正在启动 Cursor...")
    cursor_path = os.path.join(os.getenv("LOCALAPPDATA"), "Programs", "Cursor", "Cursor.exe")
    if os.path.exists(cursor_path):
        subprocess.Popen(cursor_path)
        return True
    return False

def generate_random_string(length=6):
    """生成随机字符串（字母和数字）"""
    chars = string.ascii_lowercase + string.digits  # 小写字母和数字
    # 确保长度不超过6
    actual_length = min(length, 6)
    return ''.join(random.choice(chars) for _ in range(actual_length))

def generate_random_name(min_length=3, max_length=5):
    """生成随机名字（仅字母）"""
    length = random.randint(min_length, max_length)
    # 首字母大写，其余小写
    name = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    return name.capitalize()

def register_account(user_input, first_name, last_name):
    """注册 Cursor 账号"""
    # 生成随机字符串作为邮箱前缀
    email_prefix = generate_random_string()
    email = f"ygnzxydlz{email_prefix}@2925.com"
    password = generate_password()
    
    print(f"使用邮箱: {email}")
    
    # 初始化 undetected_chromedriver
    print("正在启动浏览器...")
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    
    # 添加更多选项来提高稳定性
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-infobars')
    
    try:
        # 不指定特定版本，让它自动匹配当前 Chrome 版本
        driver = uc.Chrome(
            options=options,
            use_subprocess=True,  # 使用子进程来提高稳定性
            driver_executable_path=None,  # 自动下载匹配的驱动
            browser_executable_path=None,  # 自动查找浏览器路径
            suppress_welcome=True  # 禁用欢迎页面
        )
        
        # 注入 stealth.js
        if os.path.exists('stealth.min.js'):
            with open('stealth.min.js', 'r') as f:
                js = f.read()
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': js
                })
        
        # 设置页面加载超时
        driver.set_page_load_timeout(30)
        
        try:
            # 访问登录页面
            print("正在访问登录页面...")
            driver.get("https://authenticator.cursor.sh/?client_id=client_01GS6W3C96KW4WRS6Z93JCE2RJ&redirect_uri=https%3A%2F%2Fcursor.com%2Fapi%2Fauth%2Fcallback&response_type=code&state=%257B%2522returnTo%2522%253A%2522%252Fsettings%2522%257D")
            time.sleep(5)
            
            # 点击 Sign up 链接
            print("正在查找注册链接...")
            signup_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.BrandedLink[href*='sign-up']"))
            )
            signup_link.click()
            time.sleep(3)
            
            # 在浏览器中填写表单
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
            print("\n正在点击 Continue 按钮...")
            continue_button = driver.find_element(By.CSS_SELECTOR, "button[name='intent'][value='sign-up']")
            continue_button.click()
            
            # 等待人工完成验证
            print("\n请完成人机验证...")
            print("完成验证后请按回车键继续...")
            input()
            
            # 等待密码输入框出现
            print("正在填写密码...")
            try:
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                simulate_human_input(password_input, password)
            except:
                print("未找到密码输入框，请确认是否已完成验证")
                print("完成后按回车键继续...")
                input()
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                simulate_human_input(password_input, password)
            
            # 点击 Next 按钮
            next_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            next_button.click()
            
            # 等待人工完成第二次验证
            print("\n请完成第二次人机验证...")
            print("完成验证后请按回车键继续...")
            input()
            get_verification_code(email)
            # 等待最后一次人机验证
            print("\n请完成最后一次人机验证...")
            print("完成验证后请按回车键继续...")
            input()
            
            # 等待注册完成
            time.sleep(3)
            
            # 保存账号信息
            account_info = {
                "email": email,
                "password": password
            }
            
            with open("cursor_account.json", "w") as f:
                json.dump(account_info, f, indent=2)          
            print("账号信息已保存到 cursor_account.json")
            cursor_config = {
                "email": email,
                "password": password
            }
            
            config_path = os.path.join(os.getenv("APPDATA"), "Cursor", "config.json")
            if os.path.exists(config_path):
                os.remove(config_path)
            
            with open(config_path, "w") as f:
                json.dump(cursor_config, f, indent=2)
            
            print("Cursor 配置已更新")           
            print("\n正在重启 Cursor...")
            kill_cursor_process()
            
            # 启动新的 Cursor 实例
            if start_cursor():
                print("Cursor 已使用新账号重新启动")
            else:
                print("无法找到 Cursor 程序，请手动启动")
            
            print("\n注册完成！按回车键关闭浏览器...")
            input()
        except Exception as e:
            print(f"操作过程中出错: {str(e)}")
            if driver:
                try:
                    driver.save_screenshot("error_screenshot.png")
                    print("错误截图已保存到 error_screenshot.png")
                except:
                    pass
            raise
        finally:
            if driver:
                driver.quit()
                
    except Exception as e:
        print(f"浏览器初始化失败: {str(e)}")
        raise
        
    return email, password

def main():
    # 确保 stealth.min.js 存在
    if not os.path.exists('stealth.min.js'):
        create_stealth_js()
    # 生成随机名字
    first_name = generate_random_name()
    last_name = generate_random_name()
    print(f"使用名字: {first_name} {last_name}")
    try:
        # 注册账号
        email, password = register_account(None, first_name, last_name)
        print(f"\n注册完成！")
        print(f"邮箱: {email}")
        print(f"密码: {password}")
        print("请重启 Cursor 以应用新的登录信息")
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 