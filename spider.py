#!/usr/bin/python
# coding=utf-8

import requests
import Queue
import os
import json


class Spider:
    """Spider 爬虫: 输入目标网站, 和感兴趣的内容,然后就开始爬!
        可以设定要搜索的信息, 然后保存到本地
    """

    url = ''
    searchword = ''
    req = ''
    q = Queue.Queue()
    limithead = "http://"
    limitheadssl = "https://"
    uselimit = True
    host = ''
    wordCount = 100000

    # def __init__(self):
    # self.setTarget()

    def setTarget(self):
        url = raw_input("目标网站:(比如: http://www.baidu.com) : ")
        canOut = raw_input("是否要爬出站外:[y/n] 默认是 n, 除非你的硬盘和内存够大,否则选n ")
        self.searchword = raw_input("请输入感兴趣的内容: ")
        self.wordCount = raw_input("当感兴趣的内容在同一页面出现多少,就下载页面,默认:10000次,相当于不储存: ")
        url = url.strip()
        if (url.startswith('http') == False):
            self.url = 'http://' + url
        else:
            self.url = url
        self.host = self.getHost(self.url)
        # if (len(str(self.url))==len(str("http://")+str(self.host)) or len(str(self.url))==len(str("https://")+str(self.host))):
        #     self.url = self.url + '/'
        print "起始的地址是: " + self.url
        print "主机的名称是: " + self.host
        print "要搜索的内容: " + self.searchword
        print "本地保存的等级: " + self.wordCount

        if canOut == 'y':
            self.uselimit = False;
        else:
            self.limithead = self.url
            self.limitheadssl = str(self.url).replace("http://", "https://", 1)
        self.pa(self.url)

    def pa(self, url):
        """返回true 就是继续爬, false 就是停"""
        print "开始爬: %s" % url
        self.req = requests.get(url)
        if (self.req.status_code == 200):
            print "成功连接到 %s" % url
            self.zhua(self.searchword)
            return True
        else:
            print "连接失败了~~~,退出!"
            return False

    def zhua(self, word):
        r = self.req.content
        word = str(word)

        if (r.find(word)):
            rc = r.count(word)
            file = open("res.txt", "a+")
            file.write(self.req.url + " " + str(rc) + "\n")
            print "在 %s 一共抓到 %d 次 << %s >>" % (str(self.req.url), rc, word)
            file.close();
            if (rc >= int(self.wordCount)):
                # print "将网页存储到: "+self.host+"目录下"
                if (os.path.isdir(str(self.host))) == False:
                    os.mkdir(str(self.host))
                fileurl = self.req.url
                fileurl = fileurl.replace('/', '_')
                fileurl = self.host + "/" + fileurl
                file = open(fileurl, "w")
                print "保存了文件: " + str(fileurl)
                file.write(r)
                file.close()
        lastpos = 0;
        while (True):
            pos = r.find("href=\"", lastpos)
            if (pos == -1):
                break;
            pos2 = r.find('"', pos + 6)
            nr = str(r[pos + 6:pos2])
            if nr.startswith("/"):
                # print "/ 开头的 nr : "+nr
                nr = "http://" + self.host + nr
                # print "获得的新 nr : "+nr

            self.q.put(nr)
            lastpos = pos2

        print "当前列队大小: " + str(self.q.qsize())

        while self.q.not_empty:
            newurl = self.q.get()
            newurl = str(newurl)
            if (newurl.startswith(str("http")) == False):
                print "无法解析的地址 : " + newurl
                continue
            if (self.host != self.getHost(newurl)):
                print "不让跑出站点哦!!: " + newurl
                continue
            if (self.isInQ(newurl) == True):
                print "重复的 url 跳过这个: " + newurl
                continue
            if self.pa(newurl) == False:
                print "无法访问 这个: " + newurl
                continue
            if self.q.empty():
                print "我靠!列队空了~~爬完了, 列队大小: %d" % self.q.qsize()
                break

    def isInQ(self, url):
        file = open("res.txt", "r")
        res = False
        while (True):
            s = file.readline()
            if (s == ''):
                break
            substr = s.split(" ", 1)
            if substr[0] == url:
                print substr[0] + "  <<----- 访问过了"
                res = True
                break
        file.close()
        return res

    def getHost(self, url):
        url = str(url)
        n = url.find("/", 8)
        startn = 7
        if (url.startswith("https://")):
            startn = startn + 1
        if (n == -1):
            url = url[startn:]
        else:
            url = url[startn:n]
        # print "获得 host 是: "+ url
        return url


spider = Spider();
spider.setTarget();
