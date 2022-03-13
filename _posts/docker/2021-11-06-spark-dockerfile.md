---
layout: post
title: "도커파일 - 스파크 마스터/워커 이미지 및 컴포즈로 클러스터 구성하기"
tags: docker
---

스파크 스트리밍 실습을 위해서 컨테이너 기반 스파크 클러스터를 설치한다.

먼저 아래는 스파크가 설치된 이미지로, 빌드한 뒤 마스터와 워커를 위한 베이스 이미지로써 사용한다.

```Dockerfile
From ubuntu:20.04

ENV SPARK_HOME=/opt/spark-3.0.3-bin-hadoop2.7
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre
ENV PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH

RUN apt-get update
RUN apt-get install -y openjdk-8-jdk
RUN apt-get install -y wget
RUN apt-get install -y python3
RUN wget https://archive.apache.org/dist/spark/spark-3.0.3/spark-3.0.3-bin-hadoop2.7.tgz && tar -xzf spark*.tgz && rm spark*.tgz && mv spark* /opt
RUN mkdir /data

CMD ["/bin/bash"]
```

아래는 마스터 역할을 하는 이미지로, 실습에서 사용할 주피터노트북과 netcat, tweepy 패키지 등을 추가적으로 설치해준다.

start-master.sh 라는 스크립트는 마스터의 호스트명 환경변수 지정 및 각종 스파크의 configuration 을 처리한 뒤 실행파일을 통해 마스터 대몬을 실행시키는데, 이를 CMD 구문에 넣음으로써 컨테이너가 생성될 때 기본적으로 실행되게끔 한다.

SPARK_MASTER_HOST에서는 hostname 의 결과를 받아가는데, 호스트명은 컴포즈 측에서 지정해준다.

```Dockerfile
FROM spark-base:3.0.3

COPY start-master.sh /

RUN apt-get install -y python3-pip
RUN pip3 install jupyter
RUN apt-get install -y netcat
RUN pip3 install tweepy
RUN mkdir /notebooks

EXPOSE 8080 7077 8888 4040

CMD ["/bin/bash", "/start-master.sh"]
```
```bash
export SPARK_MASTER_HOST=`hostname`
bash $SPARK_HOME/sbin/spark-config.sh
bash $SPARK_HOME/bin/load-spark-env.sh
$SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master
```

아래는 워커 역할을 하는 이미지로, 마스터와 같이 실행될 때 start-worker.sh 를 실행하며, 워커 대몬을 실행시킬 때 마스터 노드를 지정한다.

```Dockerfile
FROM spark-base:3.0.3
COPY start-worker.sh /
EXPOSE 8081
CMD ["/bin/bash", "/start-worker.sh"]
```
```bash
bash $SPARK_HOME/sbin/spark-config.sh
bash $SPARK_HOME/bin/load-spark-env.sh
$SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077
```

<br>

위의 도커파일로 만들어진 마스터와 워커들을 가지고 클러스터를 만드는 yml 파일이다.

우선 네트워크는 CIDR 16으로 10.5.0.0 으로 지정하였으며, 그 안에서 컨테이너마다 주소를 하나씩 지정해주었다.

마스터 역할의 컨테이너는 pyspark 드라이버로 주피터 노트북을 띄우기 때문에 8888 포트를 열어주며, 그 외에 스파크에서 실행되는 웹UI를 위한 포트들도 같이 열어준다.

노트북파일들을 위한 볼륨도 지정해준다.

환경변수에서는 파이스파크 드라이버를 주피터 노트북으로 지정해주고, 호스트에서도 접속이 가능하게끔 주피터노트북의 설정값을 오버라이드해서 실행시킨다.

워커 역할의 컨테이너는 크게 지정해줄 것이 없으며, 현재는 2개만 띄우지만 호스트의 자원 상황에 따라 워커 노드들을 더 추가할 수 있다.

```yml
version: "3.7"
services:
    spark-master:
        image: spark-master:3.0.3
        container_name: spark-master
        hostname: spark-master
        ports:
            - "8080:8080"
            - "7077:7077"
            - "8889:8888"
            - "4040:4040"
        volumes:
            - ./codes:/notebooks
            - ./data:/data
        networks:
            spark-network:
                ipv4_address: 10.5.0.2
        environment:
            - "PYSPARK_DRIVER_PYTHON=jupyter"
            - "PYSPARK_DRIVER_PYTHON_OPTS=notebook --ip=0.0.0.0 --allow-root --no-browser --NotebookApp.token='' --NotebookApp.password=''"
            - "SPARK_LOCAL_IP=spark-master"
            - "PYSPARK_PYTHON=python3"
    spark-worker-1:
        image: spark-worker:3.0.3
        container_name: spark-worker-1
        hostname: spark-worker-1
        depends_on:
            - spark-master
        ports:
            - "8081:8081"
        volumes:
            - ./data:/data
        env_file: ./worker/spark-worker.sh
        environment:
            - "SPARK_LOCAL_IP=spark-worker-1"
        networks: 
            spark-network:
                ipv4_address: 10.5.0.3
    spark-worker-2:
        image: spark-worker:3.0.3
        container_name: spark-worker-2
        hostname: spark-worker-2
        depends_on:
            - spark-master
        ports:
            - "8082:8081"
        volumes:
            - ./data:/data
        env_file: ./worker/spark-worker.sh
        environment:
            - "SPARK_LOCAL_IP=spark-worker-2"
        networks:
            spark-network:
                ipv4_address: 10.5.0.4
networks:
    spark-network:
        driver: bridge
        ipam:
            driver: default
            config:
                - subnet: 10.5.0.0/16
```

마스터 같은 경우는 하나밖에 없기 때문에 환경변수들을 environment 로 직접 지정하면 되지만, 워커는 여러노드를 생성하기 때문에 동일한 환경변수들을 모두 다 쓰기가 번거롭다.

따라서 워커의 경우 spark-worker.sh 라는 파일 아래에 환경변수들을 세팅해놓음으로써 env_file 로 일괄적으로 적용시킨다.

다만 각 노드의 SPARK_LOCAL_IP 는 다르게 가져가야하기 때문에 따로 지정해준다.

아래는 spark-worker.sh 로, 워커의 자원에 대한 환경변수값들이 들어있다.

```bash
SPARK_WORKER_CORES=1
SPARK_WORKER_MEMORY=1G
SPARK_DRIVER_MEMORY=128m
SPARK_EXECUTOR_MEMORY=256m
```