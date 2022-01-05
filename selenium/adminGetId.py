"""
模拟人工提取网站后台的信息，譬如生日 号码信息等
system : Win7
Python v3.8.10
selenium == 4.1.0
pymysql
"""
import os
import time
import pymysql
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# 从原来数据库表中获取 marry表的 userid，用来查询电话信息
def getUserid(driver):
    db=pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="root", db="marry", charset='utf8')
    cursor=db.cursor()
    cursor.execute("select userid from user where (phone is null or phone = '' limit 0,10000") # 限制查询10000条 ，改太大，chrome操作久了，不重置缓存容易挂
    data=cursor.fetchall()

    for row in data:
        userId=row[0]

        url="https://adm.demo.com/admin/members/userinfolist/userid/"+str(userId)+".html"
        driver.get(url)
        # 点击”显示号码“
        driver.find_element(By.ID,"check-phone").click()
    
        wait =WebDriverWait(driver,10,0.5)
        time.sleep(3)
        # 获取新增的弹出层 使用js获取号码信息
        phone=wait.until(lambda diver:driver.find_element(By.CLASS_NAME,"layui-layer-content").text)
        phone = phone.replace("手机号码为：", "")

        # 如果获取到电话不是纯数字，说明有问题，循环到是数值类型 退出
        while phone.isnumeric() == False:
            try:
               time.sleep(3)
               phone=wait.until(lambda diver:driver.find_element(By.CLASS_NAME,"layui-layer-content").text)
               phone = phone.replace("手机号码为：", "")
            except:
               driver.refresh()
        # 更新号码信息
        res = cursor.execute("update user set phone =%s where userid= %s",[phone,userId])
        if res:
            pass
        else:
            print('更新失败'+ str(userId))
        db.commit()


        url="https://adm.demo.com/admin/members/members.html"
        driver.get(url)
    db.close()

def grapUserId(url):
    option = ChromeOptions()
    option.add_experimental_option('useAutomationExtension', False)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])

    # 设置这两个参数就可以避免密码提示框的弹出
    prefs = {}
    prefs["credentials_enable_service"] =False
    prefs["profile.password_manager_enabled"]=False
    option.add_experimental_option("prefs", prefs)

    # 不自动关闭浏览器
    option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(executable_path="E:\Program Files\Python38\chromedriver.exe",options=option)
    
    # driver.execute_cdp_cmd("Network.enable", {})
    # driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "{Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1}"}})
    #cdp命令与上面一样效果，用来实时改变user-agent等信息 命令来源 https://chromedevtools.github.io/devtools-protocol/
    #driver.execute_cdp_cmd("Network.setUserAgentOverride", {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'})

    # 隐藏window.navigator.webdriver =true的问题，使用如下cdp命令后，打开窗口后，window.navigator.webdriver =false 反爬虫检测一种方法
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
    
    # 手动输入验证码登录
    verify_code = input("请填写验证码：")
    inputbox3 = driver.find_element(By.NAME,"verify")
    inputbox3.send_keys(verify_code)
    print("验证码填写完成..请等待")
    # 定位搜索按钮点击按钮,属性选择type
    driver.find_element(By.CSS_SELECTOR,"button[type=\"submit\"]").click()  
    time.sleep(3)
    
    #这边需要加个判断信息层 ，网络延迟有时会导致 出现无法捕获状态
    
    #先判断出response.code是否是200 再进入判断 messager-content 提示信息状态
    time.sleep(2)
    # 判断是否成功登陆
    current_title=driver.title.strip()
    if current_title == "网站管理系统后台":
        print('登陆成功...')
    else:
        print('登录失败...')

    driver.find_element(By.LINK_TEXT,'会员管理').click()
    time.sleep(3)
    #资讯列表点击，必须是最大化窗口，因为未最大化宽度的时候，右边缩进，是显示图标，由于根据link_text 会提示找不到元素
    driver.find_element(By.LINK_TEXT,'会员列表').click()
    time.sleep(3)

    print("正在搜索id")

    # 每次读取10000条数据出来，
    getUserid(driver)

    #间隔5-10
    #time.sleep(random.randint(5,11))
     #获取到数据库中，update对应id值 UPDATE  IGNORE `test_update` SET id = 1 where id = 2;

    #print('采集成功'+ userID)
    #driver.del_all_cookiee() #删除chromedriver.exe缓存，可以缓解内存溢出的情况
    #driver.quit()
def main():
    # 利用系统内置命令，强制结束对应chrome进程。
    os.system('taskkill /im chrome.exe /F')
    os.system('taskkill /im chromedriver.exe /F')
    # token 可以从页面代码中 通过正则提取出来
    grapUserId("https://adm.demo.com/admin/login?token=662e34d1c831deff7f663")
if __name__ == '__main__':
    main()
