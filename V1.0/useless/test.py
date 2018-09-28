# 获取新闻的标题，内容，时间和评论次数
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
import pandas


def getNewsdetial(newsurl):
    res = requests.get(newsurl)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    newsTitle = soup.select('.page-headerh1')[0].text.strip()
    nt = datetime.striptime(soup.select('.time-source')[0].contents[0].strip(), '%Y年%m月%d日%H:%M')
    newsTime = datetime.strftime(nt, '%Y-%m-%d %H:%M')
    newsArticle = getnewsArticle(soup.select('.article p'))
    newsAuthor = newsArticle[-1]
    return newsTitle, newsTime, newsArticle, newsAuthor


def getnewsArticle(news):
    newsArticle = []
    for p in news:
        newsArticle.append(p.text.strip())
    return newsArticle


# 获取评论数量

def getCommentCount(newsurl):
    m = re.search('doc-i(.+).shtml', newsurl)
    newsid = m.group(1)
    commenturl = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=gn&newsid=comos-{}&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20'
    comment = requests.get(commenturl.format(newsid))  # 将要修改的地方换成大括号，并用format将newsid放入大括号的位置
    jd = json.loads(comment.text.lstrip('var date='))
    return jd['result']['count']['total']


def getNewsLinkUrl():
    # 得到异步载入的新闻地址（即获得所有分页新闻地址）
    urlFormat = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||mtjj&level==1&&=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&callbake=newsloadercallback&_=1501000415111'
    url = []
    for i in range(1, 10):
        res = requests.get(urlFormat.format(i))
        jd = json.loads(res.text.lstrip('newsloadercallbake(').rstrip(');'))
        url.extend(getUrl(jd))
    # entend和append的区别
    return url


def getUrl(jd):
    # 获取每一分页的新闻地址
    url = []
    for i in jd['result']['date']:
        url.append(i['url'])
    return url


# 取得新闻时间，编辑，内容，标题，评论数量并整合在total_2中
def getNewsdDetail():
    title_all = []
    author_all = []
    commentCount_all = []
    article_all = []
    time_all = []
    url_all = getNewsLinkUrl()
    for url in url_all:
        title_all.append(getNewsdetial(url)[0])
        time_all.append(getNewsdetial(url)[1])
        article_all.append(getNewsdetial(url)[2])
        author_all.append(getNewsdetial(url)[3])
        commentCount_all.append(getCommentCount(url))
        total_2 = {'a_title': title_all, 'b_article': article_all, 'c_commentCount': commentCount_all,
                   'd_time': time_all, 'e_editor': author_all}
    return total_2


# （运行起始点）用pandas模块处理数据并转化为excel文档

df = pandas.DataFrame(getNewsdDetail())
df.to_excel('news2.xlsx')



