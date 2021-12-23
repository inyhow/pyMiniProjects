#  基于pyppeteer-0.2.6 利用cdp命令操作浏览器，运行无需chromedriver等驱动，会自动下载对应浏览器

import asyncio
import random
import os
import requests
from pyppeteer import launch
import logging
# 运行时，屏幕终端有很多不相关的日志打印
pyppeteer_level = logging.WARNING
logging.getLogger('pyppeteer').setLevel(pyppeteer_level)
logging.getLogger('websockets.protocol').setLevel(pyppeteer_level)
pyppeteer_logger = logging.getLogger('pyppeteer')
pyppeteer_logger.setLevel(logging.WARNING)

'''随机选择一个user-agent 与下面拼接'''
def randfakeUa():
    with open('fake_ua.txt', 'r') as f:
        fake_ua = [fua.strip() for fua in f.readlines()]
    fakeua = random.choice(fake_ua)
    return fakeua
#输入时，随机停顿时间，模拟人工输入
def input_time_random():
    return random.randint(160, 361)
#获取视窗宽，高
def screenSize():
    import ctypes
    #使用user32.dll GetSystemMetrics函数
    user32 = ctypes.windll.user32
    width =user32.GetSystemMetrics(0)
    height =user32.GetSystemMetrics(1)
    return width,height

def Proxies():
    # 这边利用了 快代理的私密代理 
    api_url = "http://dps.kdlapi.com/api/getdps/?orderid=963972275667063&num=1&pt=1&sep=1"

    proxy_url = requests.get(api_url).text
    proxyHost = proxy_url.split(':')[0]  # 得到参数
    proxyPort = proxy_url.split(':')[1]  # 得到参数
    print(proxyHost, proxyPort)


    # 代理隧道验证信息
    proxyServer = "http://" + proxyHost + ":" + proxyPort
    return proxyServer

def Authens():
    proxyUser = "350586972" #订单详情里面看
    proxyPass = "2awh1111" # 这边随便填的，需要自己去快代理订单详情中查看
    authen = {"username": proxyUser, "password": proxyPass}
    return authen

async def main():
    # 获取最大化窗口高宽值
    width,height= screenSize()

    browser = await launch(headless = True,
    autoclose = False,
    timeout = 1500,
    # 开发者工具
    devtools = False,
    dumpio = True,
    options = {'args':
            [
                '--no-sandbox',
                # 关闭提示条
                '--disable-infobars',
                f'--window-size={width},{height}',
                '--disable-extensions',
                '--hide-scrollbars',
                '--disable-bundled-ppapi-flash',
                '--mute-audio',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-features=TranslateUI',
                # 代理问题 https://blog.csdn.net/qq_40734108/article/details/118083047
                "--proxy-server=" + Proxies()
            ],
        }
    )
    # 无痕模式浏览器
    context = await browser.createIncognitoBrowserContext()
    # 添加headers
    headers = {
        'Accept-Encoding': 'gzip' #使用gzip压缩让数据传输更快
    }
    page = await context.newPage()
    await page.authenticate(Authens())
    await page.setExtraHTTPHeaders(headers)

    # 这边设置随机user-agent
    await page.setUserAgent(randfakeUa())
    await page.setViewport({'width': width, 'height': height})
    try:
        if await page.title() == '安全验证 - 知乎':
            print("呗限制了")
            await browser.close()
    except Exception as e:
        pass

    # https://www.zhihu.com/account/unhuman 获取异常访问页码url 就退出 重新导入代理ip
    await page.goto('https://www.zhihu.com/column/c_1407428091224936448')
    # 注入JS，绕过浏览器检测
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.evaluate('''() => {window.navigator.chrome = {runtime: {}, }; }''')
    await page.evaluate('''() =>{Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});}''')
    await page.evaluate('''() =>{Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')


    await asyncio.sleep(5)
    randstr = input_time_random()-60

    try:
        btn_ok = await page.querySelector('[id="Popover2-toggle"]')
    except Exception as e:
        print(e)
    finally:
        await page.type('#Popover2-toggle', '英特尔主板基础参数', {'delay': randstr})
        # 元素载入后执行搜索 “英特尔主板基础参数”
        await page.click('.SearchBar-searchButton', {'waitUntil': 'domcontentloaded'});
        await asyncio.sleep(2)
        # pyppeteer.errors.TimeoutError: Navigation Timeout Exceeded: 30000 ms exceeded.
        await page.goto(url='https://zhuanlan.zhihu.com/p/445177856')

        #await page.hover('#alreday-login > a')  # 移动到元素上

        # content= await page.content()
        await asyncio.sleep(2)
        element = await page.querySelector('.Modal-wrapper')
        if (element):
            print('登录窗口对象存在,关闭弹窗')
            await page.evaluate('''document.getElementsByClassName('Modal-wrapper')[0].remove(document.getElementsByClassName('Modal-wrapper'))''')
        await asyncio.sleep(2)

        content = await page.evaluate('''() => {
            window.scrollBy(0, document.body.scrollHeight)
        }''')
        await browser.close()

if __name__ == '__main__':
    count = 0
    while count <= 660:
          asyncio.get_event_loop().run_until_complete(main())

          count += 1
