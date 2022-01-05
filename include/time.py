import datetime
import sys

"""
调用方法：
days = get_whole_year(2021)
for day in days:
   # today = datetime.date.today()
   day = datetime.datetime.strptime(day,"%Y-%m-%d").date()
   yestday = day + datetime.timedelta(days=-1) #days参数1是明天，-1即是昨天。
   today = day + datetime.timedelta(days=1) #今天

   # print(str(day)+" 的昨天:"+ str(yestday)+ " 它的明天是："+ str(today))
   print(str(day) + " 它的明天是：" + str(today))
"""   

# 得到一年中所有的日期
def get_whole_year(year=2022):
    begin = datetime.date(year, 1, 1)
    now = begin
    end = datetime.date(year, 5, 31) # 到5月31日
    delta = datetime.timedelta(days=1)
    days = []
    while now <= end:
        days.append(now.strftime("%Y-%m-%d"))
        now += delta
    return days

