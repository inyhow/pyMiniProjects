from multiprocessing import Queue
import multiprocessing

def download(p,st): # 下载数据

    print(str(st)+'数据已经下载成功....')


def main():
    p1 = Queue()

    t1 = multiprocessing.Process(target=download,args=(p1,"123"))
    t2 = multiprocessing.Process(target=download,args=(p1,"456"))

    t1.start()
    t2.start()

if __name__ == '__main__':
    main()
