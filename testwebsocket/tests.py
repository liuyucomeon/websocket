import redis
from gevent import pywsgi, monkey
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
import redis.exceptions

monkey.patch_all()

# channel名格式
# 订单模块 order:门店id  eg. order:1

class WebSocketApp(object):
    def __call__(self, env, start_response):
        ws = env['wsgi.websocket']
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
        redis_cli = redis.Redis(connection_pool=pool)
        pubsub = redis_cli.pubsub()
        channel = ws.receive()
        pubsub.subscribe([channel])

        for item in pubsub.listen():
            if item['type'] == 'message':
                try:
                    ws.send(item['data'].decode())
                except WebSocketError:
                    # 取消redis订阅
                    pubsub.unsubscribe([channel])


server = pywsgi.WSGIServer(('', 8880), WebSocketApp(), handler_class=WebSocketHandler)
server.serve_forever()