# spider-fw
基于gevent 的异步爬虫框架,此项目处于实验阶段,仅供参考

# 技术选择
* Python2.7
* gevent

# 说明
1. 此框架去除了原框架中数据采集/数据库读写/文件读写的分布式执行部分(基于celery),以及爬虫调度管理模块(基于apscheduler)、爬虫监控部分,仅保留异步执行部分核心功能
2. 个人认为scrapy 和pyspider 对一些简单的爬虫场景来说比较重。而我希望实现一个在数据爬取、数据解析、数据存储 等各流程都能异步,并且方便控制并发的框架。
3. MySQL 读写如需异步需要使用pymysql, 文件读写需要pyaio

# 执行流程
1. 根据注册的流程函数初始化相同数量的gevent 线程池, 其大小为并发设置参数`pool_size`。同时初始化数个队列用于多个工作线程池之间的通信
2. 启动第一个工作线程池,并将结果发送给下一个工作线程池
3. 当所有线程池处于空闲状态,且队列中无任务存在,工作流结束。

# 目录
* command - 命令目录
* framework - 框架代码
* projects - 项目代码, 每个项目下的pages 文件夹存放数据采集相关代码, 而spiders 文件夹存放其他流程代码

# 运行
python command/run.py projects/demo/spiders/china_nba.py


