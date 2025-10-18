import redis
import threading
import time

class RedisModel:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url)
        self._stop_ping = False
        self._ping_thread = None
        
        result = self.ping()
        if not result:
            raise Exception("Redis connection failed")
        print("PubSub Redis connection established successfully...")
        
        # Start automatic ping in background thread
        self._start_keepalive()

    def get_redis(self):
        return self.redis
    
    def ping(self):
        try:
            return self.redis.ping()
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False
    
    def publish(self, channel: str, message: str):
        self.redis.publish(channel, message)
    
    def _keepalive_worker(self):
        """Background thread that pings Redis every 30 seconds"""
        while not self._stop_ping:
            time.sleep(30)
            if not self._stop_ping:
                try:
                    self.ping()
                    print("Redis keepalive ping successful")
                except Exception as e:
                    print(f"Redis keepalive ping failed: {e}")
    
    def _start_keepalive(self):
        """Start the keepalive background thread"""
        if self._ping_thread is None or not self._ping_thread.is_alive():
            self._stop_ping = False
            self._ping_thread = threading.Thread(target=self._keepalive_worker, daemon=True)
            self._ping_thread.start()
            print("Redis keepalive thread started (ping every 30 seconds)")
    
    def close(self):
        """Stop keepalive and close Redis connection"""
        self._stop_ping = True
        if self._ping_thread and self._ping_thread.is_alive():
            self._ping_thread.join(timeout=2)
        if self.redis:
            self.redis.close()
        print("Redis connection closed")