"""
采集后台的用户id对应信息 ： selenium/adminGetId.py selenium+requests优化版本
其实正常采集分析数据的时候，在requests无法直接采集的情况下，应该先可视化获取cookiee，然后结合requests这样的库去采集，毕竟可视化采集效率低
selenium先获取cookiee 同步给requests使用
Python v3.8.10
selenium 4.1.0
"""
import time
import json
import pymysql
import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# 获取用户id，chrome cookiee同步给requests使用

def getUserid(driver):
    db = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="root", db="marry", charset='utf8')
    cursor = db.cursor()
    cursor.execute("select userid from user where  phone = '' limit 0,100000")
    data = cursor.fetchall()
    # 获取chrome的cookies信息
    sel_cookies = driver.get_cookies()
    #print(sel_cookies)
    jar = requests.cookies.RequestsCookieJar()
    for i in sel_cookies:
        # 将selenium侧获取的完整cookies的每一个cookie名称和值传入RequestsCookieJar对象
        # domain和path为可选参数，主要是当出现同名不同作用域的cookie时，为了防止后面同名的cookie将前者覆盖而添加的
        jar.set(i['name'], i['value'], domain=i['domain'], path=i['path'])
    # 退出浏览器    
    driver.quit()
    session = requests.session()  # requests以session会话形式访问网站
    session.cookies.update(jar)  # 将配置好的RequestsCookieJar对象加入到requests形式的session会话中
    #print(session.cookies)
    url = 'https://adm.demo.com/admin/members/phone'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.35 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.35'
    }
    for row in data:
        userId = row[0]
        time.sleep(1)
        # 封装信息
        payload = {
            'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'userid': userId,
        }
        # 利用requests 模拟post 直接获取返回json信息
        req = requests.Request(method='POST', url=url, headers=headers, data=payload)
        rpe = session.send(session.prepare_request(req), timeout=10)
        #print(session.cookies)  # 此时的cookies同步为selenium侧的cookies
        #增加错误判断
        try:
            res = json.loads(rpe.content.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            print(rpe.content)
        except requests.exceptions.ProxyError:
            print("需要减少重试次数")
        # 如果返回status =0 那么可能信息是被标记为 已删除    
        if res["status"] == 0:
            #print(str(userId) + ":"+ '已删除')
            # 执行入库更新操作
            res = cursor.execute("update user set phone =%s where userid= %s", ['0', userId])
            if res:
                pass
            else:
                print('更新失败' + str(userId))
        else:
            # 如果phone['result'] =='查询失败' 就啥不弄，times.sleep(3)
            phone = res['result']
            print(str(userId) + ":"+ phone)
            time.sleep(3)
            res = cursor.execute("update user set phone =%s where userid= %s", [phone, userId])
            if res:
                pass
            else:
                print('更新失败' + str(userId))
        db.commit()
    db.close()


def grapUserId(url):
    option = ChromeOptions()
    option.add_experimental_option('useAutomationExtension', False)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_argument('--no-sandbox')
    # 设置这两个参数就可以避免密码提示框的弹出
    prefs = {}
    prefs["credentials_enable_service"] = False
    prefs["profile.password_manager_enabled"] = False
    option.add_experimental_option("prefs", prefs)

    # 不自动关闭浏览器
    option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(r"E:\Python38\chromedriver.exe"), options=option)
    # 隐藏window.navigator.webdriver =true的问题，使用如下cdp命令后，打开窗口后，window.navigator.webdriver =false
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
           Object.defineProperty(navigator, 'webdriver', {
             get: () => false
      })
     """
    })

    # 打开登陆页面
    driver.get(url)
    driver.maximize_window()

    userid = driver.find_element(By.NAME,'username')
    userid.send_keys("admin")

    passwd = driver.find_element(By.NAME,'password')
    passwd.send_keys("admin")

    verify_code = input("请填写验证码：")
    inputbox3 = driver.find_element(By.NAME,"verify")
    inputbox3.send_keys(verify_code)
    print("验证码填写完成..请等待")

    # 定位搜索按钮点击按钮,属性选择type
    driver.find_element(By.CSS_SELECTOR,"button[type=\"submit\"]").click()
    time.sleep(2)
    # 获取弹出层信息
    dialog_box = driver.find_element(By.CLASS_NAME,"messager-content")
    # 其实可以先判断出response.code是否是200 再进入判断 messager-content 提示信息状态
    time.sleep(1)

    # 判断是否成功登陆
    current_title = driver.title.strip()

    if current_title == "网站管理系统后台":
        print('登陆成功...')
    else:
        print('登录失败...')
        driver.quit()
        return False

    time.sleep(3)

    print("入库Number ")

    # 读取数据，并提取预先要取的json部分信息 并入库
    getUserid(driver)


def main():
    grapUserId("https://adm.demo.com/admin/login?token=662e34d1c831deff7f663")
if __name__ == '__main__':
    main()
