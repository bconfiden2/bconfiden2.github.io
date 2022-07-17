---
layout: post
title: "주키퍼 클러스터(3대) 세팅"
tags: homecls
---

아래와 같은 클러스터 환경에서 주키퍼를 설치하려고 한다.

| 역할 | 주소 | 호스트명 | 장비 | 운영체제 |
| :-: | :-: | :-: | :-: | :-: |
| 주키퍼 | 192.168.100.141 | h01 | 노트북 | Ubuntu Desktop 20.04 |
| 주키퍼 | 192.168.100.142 | h02 | 데스크탑 | Ubuntu Desktop 20.04 |
| 주키퍼 | 192.168.100.143 | h03 | 노트북 | Ubuntu Desktop 20.04 |

기본적으로 각 노드들 사이에는 서로의 ssh-key 가 인증되어 있고, 호스트명을 서로 식별할 수 있으며, jdk는 모두 1.8 버전으로 설치되어 있다.

<br>

## 실행파일 다운로드

[아카이브](https://archive.apache.org/dist/zookeeper/)에서 지금까지 릴리즈된 다양한 버전의 주키퍼를 다운 받을 수 있다.

나는 가장 최근 버전인 3.8.0 을 선택했으며, bin.tar.gz 를 선택하여 다운로드한 뒤 압축을 풀어주면 된다.

```bash
# 다운로드
bconfiden2@h01:/opt$ wget https://archive.apache.org/dist/zookeeper/zookeeper-3.8.0/apache-zookeeper-3.8.0-bin.tar.gz
--2022-07-11 15:21:42--  https://archive.apache.org/dist/zookeeper/zookeeper-3.8.0/apache-zookeeper-3.8.0-bin.tar.gz
Resolving archive.apache.org (archive.apache.org)... 138.201.131.134, 2a01:4f8:172:2ec5::2
Connecting to archive.apache.org (archive.apache.org)|138.201.131.134|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 13185104 (13M) [application/x-gzip]
Saving to: ‘apache-zookeeper-3.8.0-bin.tar.gz’

apache-zookeeper-3.8.0-bin.tar.gz    100%[=====================================================================>]  12.57M   234KB/s    in 56s

2022-07-11 15:22:39 (229 KB/s) - ‘apache-zookeeper-3.8.0-bin.tar.gz’ saved [13185104/13185104]

# 압축 풀기
bconfiden2@h01:/opt$ tar -xzvf apache-zookeeper-3.8.0-bin.tar.gz
# ...
# ...
# ...
bconfiden2@h01:/opt$ ls
apache-zookeeper-3.8.0-bin
```

하둡을 설치했을 때와 마찬가지로, 버전이 바뀔 때 마다 경로명이 바뀌는 이슈를 피하기 위해 zookeeper나 zkp 등과 같은 심볼릭 링크를 걸어놓는다.

/opt 디렉토리의 경우 기본적으로 일반 사용자의 쓰기 권한이 없지만, 편의를 위해 권한을 부여하고 진행하고 있다.

```bash
# 심볼릭 링크 생성!
bconfiden2@h01:/opt$ ln -s apache-zookeeper-3.8.0-bin zkp
bconfiden2@h01:/opt$ ls
apache-zookeeper-3.8.0-bin  zkp
```

<br>

## 주키퍼 설정

주키퍼의 환경설정 파일은, 주키퍼 홈(다운로드하고 압축을 푼 경로, ```/opt/zkp```) 아래에 있는 conf/zoo.cfg 파일이다.

기본적으로 이 파일은 존재하지 않는 대신 같은 경로 아래에 zoo_sample.cfg 를 제공하기 때문에, ```cp conf/zoo_sample.cfg conf/zoo.cfg```를 통해 생성한다.

```bash
bconfiden2@h01:/opt/zkp$ vi conf/zoo.cfg
# 기본적으로 세팅되어있음
tickTime=2000
initLimit=10
syncLimit=5
clientPort=2181

# 수정 필요
dataDir=/opt/.data/zookeeper

# 추가 선택
admin.serverPort=8081

# 추가 필요
server.1=h01:2888:3888
server.2=h02:2888:3888
server.3=h03:2888:3888
```

각 프로퍼티들에 대한 설명은 [공식문서](https://zookeeper.apache.org/doc/r3.8.0/zookeeperAdmin.html#sc_configuration)를 참조하자.

```수정 필요``` 항목은 인메모리 디비 스냅샷이나, 디비 업데이트에 대한 트랜잭션 로그들을 저장할 위치로, 꼭 opt 아래 경로가 아니더라도 사용자의 홈디렉토리 등 원하는 경로를 지정해주면 된다.

```추가 선택```은 이미 서버에서 8080 포트를 다른 서비스가 잡고 있는 경우에 추가하여 다른 포트의 값을 지정한다.

```추가 필요```에는 클러스터를 구성하는 각 서버들의 호스트명과, 주키퍼 내부적으로 리더 선출 등에서 활용하는 포트들을 세팅해준다.

맨 앞의 server.[X] 에 들어가는 숫자는 각 서버의 식별자로써 1부터 255 사이의 정수를 넣어야 하며, 각 서버마다 위에서 dataDir 로 세팅한 경로 아래에 myid 파일에 자신의 아이디 값을 추가해줘야 한다.

<br>

## 실행 및 확인

클러스터 내의 다른 노드들에도 설정파일과 실행파일들을 복사해준다(rsync).

```bash
bconfiden2@h01:/opt$ rsync -avh /opt/apache-zookeeper-3.8.0-bin h02:/opt
bconfiden2@h01:/opt$ rsync -avh /opt/apache-zookeeper-3.8.0-bin h03:/opt
```

마지막으로 주키퍼를 실행하기 전에 위에서 언급했던 myid 파일을 세팅해줘야 하는데, 각 서버마다 dataDir 로 세팅해준 경로 아래에 myid 파일을 생성하여 자기의 id로 세팅했던 값을 넣어준다.

```bash
# dataDir
bconfiden2@h01:/opt/zkp$ mkdir -p /opt/.data/zookeeper
bconfiden2@h01:/opt/zkp$ touch /opt/.data/zookeeper/myid
# h01 의 경우 server.1 로 세팅했기 때문에, 파일에  1  을 써주면 된다.
# 동일하게 h02 는 2, h03 은 3으로!
bconfiden2@h01:/opt/zkp$ echo [X] > /opt/.data/zookeeper/myid
```

위의 과정을 h02, h03 에서도 동일하게 진행함으로써, 각 서버의 /opt/.data/zookeeper/myid 파일에는 zoo.cfg 파일에서 설정해둔 id 값이 담기게 된다.

주키퍼 실행은 간단한데, bin/zkServer.sh 스크립트를 모든 서버(h01, h02, h03)에서 실행시켜준다.

```bash
# 8080 포트가 이미 사용중이었지만 admin.serverPort 값을 변경해주지 않았다면 실패한다.
# 관련된 로그는 주키퍼 홈 아래의 logs 디렉토리에서 확인할 수 있다.
bconfiden2@h01:/opt$ ./zkp/bin/zkServer.sh start
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: /opt/zkp/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
```

잘 실행되고 있는지 확인하기 위해서 jps를 출력하거나,
```bash
bconfiden2@h01:/opt$ jps
11249 ZooKeeperMain
11155 QuorumPeerMain
11784 Jps
```

status 를 찍어볼 수도 있다.
```bash
bconfiden2@h01:/opt/zkp$ ./bin/zkServer.sh status
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: /opt/zkp/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost. Client SSL: false.
Mode: follower
```

status 결과의 맨 아래를 보면 h01 서버는 현재 Follower인데, 아래처럼 h03 에서 확인했을 때 Leader 역할을 하고 있음을 알 수 있다.

```bash
bconfiden2@h03:/opt$ ./zkp/bin/zkServer.sh status
/usr/bin/java
ZooKeeper JMX enabled by default
Using config: /opt/zkp/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost. Client SSL: false.
Mode: leader
```