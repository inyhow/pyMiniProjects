from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import string
import zipfile
import time
import requests
import random

#生成代理插件
def create_proxyauth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """代理认证插件
    args:
        proxy_host (str): 你的代理地址或者域名（str类型）
        proxy_port (int): 代理端口号（int类型）
        # 用户名密码认证(私密代理/独享代理)
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径

    return str -> plugin_path
    """

    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path

def zhihu():
    # 随机选择一个user-agent 与下面拼接 每行一个user-agent 也可以用fakeUa 模块 
    with open('fake_ua.txt', 'r') as f:
        fake_ua = [fua.strip() for fua in f.readlines()]
    fakeua = random.choice(fake_ua)

    apiurl = "http://dps.kdlapi.com/api/getdps/?orderid=953952881615517&num=1&pt=1&sep=1"

    proxy_url = requests.get(apiurl).text
    proxy_ip = proxy_url.split(':')[0]  # 得到参数
    proxy_port = proxy_url.split(':')[1]  # 得到参数
    print(proxy_ip, proxy_port)

    proxy_username = "350586972"
    proxy_password = "2awhd5ee"
    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host=proxy_ip,  # 代理IP
        proxy_port=proxy_port,  # 端口号
        # 用户名密码(私密代理/独享代理)
        proxy_username=proxy_username,
        proxy_password=proxy_password
    )
    options = webdriver.ChromeOptions()
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disbale-gpu')
    options.add_extension(proxyauth_plugin_path)
    options.add_argument(f"user-agent={fakeua}")

    # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出
    desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略页面加载策略
    desired_capabilities["pageLoadStrategy"] = "none"  # none表示将browser操作方法改为非阻塞模式，在页面加载过程中也可以给browser发送指令，如获取url，pagesource等资源，get新的url等。

    chromedriver_path = "E:\Program Files\Python38\chromedriver.exe"
    driver = webdriver.Chrome(service = Service(chromedriver_path),desired_capabilities=desired_capabilities,options=options)
    driver.get("https://zhuanlan.zhihu.com/shuhangli")  # 到知乎机构栏目
    driver.maximize_window()
    time.sleep(2)
    # 知乎人机检测
    if driver.current_url.find("zhihu.com/account/unhuman") != -1:
        driver.get("https://zhuanlan.zhihu.com/p/346902012")
        driver.quit()
    time.sleep(2)

    # wait =WebDriverWait(driver, 10, poll_frequency=1).untill
    # 这么要判断是否有 id = Modal-wrapper 的层，否则会出错
    try:
        driver.find_element(By.CLASS_NAME, 'Modal-wrapper')
    except NoSuchElementException:
        pass
    finally:
        try:
            element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME,
                                                                                        "Modal-wrapper")))
            driver.execute_script("document.getElementsByClassName('Modal-wrapper')[0].remove(document.getElementsByClassName('Modal-wrapper'))", element)
        except TimeoutException:
            driver.refresh()
            driver.get("https://zhuanlan.zhihu.com/p/346902012")
            driver.quit()

    if driver.find_element(By.ID, "Popover2-toggle").is_displayed():
        searchbox = driver.find_element(By.ID, "Popover2-toggle")
        searchbox.send_keys("我主良缘")
        driver.find_element(By.CLASS_NAME, "SearchBar-searchButton").click()
    else:
        driver.get("https://zhuanlan.zhihu.com/p/346902012")
        driver.quit()

    driver.get("https://zhuanlan.zhihu.com/p/346902012")  # 到达指定要刷的文章页
    time.sleep(2)
    driver.set_page_load_timeout(10)
    # 这么要判断是否有 id = Modal-wrapper 的层，否则会出错
    try:
        driver.find_element(By.CLASS_NAME, 'Modal-wrapper')
    except NoSuchElementException:
        pass
    finally:
        time.sleep(2)
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "Modal-wrapper")))
        driver.execute_script("document.getElementsByClassName('Modal-wrapper')[0].remove(document.getElementsByClassName('Modal-wrapper'))", element)

    # 执行滚动操作 读完所有文章
    driver.execute_script("return window.scrollTo(0,12000)")
    time.sleep(2)
    driver.quit()

if __name__ == '__main__':
    count = 0
    while count <= 515:
        zhihu()
        count += 1
    print("阅读量刷完了")
