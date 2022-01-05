# -*- coding: utf-8 -*-
# @Time    : 2021/7/28 07:48
# @Author  : inyhow
# @File    : get_agent.py
# @Desc    : 获取免费代理http ip数据

import requests
import random

from bs4 import BeautifulSoup
import ast

#代理资源采集 http://www.ip3366.net/free/?stype=1&page=2  代理资源或者数据量小的比较适合内存型数据库 redis 或mongo
def get_proxy_list(page):
    url="https://www.kuaidaili.com/free/inha/{page}" .format(page = page)
    pageno=0
    headinfo={
        'User-Agent': 'Mozilla/5.0 (Windows NT 7.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safaxri/537.36'
    }
    proxy_list=[]
    while pageno<10:
        pageno=pageno+1
        # 设置休眠时间 用来降低爬虫随机化采集间隔 这个站建议采集间隔时间久些
        sleep_time = random.randint(0,6) + random.random()
        rsp=requests.get(url+str(pageno),headers=headinfo)

        if rsp.text is None:
            return None

        soup=BeautifulSoup(rsp.text, features="lxml")
        tables=soup.find_all('table')

        data=[]
        for table in tables:
            if table.has_attr('class') and "table-bordered" in table['class']:
                rows=table.findAll('tr')
                items = []
                for row in rows:
                    cols=row.findAll('td')
                    if (len(cols)>5):
                        ip=cols[0].text
                        port=cols[1].text
                        type=cols[3].text.lower()
                        #pos = cols[4].text
                        #data = "{"+type+":"+ type +"://" +ip+":"+port+ "},"
                        proxyData = type +"://"+ip+":"+port
                        item = {
                            type: proxyData
                        }
                        req = requests.request('GET',url="https://dev.kdlapi.com/testproxy",proxies=item)
                        if req.status_code == 200:
                            items.append(item)
                            print(proxyData)


            #proxy_list.extend(data)


            #print(items)
    #df=pd.DataFrame(proxy_list)
    #df.columns=['IP', 'Port', 'Type','Pos']
    #df.columns = ['IP','Port','Type']


    #print(df)

#sleep_time = random.randint(0,2) + random.random() #设置休眠时间 用来降低爬虫随机化采集间隔世纪
for i in range(1,30):
    get_proxy_list(i)
