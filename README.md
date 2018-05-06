TaobaoAnalysis
=========

练习NLP，分析淘宝评论的项目


项目结构
---------

为了方便，约定本项目中所有程序的当前目录都是项目根目录

```
.
├─analyze             分析用的主要程序
│  ├─dataprocess      准备训练数据
│  └─models           机器学习模型
├─crawler             爬虫
│  └─Taobao           Scrapy爬虫项目
│     └─spiders       Scrapy爬虫
├─data                所有程序数据
│  ├─crawler          爬虫数据，如要爬的商品ID
│  ├─models           机器学习模型数据
│  ├─plots            统计图
│  └─train            机器学习训练数据，如语料库、正负样本
└─utils               辅助模块，如读写数据库
```


依赖
---------

Python库见requirements.txt

另外需要安装[PhantomJS](http://phantomjs.org/)，并将其所在目录添加到环境变量Path
