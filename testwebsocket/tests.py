import redis
from gevent import pywsgi, monkey
from geventwebsocket.handler import WebSocketHandler

monkey.patch_all()

# channel名格式
# 订单模块 order:门店id  eg. order:1

class WebSocketApp(object):
    def __call__(self, env, start_response):
        ws = env['wsgi.websocket']
        rc = redis.Redis(host='127.0.0.1')
        ps = rc.pubsub()
        channel = ws.receive()
        ps.subscribe([channel])
        for item in ps.listen():
            if item['type'] == 'message':
                ws.send(item['data'].decode())


server = pywsgi.WSGIServer(('', 8888), WebSocketApp(), handler_class=WebSocketHandler)
server.serve_forever()