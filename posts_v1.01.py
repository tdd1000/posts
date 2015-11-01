# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import string

class BP:
        def __init__(self):
                self.pageIndex=1
                self.titleIndex=0
                self.user_agent='Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
                self.headers={'User-Agent':self.user_agent}
                self.Posts=[]
                self.Titles=[]
                self.enable=False
                self.tiebaUrl=''
                self.pageUrl=''
        def getTitle(self,titleIndex):
                try:
                        url = self.tiebaUrl+'&pn='+str(titleIndex)
                        request=urllib2.Request(url)
                        response=urllib2.urlopen(request)
                        titleCode=response.read().decode('utf-8')
                        return titleCode
                except urllib2.URLError,e:
                        if hasattr(e,"reason"):
                                print u"fail:",e.reason
                                return None

        def getTitleItems(self,titleIndex):
                titleCode = self.getTitle(titleIndex)
                #print titleCode
                if not titleCode:
                        print "the end...."
                        return None
                items = re.findall(r'<a href="(.*?)" title=.*?>(.*?)</a></div>', titleCode)
                authors = re.findall(r'target="_blank">(.*?)</a><span class="icon_wrap  icon_wrap_theme1 frs_bright_icons ">', titleCode)
                titlePosts = []
                for i in range(len(items)):
                        item=items[i]
                        #item[0]是page，item[1]是主题,item[2]是作者
                        titlePosts.append([item[0].strip(),item[1].strip(),authors[i].strip()])
                return titlePosts
        
        def getPage(self,pageIndex):
                try:
                        #url = 'http://tieba.baidu.com/p/4134825978?pn=' + str(pageIndex)
                        url = self.pageUrl + '?pn=' + str(pageIndex)
                        request=urllib2.Request(url)
                        response=urllib2.urlopen(request)
                        pageCode=response.read().decode('utf-8')
                        return pageCode
                except urllib2.URLError,e:
                        if hasattr(e,"reason"):
                                print u"fail:",e.reason
                                return None

        def getPageInfo(self,pageIndex):
                pageCode = self.getPage(pageIndex)
                if not pageCode:
                        print "the end...."
                        return None
                pattern=re.compile('<li class="l_reply_num" style="margin-left:8px" ><span class="red" style="margin-right:3px">([0-9]*?)</span>.*?<span class="red">([0-9]*?)</span>.*?</li>',re.S)
                items = re.findall(pattern,pageCode)
                pageInfo = []
                print len(items)
                for item in items:
                        #item[0]回复数，item[1]总页数
                        pageInfo.append([item[0].strip(),item[1].strip()])
                return pageInfo
        
        def getPageItems(self,pageIndex):
                pageCode = self.getPage(pageIndex)
                if not pageCode:
                        print "the end...."
                        return None
                pattern=re.compile('<li class="d_name" data-field.*?data-field.*?target="_blank">(.*?)</a>.*?class="d_post_content j_d_post_content ">'+
                                   '(.*?)</div><br>.*?</a></span><span class="tail-info">(.*?)</span>',re.S)
                items = re.findall(pattern,pageCode)
                pagePosts = []
                for item in items:
                        #item[0]，item[1]是ID，item[2]是内容,item[3]是楼数
                        temp=item[1].strip()
                        temp=temp.replace('<br>','\n')
                        contexList=re.sub('<.*?>', '',temp)
                        contex=string.join(contexList,sep='')
                        pagePosts.append([item[0].strip(),contex,item[2].strip()])
                return pagePosts

        def loadPage(self):
                if self.enable==True:
                        if len(self.Posts)<2:
                                pagePosts=self.getPageItems(self.pageIndex)
                                if pagePosts:
                                        self.Posts.append(pagePosts)

        def loadTitle(self):
                if self.enable==True:
                        if len(self.Titles)<2:
                                titlePosts=self.getTitleItems(self.titleIndex)
                                if titlePosts:
                                        self.Titles.append(titlePosts)
                                        self.titleIndex+=50
                                        
        def getOneTitle(self,titlePosts):
                i=0
                print u"[Q]quit,otherwise show next 10 titles"
                input=raw_input()
                if input=="Q":
                        self.enable=False  
                        return
                while i<len(titlePosts):
                        if 10<len(titlePosts)-i:
                                k=10
                        else:
                                k=len(titlePosts)-i
                        title=[]
                        for j in range(k):
                                title.append(titlePosts[i])
                                i=i+1
                        while True:
                                print u"第%d页"%(self.titleIndex/50)
                                for j in range(k):
                                        print u"第%d个\t链接:%s\t主题:%s\t作者:%s\n" %(j+1,title[j][0],title[j][1],title[j][2])
                                print u"[Q]quit [C]choose titles [R]refresh otherwise,show next 10 titles"
                                input=raw_input()
                                if input=="Q":
                                        self.enable=False  
                                        return
                                if input=="R":
                                        self.titleIndex-=50
                                        return
                                if input!="C":
                                        break
                                print u"choose a title 1-"+str(k)
                                input=raw_input()
                                index=int(input)
                                if index>=1 and index<=k:
                                        self.pageUrl="http://tieba.baidu.com"+title[index-1][0]
                                        self.pageIndex=1
                                        pageInfo=self.getPageInfo(self.pageIndex)
                                        totalPageNum=int(pageInfo[1][1])
                                        totalReplyNum=int(pageInfo[1][0])
                                        print u"共%d个回复，共%d页\n" %(totalReplyNum,totalPageNum)
                                        print "choose a page 1-%d" %(totalPageNum)
                                        input=raw_input()
                                        self.pageIndex=int(input)-1
                                        self.enable=True
                                        while self.enable==True:
                                                self.pageIndex+=1
                                                if self.pageIndex>totalPageNum:
                                                        print "no page to show, press any key to continue"
                                                        input=raw_input()
                                                        break
                                                print u"loading 第%d页" %(self.pageIndex)
                                                self.loadPage()
                                                print "done"
                                                if len(self.Posts)>0:
                                                        PagePosts=self.Posts[0]
                                                        del self.Posts[0]
                                                        self.getOnePost(PagePosts,self.pageIndex)

                                                else:
                                                        break


        def getOnePost(self,pagePosts,page):
                for post in pagePosts:
                        input=raw_input()
                        #self.loadPage()
                        if input=="Q":
                                self.enable=False  
                                return
                        print u"第%d页\t第%s\tID:%s\t\n%s" %(page,post[2],post[0],post[1])

        def start(self):
                print "inpute name of tieba"
                kw = raw_input()
                self.tiebaUrl="http://tieba.baidu.com/f?ie=utf-8&kw="+kw+"&fr=search"
                self.enable=True
                while self.enable==True:
                        print u"loading 第%d页"%(self.titleIndex/50+1)
                        self.loadTitle()
                        print "Done"
                        if len(self.Titles)>0:
                                titlePosts=self.Titles[0]
                                del self.Titles[0]
                                self.getOneTitle(titlePosts)
                        else:
                                return None

s=BP()
s.start()
