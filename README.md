# Blog Crawler 博客爬虫

## 1. 项目简介

本项目是一个博客爬虫，用于爬取指定博客网站的文章内容。
本项目面相接口编程（ABC），通过实现接口的方式，可以实现对不同博客网站的爬取。

目前针对的博客网站是：[CSDN](https://www.csdn.net/)。基本功能流程如下：

1. 下载文章 HTML 页面
2. 下载文章图片
3. 上传图片到图床并替换文章中的图片链接
4. 生成一系列博客内容：标题、摘要、内容、版权声明、图片列表等
5. 上传博客内容到指定博客网站

## 2. 项目结构

```mermaid
sequenceDiagram
    participant URLProducer as URLProducer 子类
    participant URLScheduler as URLScheduler
    participant URLConsumer as URLConsumer 子类
    participant HTMLDownloader as HTMLDownloader
    participant ContentParser as ContentParser 子类
    participant ImageDownloader as ImageDownloader 子类
    participant Persistence as Persistence 子类

    %% URLProducer 发送 URL 到调度器
    URLProducer ->> URLScheduler: 不断发送 (url, type)
    URLScheduler -->> URLProducer: 确认接收

    %% URLConsumer 从调度器获取 URL
    URLConsumer ->> URLScheduler: 不断获取 (type 匹配的 url)
    URLScheduler -->> URLConsumer: 返回 url

    %% HTMLDownloader 下载网页内容
    URLConsumer ->> HTMLDownloader: 下载网页内容 (url)
    HTMLDownloader -->> URLConsumer: 返回 HTML 内容

    %% ContentParser 解析网页内容
    URLConsumer ->> ContentParser: 解析 HTML 内容

    %% ImageDownloader 下载图片
    ContentParser ->> ImageDownloader: 下载图片
    ImageDownloader -->> ContentParser: 返回图片字节流
    ContentParser ->> Persistence: 镜像存储图片
    Persistence -->> ContentParser: 返回镜像链接
    ContentParser ->> ContentParser: 替换网页内容中的图片链接
    ContentParser -->> URLConsumer: 返回解析结果 (标题、内容、图片链接等)

    %% 数据持久化
    URLConsumer ->> Persistence: 持久化博客数据 (标题、内容、封面、简介等)
    Persistence -->> URLConsumer: 数据持久化完成

    %% 流程结束
    URLConsumer -->> URLScheduler: 标记 URL 处理完成

```

## 3. 快速开始

```shell
conda create -n blog-crawler python=3.9
conda activate blog-crawler
pip install -r requirements.txt
```