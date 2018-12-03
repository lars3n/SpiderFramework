#coding:utf-8
from framework.spider import *

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0",
}


@chains.wrap_all_method_ctx()
class NewsList(object):

    def __init__(self):
        self.url = 'http://china.nba.com/news/'

    def fetch(self):
        res = fetcher(
            self.url,
            {
                'headers': headers,
                'engine': 'requests',
            }
        )
        if res.is_success():
            return res.data

    def p_news(self, ctx):
        html = ctx.res
        with Parser(html).parse_dom() as soup:
            news_wrap = soup.find('div', class_='news-wrap')
            news_list = news_wrap.find_all('a')

            for news in news_list:
                cover = news.find('span', class_='img-wrapper').find('img')['data-original']
                title = news.find('span', class_='news-title').text.strip()
                publish_date = news.find('i').text.strip()

                url = news['href']

                yield chains.Ctx(
                    cover=cover,
                    title=title,
                    publish_date=publish_date,
                    url=url
                )


@chains.wrap_all_method_ctx()
class NewsDetail(object):

    def __init__(self):
        pass

    def fetch(self, ctx):
        url = ctx.url

        res = fetcher(
            url,
            {
                'headers': headers,
                'engine': 'requests',
            }
        )
        return res.data

    def p_news(self, ctx):
        html = ctx.res

        with Parser(html).parse_dom() as soup:
            content = soup.find('div', attrs={'id': 'Cnt-Main-Article-QQ'})

            content = str(content)[:200]

            return chains.Ctx(content=content)



