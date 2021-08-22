---
layout: post
title: "[Kafka] 카프카를 단일 브로커로 설치하고 CLI 명령어 실습해보기"
subtitle: ""
categories: bigdata
tags: kafka
---

Ubuntu 20.04 에다가 카프카를 설치해서 CLI 환경에서 토픽을 생성해보고 메시지 프로듀싱과 컨슘 등의 실습을 해보자.

일반적으로 토픽 등을 관리하는 *카프카 클라이언트*라는 서버를 따로 두지만, 지금은 브로커 1대로 이루어진 카프카 클러스터를 목표로 하기 때문에 그냥 브로커가 클라이언트 역할도 같이 하도록 한다.

<br>

## 카프카 설치

[공식 홈페이지](https://kafka.apache.org/downloads)에 여러 버전들이 있는데, 자세한 사항은 각 버전마다 달려있는 *Release Notes*를 읽도록 하자.

지금은 현시점에서 가장 최신 버전인 ```2.8.0```을 설치한다. (Java 1.8 사용)

```bash
curl http://mirror.navercorp.com/apache/kafka/2.8.0/kafka-2.8.0-src.tgz --output kafka.tgz
tar -xzf kafka.tgz
cd kafka-2.8.0-src
./gradlew jar -PscalaVersion=2.13.5
```

[여기](https://downloads.apache.org/kafka/) 혹은 [여기](https://archive.apache.org/dist/kafka/)에서도 다운로드가 가능하다.

~~gradle 로 프로젝트를 빌드하는 과정에서 왜인지는 모르겠지만 java(1.8) 와 javac(11) 의 버전이 다르게 돼있어서 에러가 많이 났었다~~

<br>

## 브로커 설정

카프카가 사용하는 힙메모리의 크기는 기본적으로 256MB로 설정되어있는데, 카프카가 ```KAFK_HEAP_OPTS```라는 환경변수를 참조하므로 이 환경변수에 값을 세팅해주어 설정을 바꿔줄 수 있다.

```bash
export KAFKA_HEAP_OPTS="-Xmx2G -Xms2G"
# 노드가 갖고있는 자원에 맞게 할당해주기
```

이외에도 카프카는 다양한 환경변수들을 참조하는데, 어떤 환경변수들이 있는지 궁금하다면 ```bin/kafka-run-class.sh```에서 확인해볼 수 있다.

<br>

카프카를 실행시킬 때 ```config/``` 아래의 properties 파일들을 참조시키는데, 이 브로커를 외부에서 접속하기 위해서 기본적으로 ```server.properties```를 바꿔줘야 한다.
```bash
vi /config/server.properties

# 파일 내에서 아래 문장이 주석처리 되어 있을 텐데, 주석을 풀어준다.
listeners=PLAINTEXT://:9092
# 아래 문장 역시 주석을 풀어준 뒤, your.host.name 부분에 서버의 public IP 주소를 넣어준다.
advertised.listeners=PLAINTEXT://your.host.name:9092
```

<!-- 다른 옵션들도 많이 있는데, 궁금하면 [server.properties](~~)를 확인해보자. -->

외부와 9092 포트로 통신할 것이기 때문에, 방화벽에서 해당 포트를 열어줘야 통신이 가능하다.

```bash
sudo ufw enable
sudo ufw allow 9092
```

<br>

## 서버 실행

카프카를 실행시키기 전에, 카프카를 관리하는 주키퍼를 켜줘야 한다.

주키퍼 관련 설정 파일을 참조시켜서 데몬으로 동작하게 한 뒤, ```jps``` 를 통해 잘 켜졌는지 확인한다. 곧바로 카프카도 실행시킨다.
```bash
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
jps
# jps 결과에 QuorumPeerMain 이라는 프로세스가 떠있으면 완료
bin/kafka-server-start.sh -daemon config/server.properties
jps
# 마찬가지로, Kafka 라는 프로세스가 떠있으면 완료
```

이제 이 컴퓨터에 카프카가 돌아가고 있어서, 다른 컴퓨터에서 이 브로커에 메시지를 쓰거나 읽을 수 있다.

<br>

## 토픽 생성

토픽을 만들어놓아야 외부에서 해당 토픽으로 메시지를 쓸 수 있기 때문에, 테스트용 토픽을 CLI 명령어로 만들어 놓는다. 물론 설정파일에서 **토픽이 없다면 자동으로 생성해서 메시지를 쓰는 설정**을 할 수도 있다.

```bash
cd bin
# 토픽 생성, replication factor나 파티션 수 조절 가능, 토픽명은 test
bash kafka-topics.sh --bootstrap-server localhost:9092 --create --replication-factor 1 --partitions 3 --topic test
# 토픽 리스트 조회
bash kafka-topics.sh --zookeeper localhost:2181 --list
# 토픽 지우기
bash kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic test
```

카프카를 서빙하는 9092 포트에 명령을 내릴 수도 있고, 주키퍼를 서빙하는 2181 포트에 내릴 수도 있다.

<br>

## Console Producer, Consumer

지금까지는 카프카가 돌아가고 있는 브로커 서버에서 토픽을 만들었다.

브로커 서버에서, 9092 포트를 열어놓아서 외부에서 카프카에 접근할 수 있게 설정했었기 때문에, 다른 컴퓨터에서 메시지를 생산하고 가져가보자. ~~물론 브로커 서버에서 그냥 localhost 로 왔다리갔다리 해도 상관 없다~~

프로듀서/컨슈머로써 접속할 컴퓨터에도 카프카가 설치되어있어야 하므로 해당 컴퓨터에서 다시 **카프카 설치**를 따라간다.

```bash
# 터미널 1번 - Producer
# X.X.X.X 는 브로커 서버의 public IP address
bash bin/kafka-console-producer.sh --bootstrap-server X.X.X.X:9092 --topic test
```

콘솔 프로듀서를 실행시키면 ```>``` 표시가 뜰 텐데, 여기에다가 원하는 메시지를 마구 입력해준다. 입력을 종료하고 싶을 때는 ```Ctrl + C```.

여기서 생성한 메시지들이 브로커의 해당 토픽에 기록되는 중이므로, 컨슈머를 통해 기록된 메시지들을 컨슘해보자.

<br>

```bash
# 터미널 2번 - Consumer
bash bin/kafka-console-consumer.sh --bootstrap-server X.X.X.X:9092 --group testgroup --topic test
```

프로듀서 터미널에서 쳤던 메시지들을 전부 가져오는 걸 볼 수 있는데, **순서대로 가져오지 않는다**는 점을 확인할 수 있다.

토픽의 파티션을 3개로 나눴기 때문에, 각 파티션 안에서는 순서가 보장이 되지만 전체 파티션에서의 순서는 보장되지 않는다.

```--partition x``` 옵션을 추가할 경우는 x 파티션에서만 consume 해올 수도 있다.

<br>

앞서 콘솔 컨슈머를 실행시킬 때 컨슈머 그룹도 지정을 해주었는데, 또다른 새로운 컨슈머 그룹을 지정하면 처음부터 읽어 올 수 있다.

```bash
bash bin/kafka-console-consumer.sh --bootstrap-server X.X.X.X:9092 --group testgroup2 --from-beginning --topic test
```

이렇게 여러 컨슈머 그룹이 생성되었을 때, 아래처럼 컨슈머 그룹들에 대해서도 알아볼 수 있는 프로그램도 제공하고 있다.
```bash
# 컨슈머 그룹 조회
bash bin/kafka-consumer-groups.sh --bootstrap-server X.X.X.X:9092 --list
# 특정 컨슈머 그룹의 상태 확인
bash bin/kafka-consumer-groups.sh --bootstrap-server X.X.X.X:9092 --group testgroup --describe
# 컨슈머 그룹 제거
bash bin/kafka-consumer-groups.sh --bootstrap-server X.X.X.X:9092 --group testgroup --delete
```

```--describe```은 각 파티션별로 컨슈머들의 현재 오프셋과 그에 따른 LAG 등을 표시해준다.
