import redis

class RedisModel:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url)
        result = self.ping()
        if not result:
            raise Exception("Redis connection failed")
        print("PubSub Redis connection established successfully...")

    def get_redis(self):
        return self.redis
    
    def ping(self):
        return self.redis.ping()
    def publish(self, channel: str, message: str):
        self.redis.publish(channel, message)