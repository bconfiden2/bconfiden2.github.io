---
layout: post
title: "[도커] 우분투 컨테이너를 실행시키면 왜 그냥 종료되는가"
subtitle: ""
categories: system
tags: docker
---

도커 컨테이너는 일반적으로 가상머신과 비교되기 때문에, 컨테이너를 실행시킨다는 것을 어떤 기능을 갖는 서버를 실행시킨다는 것이라고 생각이 들기 마련이다.

따라서 ```docker run ubuntu:20.04```와 같이 우분투 이미지를 가지고 컨테이너를 실행시킨다면 가상머신을 하나 생성하듯이 우분투 서버가 하나 생성된다고 생각되지만, 해보면 막상 아무 일도 일어나지 않는다.

```bash
bconfiden2@dmlab-bear0:~$ sudo docker run ubuntu:20.04
bconfiden2@dmlab-bear0:~$ sudo docker ps -a
CONTAINER ID   IMAGE          COMMAND   CREATED         STATUS                     PORTS     NAMES
8692505d0910   ubuntu:20.04   "bash"    2 seconds ago   Exited (0) 2 seconds ago             gallant_jepsen
```

오히려 실행시켰던 컨테이너가 Exited로 종료 된 것을 볼 수 있는데, 이는 컨테이너에 대한 잘못된 이해에서 출발한다.

<br>

## 컨테이너

도커의 이미지는, 특정 프로그램(혹은 명령어)을 실행시킬 수 있는 환경에 대한 정보를 가지고 있어, 컨테이너로 만들어 올릴 때 그 환경에서 특정 명령어를 실행시킬 뿐이다.

ubuntu:20.04 를 docker run 으로 실행시켰을 때는, 우분투 환경에서 어떤 명령을 실행시킨 뒤, 해당 프로그램이 종료되어 컨테이너가 종료된 것이다.

즉 우분투 이미지는 기본적으로 자신이 갖고 있는 ```/bin/bash``` 를 실행시키는 이미지이기 때문에, 컨테이너는 배쉬를 실행시킨 뒤 배쉬가 종료되자 자연스럽게 종료된 것이다.

그렇기 때문에 우리가 컨테이너를 실행시킬 때 명령어를 인자로 넣어준다면, 컨테이너는 해당 명령어를 수행하고 그 결과를 HostOS 의 표준출력으로 찍어준 뒤 종료된다.

도커의 공식문서에서 나와있듯이, [COMMAND] 부분이 사용자가 넣어주는 명령어가 된다.

>> $ docker run [OPTIONS] IMAGE[:TAG] [COMMAND] [ARG...]

```bash
bconfiden2@dmlab-bear0:~$ sudo docker run ubuntu:20.04 echo Hello, World!
Hello, World!
```

이렇게 컨테이너를 실행시킬 때 명령어를 넣어주게 된다면, 이미지에 기본적으로 설정된 실행프로그램(default command)은 수행되지 않고, 사용자가 지정한 명령을 실행시킨다.

이 default command 는 Dockerfile 에서 CMD 로 설정하며, 실제로 도커 허브에서 [우분투 이미지를 만드는 Dockerfile](https://github.com/tianon/docker-brew-ubuntu-core/blob/49f002ba206e2cea2024aaa9f6f4ee4e9fb5c084/focal/Dockerfile) 을 확인해보면 CMD 에 bash 프로그램으로 지정된 것을 확인할 수 있다.

<br>

## 백그라운드 프로세스

컨테이너는 프로그램이 동작 중이면 종료되지 않기 때문에, 배포할 애플리케이션을 컨테이너로 실행시킨다면 컨테이너가 계속 서버로써 동작하게 할 수 있다.

예를 들어 도커 허브에 있는 httpd 이미지나, mysql 이미지 등을 실행시키면, 각 이미지에서 설정된 기본명령어(웹서버, 데이터베이스서버)가 실행되면서 프로그램이 종료되지 않아 컨테이너가 계속 살아있는 것을 볼 수 있다.

```bash
bconfiden2@dmlab-bear0:~$ sudo docker run -d -e MYSQL_ALLOW_EMPTY_PASSWORD=True mysql:5.7
0723f1f6eb3460e52fb7dce2d5e2af007eb5e6edf853aefd171e5caf274fc84f
bconfiden2@dmlab-bear0:~$ sudo docker ps -a
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS                      PORTS                 NAMES
0723f1f6eb34   mysql:5.7      "docker-entrypoint.s…"   5 seconds ago    Up 4 seconds                3306/tcp, 33060/tcp   jolly_lalande
```

일반적으로 서버에서 애플리케이션을 실행시킬 때는 백그라운드로 실행시킨다.

그러나, 컨테이너에서 애플리케이션을 백그라운드로 실행시킬 때는 컨테이너가 바로 종료되며 서버 역할을 할 수 없기 때문에, 컨테이너에서는 포어그라운드로 프로그램을 실행시켜야 한다.

도커로 스파크 클러스터를 구성할 때, 원래 하듯이 ```start-master.sh``` 등의 스크립트를 직접 실행시키면 이는 백그라운드로 켜지기 때문에 컨테이너가 종료된다.

대신 ```bin/spark-class```라는 실행파일에 옵션(Master/Worker 클래스 경로 등)을 줘서 직접 프로그램을 실행시킨다면 아래와 같이 포어그라운드로 마스터/워커 노드들이 동작하게 되어, 컨테이너가 종료되지 않고 정상적으로 클러스터를 올릴 수 있다.

아래는 -it 옵션을 주고 bash 를 실행시켜 컨테이너에 접속한 뒤 스파크를 실행시킨건데, 이렇게 포어그라운드로 돌아가게끔 마스터노드를 켜야 컨테이너가 죽지 않는다.

따라서 이 명령어를 master 이미지를 만들 Dockerfile 의 CMD 로 설정해놓는다면, 컨테이너가 실행되면서 마스터노드 역할을 하게 된다.
```bash
bconfiden2@dmlab-bear0:~$ sudo docker run -it --rm --name test spark-base:3.0.3 bash
root@886c58f9885d:/# $SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master
Using Spark's default log4j profile: org/apache/spark/log4j-defaults.properties
21/09/24 04:14:32 INFO Master: Started daemon with process name: 147@886c58f9885d
...
...
...
21/09/24 04:14:33 INFO MasterWebUI: Bound MasterWebUI to 0.0.0.0, and started at http://886c58f9885d:8080
21/09/24 04:14:33 INFO Master: I have been elected leader! New state: ALIVE

```
