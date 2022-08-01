# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, queue, threading
import xlwt, os
from time import sleep
from tqdm import tqdm
from Download import Download

TotalNum = 0


class Article(object):
    title = ""
    article_link = ""
    authors = ""
    authors_link = ""
    abstract = ""

    def __init__(self):
        title = "New Paper"


def save_xls(sheet, paper):
    # 将数据按列存储入excel表格中
    global TotalNum
    sheet.write(TotalNum, 0, TotalNum)
    sheet.write(TotalNum, 1, paper.title)
    sheet.write(TotalNum, 2, paper.article_link)
    sheet.write(TotalNum, 3, paper.journal)
    sheet.write(TotalNum, 4, paper.authors_link)
    sheet.write(TotalNum, 5, paper.abstract)
    TotalNum += 1


head = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}  # 20210607更新，防止HTTP403错误

article_titles = []
article_links = []


def GetInfo(sheet, html):
    soup = BeautifulSoup(html, "html.parser")
    # print("\n"+soup)
    articles = soup.find_all(class_="gs_ri")
    for article in articles:
        paper = Article()
        try:
            title = article.find('h3')
            paper.title = title.text
            try:
                paper.article_link = title.a.get('href')
                article_titles.append(paper.title)
                article_links.append(paper.article_link)
            except:
                continue
            # print("\n"+paper.title)
            # print("\n"+paper.article_link)
            journal = article.find(class_="gs_a")
            paper.journal = journal.text
            # print("\n"+paper.authors)
            authors_addrs = journal.find_all('a')
            for authors_addr in authors_addrs:
                # print("\n"+authors_addr.get('href'))
                paper.authors_link = paper.authors_link + (authors_addr.get('href')) + "\n"

            abstract = article.find(class_="gs_rs")
            paper.abstract = abstract.text
            # print("\n"+paper.abstract)
        except:
            continue
        save_xls(sheet, paper)
    return


exitFlag = 0


class myThread(threading.Thread):
    def __init__(self, queueLock, queue):
        threading.Thread.__init__(self)
        self.queueLock = queueLock
        self.queue = queue

    def run(self):
        euDownload(self.queueLock, self.queue)


def euDownload(queueLock, queue):
    while not exitFlag:
        queueLock.acquire()
        if not queue.empty():
            url, path = queue.get()
            queueLock.release()
            try:
                Download.getPDF(url, path)
            except:
                continue
        else:
            queueLock.release()
        time.sleep(3)


if __name__ == '__main__':
    myxls = xlwt.Workbook()
    sheet1 = myxls.add_sheet(u'PaperInfo', True)
    column = ['序号', '文章题目', '文章链接', '期刊', '作者链接', '摘要']
    for i in range(0, len(column)):
        sheet1.write(TotalNum, i, column[i])
    TotalNum += 1

    keyword = input("keywords is?\n")
    # keyword = diabetes and conjunctiva and (microcirculation or microvasculature)
    # symfony and ((high myopia)or(long axis))
    # print("\n"+keyword)
    key = keyword.replace(" ", "+")
    info = ".\\Info\\" + keyword + "_PaperInfo.xls"
    ##检索
    print("\n" + "检索中……")
    if os.path.exists(info) == True:
        print("\n" + "PaperInfo already exists!")
    else:
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["pageLoadStrategy"] = "none"  # 此两行配置可以大大节省加载时间
        option = webdriver.ChromeOptions()
        chrome_dir = os.getcwd() + '/Chrome/'
        # print(chrome_dir)
        option.add_argument("--user-data-dir=" + chrome_dir)
        browser = webdriver.Chrome(options=option, executable_path='./chromedriver.exe')
        url = 'https://xs.dailyheadlines.cc/scholar?start=0&q=diabetes&hl=zh-CN&as_sdt=0,5'

        start = 0
        for i in tqdm(range(10)):
            url = 'https://xs.dailyheadlines.cc/scholar?start=' + str(start) + '&q=' + key + '&hl=zh-CN&as_sdt=0,5'
            start = start + 10
            browser.get(url)
            time.sleep(3)  ##睡眠3s,等待加载
            html = browser.page_source
            GetInfo(sheet1, html)
            myxls.save(info)
            sleep(0.5)
        browser.close()
    print("\n" + "检索完成")

    ##下载
    print("\n" + "下载中……")
    if len(article_titles) == 0:
        import xlrd

        data = xlrd.open_workbook(info)
        table = data.sheet_by_index(0)
        article_titles = table.col_values(1)[1:]
        article_links = table.col_values(2)[1:]
        # print(len(article_titles),len(article_links))
    # 保存路径
    dir = ".\\Articles\\" + keyword + "\\"
    if os.path.exists(dir) == False:
        os.mkdir(dir)
    # print (dir)
    queueLock = threading.Lock()
    article_num = len(article_titles)
    workQueue = queue.Queue(article_num)
    threads = []
    # 创建新线程
    for i in range(25):
        thread = myThread(queueLock, workQueue)
        thread.start()
        threads.append(thread)
    queueLock.acquire()
    for k in range(article_num):
        article_title = "{0}".format(article_titles[k].replace(':', ' ')).replace('.', '')
        path = dir + article_title + ".pdf"
        # print("\n"+path)
        workQueue.put((article_links[k], path))
    queueLock.release()
    # 等待队列清空
    while not workQueue.empty():
        pass
    # 通知线程是时候退出
    exitFlag = 1
    # 等待所有线程完成
    for t in threads:
        t.join()
    print("\n" + "下载完成")