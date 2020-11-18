## django + celery 分布式框架定时任务

### 架构

![avatar](./docs/images/django-celery1.jpg)


### django-apschedule

* 传统定时任务，类似java Quartz
* 不是分布式
* 具体例子看看updata应用里面的view

### django-celery(推荐使用这个)

* 分布式
* 每天处理百万消息实时框架
* web页面管理调度 django-celery-beat
* 监控 flower

### docker-compose demo 快速部署


* git clone 拉取代码
* cd /microscope/monitor
* docker build -t microscope:1.0.1
* docker-compose up -d
* 第一次启动期间，等待mysql、rabbimtq、redis服务就绪有点久，大概等5分钟左右服务完全启动起来, 可查看docker logs 日志。

#### 访问地址


| 服务 | url | 用户 | 密码 | 服务端口 |
| - | - | - | - | - |
| microscope-ui | http://localhost:8000 | admin | changeme | 8000 | 
| microscope-ui-cmd-metrics | http://localhost:8000/updata/metric/ | 无 | 无 | 8000 | 
| microscope-rabbitmq | http://localhost:15672 | rootcloud | celery | 15672/5672 |
| microscope-redis | 无 | root | celery | 6379 |
| microscope-mysql | 无 | root | rootcloud | 3306 |
| microscope-prom | http://localhost:9090 | 无 | 无| 9000 |
| celery-flower | http://localhost:5555 | 无 | 无 | 5555 |
| celery-beat  | 无 | 无 | 无 | 无 |
| celery-worker | 无 | 无 | 无 | 无 |






### 常规部署

* docker-compose 部署 rabbitmq， redis， mysql（root运行）
* docker 初始化 mysql 时，设置好格式

```
docker exec -it monitor_mysql mysql -uroot -p
# mysql 8.0 错误处理 ERROR 1045 (28000): Plugin caching_sha2_password could not be loaded
# alter user 'root'@'localhost' identified by 'rootcloud' password expire never;
# alter user 'root'@'localhost' identified with mysql_native_password BY 'rootcloud';
# alter user 'root'@'%' identified with mysql_native_password BY 'rootcloud';
# flush privileges;
```

* git clone 拉取代码
* 部署pipenv，进项目 pipenv --python 3.8.6
* 部署依赖 pipenv install
* 生成数据库

```
python manage.py makemigrations app
python manage.py migrate app
```


* 运行 celery worker

```
cd microscope/monitor
pipenv run nohup celery -A monitor worker -l info >>/tmp/celery.log 2>&1 &
```

* 运行 celery beat

```
cd microscope/monitor
pipenv run nohup celery -A monitor beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler >> /tmp/celery_beat.log 2>&1 &
```

* 运行 celery flower

```
cd microscope/monitor
pipenv run nohup celery flower -A monitor --broker=amqp://rootcloud:celery@localhost:5672// >> /tmp/celery_flower.log 2>&1 &
```

* 运行 django web

```
cd microscope/monitor
pipenv run python manage.py runserver
```

### 结果

* django login 
![avatar](./docs/images/login.jpg)
* django site 
![avatar](./docs/images/site.jpg)
* periodic task 
![avatar](./docs/images/periodic_task.jpg)
![avatar](./docs/images/periodic_task1.jpg)
* celery worker
![avatar](./docs/images/celery_worker.jpg)
* celery beat
![avatar](./docs/images/celery_beat.jpg)
* celery flower
![avatar](./docs/images/flower.jpg)