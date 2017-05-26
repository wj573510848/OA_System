新浪微博爬虫建立要点记录：

1.redis去重
self.server_redis.getbit(self.key_processed_redis+str(int(int(weibo_ID)/4000000000)), int(weibo_ID)%4000000000)
self.server_redis.setbit(self.key_processed_redis+str(int(int(weibo_ID)/4000000000)), int(weibo_ID)%4000000000, 1)

2.sqlite储存数据

