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

### 2.1 基础的生产者-调度器-消费者模型

```mermaid
sequenceDiagram
    participant Producer as Producer
    participant Scheduler as Scheduler
    participant Consumer as Consumer
    Producer ->> Scheduler: 注册生产者
    alt 还有更多 Task
        Producer ->> Scheduler: 发送 Task
        Scheduler -->> Producer: 确认接收
    else 已无更多 Task
        Producer ->> Producer: 停止
    end

    Consumer ->> Scheduler: 注册消费者
    alt 还有更多 Task
        Consumer ->> Scheduler: 获取 Task
        Scheduler -->> Consumer: 返回 url
        Consumer ->> Consumer: 处理 Task
    else Scheduler 已停止工作
        Consumer ->> Consumer: 停止
    end

    alt 持续监听
        Scheduler ->> Scheduler: 继续工作
    else 所有生产者都停止工作，并且所有的队列为空
        Scheduler ->> Scheduler: 停止工作
    end

```

### 2.2 项目实现的基于 TYPE-URL 的生产者-调度器-消费者模型

URLProducer、URLScheduler、URLConsumer 三个类分别继承自 Producer、Scheduler、Consumer
类，由父类完成基础的生产者-调度器-消费者模型的实现，完成自己的生命周期管理。

同时 URLProducer、URLScheduler、URLConsumer 等类定义了对应的接口，由子类实现具体的业务逻辑。

```mermaid
sequenceDiagram
    participant URLProducer as URLProducer 子类
    participant URLScheduler as URLScheduler
    participant URLConsumer as URLConsumer 子类
    participant HTMLDownloader as HTMLDownloader
    participant ContentParser as ContentParser 子类
    participant ImageDownloader as ImageDownloader 子类
    participant Persistence as Persistence 子类

    loop 不断生成 URL
        URLProducer ->> URLScheduler: 发送 (url, type)
        URLScheduler -->> URLProducer: 确认接收
    end

    loop 不断获取 URL
        URLConsumer ->> URLScheduler: 不断获取 (type 匹配的 url)
        URLScheduler -->> URLConsumer: 返回 url
        URLConsumer ->> HTMLDownloader: 下载网页内容 (url)
        HTMLDownloader -->> URLConsumer: 返回 HTML 内容
        URLConsumer ->> ContentParser: 解析 HTML 内容
        ContentParser ->> ImageDownloader: 下载图片
        ImageDownloader -->> ContentParser: 返回图片字节流
        ContentParser ->> Persistence: 镜像存储图片
        Persistence -->> ContentParser: 返回镜像链接
        ContentParser ->> ContentParser: 替换网页内容中的图片链接
        ContentParser -->> URLConsumer: 返回解析结果 (标题、内容、图片链接等)
        URLConsumer ->> Persistence: 持久化博客数据 (标题、内容、封面、简介等)
        Persistence -->> URLConsumer: 数据持久化完成
    end

```

## 3. 快速开始

### 3.1 配置环境

```shell
conda create -n blog-crawler python=3.9
conda activate blog-crawler
pip install -r requirements.txt
```

## 3.2 项目配置

1. 配置项：
   - 如果你使用的是 `OASystemPersistence` 服务，那么必须新建并配置 `./config/application-prod.json` 文件，参考
      `./config/application-dev.json` 的说明填写配置信息。
   - 如果使用的是 `LocalPersistence` 服务，暂时无需配置。
2. URL 链接文件：新建并填写 `./data/dataset/csdn_urls.txt` 文件，填写需要爬取的 URL 链接。每行一个 URL。

这里提供一个简单的获取 URL 的方式

如果你想博客搬家，那么打开你的主页，运行下面的脚本，获取当前页面的所有文章链接。将输出的链接粘贴到
`./data/dataset/csdn_urls.txt` 文件中。

```javascript
(() => {
    // 请替换为你的博客ID
    const id = 'qq_29997037'
    const hrefs = Array.from(document.querySelectorAll('a'))
        .map(element => element.getAttribute('href'))
        .filter(href => href && href.includes(`/${id}/article/details/`));
    console.log(hrefs.join('\n'));
})();
```

### 3.3 启动项目

```shell
python main.py
```

## 4. 开源协议

本项目基于 MIT 协议进行开源，详细内容请参阅 [LICENSE](LICENSE) 文件。

## 5. 免责声明

本脚本仅供学习、研究与个人使用，旨在帮助开发者理解和学习爬虫技术。请遵守相关法律法规，尊重网站的隐私政策和服务条款。

- 本脚本的所有代码仅供技术交流和学习之用，不得用于任何商业用途、恶意用途或违反任何第三方权利。
- 使用本脚本抓取网站内容时，用户需自行承担所有法律责任，确保不会对目标网站造成任何侵害。
- 如果脚本用于抓取的数据违反了目标网站的使用条款，请立即停止使用，并删除相关数据。

感谢您的理解与支持！