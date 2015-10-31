# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
class BP:
	def __init__(self):
		self.pageIndex=1
		self.user_agent='Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
		self.headers={'User-Agent':self.user_agent}
		self.Posts=[]
		self.enable=False

	def getPage(self,pageIndex):
		try:
			#url = 'http://tieba.baidu.com/p/3980266757?pn=' + str(pageIndex)
			url = 'http://tieba.baidu.com/p/4012307015?pn=' + str(pageIndex)
			request=urllib2.Request(url)
			response=urllib2.urlopen(request)
			pageCode=response.read().decode('utf-8')
			return pageCode
		except urllib2.URLError,e:
			if hasattr(e,"reason"):
				print u"连接失败，错误原因:",e.reason
				return None

	def getPageItems(self,pageIndex):
		pageCode = self.getPage(pageIndex)
		if not pageCode:
			print "the end...."
			return None
		pattern=re.compile('post_index.*?:(.*?)}.*?<li class="d_name" data-field.*?data-field.*?target="_blank">(.*?)</a>.*?class="d_post_content j_d_post_content ">(.*?)<.*?</a></span><span class="tail-info">(.*?)</span>',re.S)
		items = re.findall(pattern,pageCode)
		#存储
		pagePosts = []
		#遍历正则表达式匹配的信息
		for item in items:
			#item[0]，item[1]是ID，item[2]是内容,item[3]是楼数
			pagePosts.append([item[0].strip(),item[1].strip(),item[2].strip(),item[3].strip()])
		return pagePosts

	def loadPage(self):
		if self.enable==True:
			if len(self.Posts)<2:
				pagePosts=self.getPageItems(self.pageIndex)
				if pagePosts:
					self.Posts.append(pagePosts)
					self.pageIndex+=1

	def getOnePost(self,pagePosts,page):
		for post in pagePosts:
			input=raw_input()
			self.loadPage()
			if input=="Q":
				self.enable=False  
				return
			print u"第%d页\t第%s\tID:%s\t\n%s" %(page,post[3],post[1],post[2])

	def start(self):
		print "loading,'Q'=quit"
		self.enable=True
		self.loadPage()
		nowPage=0
		while self.enable==True:
			if len(self.Posts)>0:
				pagePosts=self.Posts[0]
				nowPage+=1
				del self.Posts[0]
				self.getOnePost(pagePosts,nowPage)
			else:
				return None

s=BP()
s.start()