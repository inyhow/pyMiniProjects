"""
获取chrome网络日志信息，并提取其中header 例子
system: win7 x64
python version 3.8.10
python module: selenium    3
               ChromeDriver 9.0.4577.63
"""
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json

def get_status_codes(logs):
    statuses = []
    for log in logs:
        if log['message']:
            d = json.loads(log['message'])
            if d['message'].get('method') == "Network.requestWillBeSentExtraInfo" or d['message'].get('method') == 'Network.responseReceived':
                #statuses.append(d['message']['params']['headers'])
                try:
                    if d['message']['params']['headers'][':path'] != '' and d['message']['params']['headers'][':authority']=='www.zhihu.com' :
                        test_str = d['message']['params']['headers'][':path']
                        if test_str.find('api/v4/search_v3',0) == 1:
                            print(json.dumps(d['message']['params']['headers']))

                except KeyError as e:
                        #print("不存在键名"+ str(e))
                        pass
    return statuses

chromedriver_path = "E:\Program Files\Python38\chromedriver.exe"
url = "https://www.zhihu.com/search?type=content&q=%E7%9F%A5%E4%B9%8E"
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
option = ChromeOptions()
option.add_experimental_option('useAutomationExtension', False)
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_argument('--disable-blink-features=AutomationControlled') #这句必须加，否则window.navigator.driver = true
option.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"')

browser = webdriver.Chrome(chromedriver_path, desired_capabilities=capabilities,options=option)

browser.get(url)
#获取网络日志

logs = browser.get_log('performance')
#print(json.dumps(logs))
get_status_codes(logs)
browser.quit()
