# encoding:utf-8
# -*- coding: utf-8 -*-
# @Time    : 2021/7/28 07:48
# @Author  : inyhow
# @File    : get_agent.py
# @Desc    : 获取免费代理ip数据
"""
requests是根据proxy http https 关键词来使用的，https资源对应https代理，因此须臾采集https代理
说明：https://docs.python-requests.org/zh_CN/latest/user/advanced.html#proxies
http代理采集：
https://abuyun.com
https://www.kuaidaili.com/free/inha/12/
https代理采集
http://ip.yqie.com/proxyhttps/index_1.htm
http://www.ip3366.net/?stype=1&page=1
https://ip.ihuan.me/ti.html
https://proxy.ip3366.net/free/?page=2
"""
import sys
import time

import requests
import random
import gzip
import base64
from bs4 import BeautifulSoup

#代理资源采集 http://www.ip3366.net/free/?stype=1&page=2  代理资源或者数据量小的比较适合内存型数据库 redis 或mongo
def get_proxy_list(page):
    url="http://ip.yqie.com/proxyhttps/index_{page}.htm" .format(page = page)
    pageno=0
    headinfo={
        'User-Agent': 'Mozilla/5.0 (Windows NT 7.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safaxri/537.36'
    }
    proxy_list=[]
    while pageno<10:
        pageno=pageno+1
        # 设置休眠时间 用来降低爬虫随机化采集间隔世纪
        sleep_time = random.randint(0,6) + random.random()
        time.sleep(sleep_time)

        rsp=requests.get(url,headers=headinfo)
        #解压代码 不然个别会出现乱码
        try:
            html = gzip.decompress(bytes(rsp.content)).decode("utf-8")
        except:
            html = rsp.content.decode("utf-8")
        #如果空 跳出
        if html is None:
            return None
        else:
           html = html.replace('<script>document.write(window.atob("', '').replace('"));</script>', '')

        soup=BeautifulSoup(html, features="lxml")
        tables=soup.find_all('table')

        for table in tables:
            if table.has_attr('id') and "GridViewOrder" in table['id']:
                rows=table.findAll('tr')
                items = []
                for row in rows:
                    cols=row.findAll('td')
                    if (len(cols)>5):
                        # base64解码ip
                        ip= base64.b64decode(cols[1].text).decode("utf-8")
                        # 端口号
                        port=cols[2].text
                        # 协议类型
                        type=cols[4].text.lower()

                        if type == "https":
                            proxyData = type +"://"+ip+":"+port
                            item = {
                                type: proxyData
                            }
                            #验证代理ip是否有效的
                            req = requests.request('GET',url="https://httpbin.org/get?show_env=1",proxies=item)
                            time.sleep(3)
                            if req.status_code == 200:
                                items.append(item)
                                #print(req.text)
                            # 代理ip写入到https.txt中
                            with open("https.txt","a+") as f:
                                f.write(proxyData)
    # 关闭文件
    f.close()

for i in range(1,2):
    get_proxy_list(i)
