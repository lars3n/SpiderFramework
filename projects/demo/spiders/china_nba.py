#coding:utf-8
from framework.spider import *
from projects.demo.pages import china_nba
import gevent


@chains.wrap_all_method_ctx(excludes=['main'])
class SchedulerLive(object):

    # 不使用并发的执行方式
    def main(self):
        sched = SchedulerLive()
        page = china_nba.NewsList()
        page2 = china_nba.NewsDetail()
    
        reses = page.p_news(page.fetch())
        for i in reses:
            try:
                sched.save(page2.p_news(page2.fetch(i)))
            except chains.StopExec:
                continue

    def main(self):
        self.chain = chain = chains.Chain()

        page = china_nba.NewsList()
        page2 = china_nba.NewsDetail()

        chain.call(
            page.fetch, pool_size=1, interval=1
        ).call(
            page.p_news, pool_size=10,
        ).call(
            page2.fetch, pool_size=1, interval=1
        ).call(
            page2.p_news, pool_size=10
        ).call(
            self.save, pool_size=10
        ).execute(debug=True, dump_memory_usage={
            # 'dump_heap': True,
        })

        # print(chain.stat)

    def save(self, ctx):
        print ctx.title
        print ctx.cover
        # print ctx.content
        # print ctx.publish_date

        # 模拟数据库耗时
        gevent.sleep(1)


def main():
    SchedulerLive().main()



