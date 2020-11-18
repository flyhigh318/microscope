from prometheus_client import Gauge, start_http_server

value = 404
# Gauge 的监控项，比如这里的 http_code，只能初始化一次，不然会报 “ValueError：Duplicated timeseries in CollectorRegistry” 
http_code = Gauge('http_code', 'HTTP CODE')
http_code.set(value)

# Gauge 用法：Gauge('监控项', '监控项说明', ['标签1', '标签2'])
# 一定要先在 Gauge 中初始化标签（比如，['标签1', '标签2']），才能在 labels 中使用（比如，labels(IP='10.0.0.1', HOSTNAME='foobar')）
cpu_usage = Gauge('cpu_usage', 'CPU USAGE', ['IP', 'HOSTNAME'])
start_http_server(5000)
while True:
    for value in range(2):
        cpu_usage.labels(IP='10.0.0.1', HOSTNAME='foobar').set(value)  # value 类型要跟 golang 中的 numeric 数值类型匹配ls