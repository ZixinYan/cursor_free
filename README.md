# 脚本使用方法
- 注册2925无限邮，然后进入cursor_register.py脚本修改为自己的邮箱前缀
- 下载Google浏览器和cursor
- 执行注册脚本
```bash
python cursor_register.py
```
会自动执行注册命令，跟着程序的流程走一遍就可以了，密码和账号啥的都会自己生成和保存以及输入，就是其中人机验证部分没找到简单的方法，最后还是自己手动按一下比较靠谱儿，没通过的话就重新再认证一遍应该就可以了
- 找到cursor_account.json 里面就是注册成功的账户和密码，重新登陆就可以了，如果不能免费用的话就去运行一下[删除机器码](https://github.com/fly8888/cursor_machine_id)

# 未来可能添加
<p>现在脚本的问题就是对于Cloudflare的点击认证成功率不高，所以如果失败就转人工，可能这一点稍微有点儿麻烦<p>

# 项目思路
- ***网络请求***
  <p>采用curl_cffi库进行HRTTP请求，这个比requests处理反爬更加稳定，可以绕过一些User-Agent检测</p>
- ***自动化浏览器操作***
  <p>采用Selenium模拟用户交互，实现了点击按钮，输入文本，滚动页面等</p>
  <p>模拟人类真实的输入，制造输入停顿，鼠标移动等动作</p>
- ***账号密码生成***
  <p>采用随机数生成，比较自动</p>
- ***反爬***
  <p>采用undetected_chromedriver尝试规避网站的Selenium检测</p>
  <p>尝试JavaScript（stealth.min.js）隐藏webdriver进行反检测</p>
