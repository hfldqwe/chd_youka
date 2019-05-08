# 优卡爬虫

## 后端部署
主要逻辑在文件`app.py`和`handler/main.py`中

定义了三个接口：
```
('/info',main.InfoHandler),
('/current',main.CurrentRecordHandler),
('/history',main.HistoryRecordHandler),
```
分别位用户信息，今日消费记录，历史消费记录

## 爬虫

### 爬取解析
主要逻辑在`async_spider/youka.py`中

### 验证码
暂时使用打码平台，在文件`async_spider/chaojiying.py`，本来是同步的，改写了一下

### cookies
使用redis存储cookies，主要在`hfldtools/cookies`中