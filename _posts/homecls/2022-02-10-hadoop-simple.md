---
layout: post
title: "하둡 완전 분산 모드로 클러스터 설정하기"
tags: homecls hadoop
---

총 4대로 이루어져있는 라즈베리파이 클러스터에 하둡을 설치한다.

클러스터는 하나의 스위치를 통해 유선 랜으로 서로 연결되어있고, 네트워크대역은 192.168.100.0 이다.

노드들에는 수동으로 아이피를 101, 102, 103, 104 를 할당해줬고, 각각의 호스트명은 w01 ~ w04 로 지정하였다.

/etc/hosts 파일에는 모두 다른 노드들에 대한 정보가 추가되어 있다.

앞서 w01 의 홈디렉토리를 다른 노드들이 자신의 홈디렉토리로써 nfs 로 마운트해갔고 ssh key 를 등록해놓았기 때문에, 모든 노드들이 서로 자유롭게 왔다갔다 할 수 있다.

w01 를 마스터 역할을 맡기고(네임노드, 리소스매니저) 나머지 3개 노드들은 워커 역할(데이터노드, 노드매니저)로써 작동하게끔 하둡을 설정하려고 한다.

따로 디스크를 추가하지 않았기 때문에, 기본적으로 루트에 마운트된 파일시스템(sd카드) 아래에 디렉토리를 만들어서 hdfs 로 사용할 생각이다.

<br>

### 하둡 압축 파일 다운로드

아파치 재단에서 다양한 버젼의 설치 가능한 하둡 파일들과 레퍼런스를 제공하는데, 22년 2월 11일 기준으로는 [아카이브 링크](https://archive.apache.org/dist/hadoop/common/)에서 모든 버젼의 하둡 파일들을 받을 수 있다.

라즈베리파이는 arm 아키텍쳐 기반이기 때문에, aarch64 가 붙어있는 파일을 받아야 한다.

사용자의 홈디렉토리에 하둡을 설치해도 상관은 없지만, 일반적으로는 /opt 혹은 /usr/local 에 설치하기를 권장하므로 압축파일을 /opt 에 풀고, 소유권은 관리하고 실행시킬 계정으로 변경해준다.

```bash
$ sudo mv hadoop-X.X.X /opt
$ cd /opt
$ sudo chown -R hadoop:hadoop hadoop-X.X.X
```

하둡 버전이 바뀔 때 마다 환경변수 HADOOP_HOME 을 바꿔주긴 귀찮기 때문에, 아예 심볼릭 링크를 만들어놓은 뒤 홈을 링크로 지정해준다.

HADOOP_HOME 환경변수도 설정해주는데, 일반적으로는 /etc/profile.d 아래에 환경변수 관련된 값들을 설정해줄 수 있지만, 지금은 어차피 모든 노드가 같은 홈디렉토리를 공유하기 때문에 ~/.bashrc 아래에다가 지정해줬다.

```bash
$ sudo ln -s hadoop-X.X.X hadoop
$ vi .bashrc
...
export HADOOP_HOME=/opt/hadoop
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
```

하둡 홈 같은 경우에는 사실 사용자가 여러 스크립트를 실행하기 편하게 지정하는 것이다.

물론 하둡에서도 해당 환경변수를 사용하기도 하지만, 기본적으로 하둡 설정파일의 위치를 기반으로 자동으로 하둡 홈을 지정해서 실행하기 때문에 큰 문제는 없다.

만약 하둡 설정파일들($HADOOP_HOME/etc/hadoop)의 위치를 따로 /etc 아래에서 관리한다던지 할 경우에는 수동으로 반드시 지정해야 한다.

<br>

### 환경 변수 설정

여러가지 스크립트들을 호출함에 따라 실행되는 실행파일들은 여러 환경 변수들을 참조하여 사용한다.

스크립트에서 설정파일이나 실행파일들의 위치를 참조하게 해주는 변수들과, 여러 하둡 대몬과 태스크들이 실행될 때의 환경을 설정하는 변수들이 있다.

앞에서의 HADOOP_HOME 의 경우에도 이런 변수들 중 하나이지만 사용자가 시스템적으로 설정을 해놓는 것이다.

이런 변수들은 ```$HADOOP_HOME/etc/hadoop``` 아래에 hadoop-env.sh, yarn-env.sh, mapred-env.sh 등으로 존재한다.

hadoop-env.sh 를 보면 아파치에서 변수마다 주석으로 설명을 잘 해주고 있는데, 잘 읽어보면 사실상 가장 기초 세팅으로는 JAVA_HOME 만 설정해주면 된다.

그 외 많은 환경변수들은... 따로 알아보자.

<br>

### 프로퍼티 설정

hdfs, yarn, mapreduce 등을 위해 지정할 수 있는 속성값들은 너무너무너무 많고 다양한데, 설정파일들을 담은(env 들이 존재하는) 경로 아래에 core-site.xml, yarn-site.xml, hdfs-site.xml 등의 xml 파일들에서 설정 가능하다.

그러나 사실 기본 세팅을 위해서 지정해야 할 속성들은 아래처럼 그렇게 많지 않다.

core 에서는 디폴트 파일시스템을 hdfs로 설정해준다.

```bash
$ vi $HADOOP_HOME/etc/hadoop/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://w01:8020</value>
    </property>
</configuration>
```

hdfs 에서는 네임노드와 데이터노드의 경로를 설정해준다.

```bash
$ vi $HADOOP_HOME/etc/hadoop/hdfs-site.xml
<configuration>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:/hdfsNameNode</value>
    </property>
    <property>
        <name>dfs.datanode.name.dir</name>
        <value>file:/hdfsDataNode</value>
    </property>
</configuration>
```

yarn 에서는 리소스매니저 역할을 맡은 호스트명과, 맵리듀스에서 셔플을 자체적으로 할 수 있게 설정해준다.

```bash
$ vi $HADOOP_HOME/etc/hadoop/yarn-site.xml
<configuration>
    <property>
            <name>yarn.resourcemanager.hostname</name>
            <value>w01</value>
    </property>
    <property>
            <name>yarn.nodemanager.aux-services</name>
            <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
</configuration>
```

mapred 에서는 yarn 을 사용호도록 설정한다.

```bash
$ vi $HADOOP_HOME/etc/hadoop/mapred-site.xml
<configuration>
    <property>
	    <name>mapreduce.framework.name</name>
	    <value>yarn</value>
    </property>
</configuration>
```

마지막으로 워커 노드들에 대한 목록인 workers 파일에 노드들을 추가해준다.

```bash
$ vi $HADOOP_HOME/etc/hadoop/workers
w02
w03
w04
```

설정 파일들은 다른 워커노드들에도 복사해줘야 한다!

<br>

### 네임노드 포맷 및 실행

hdfs를 시작하기 전에는 네임노드를 초기화해야 한다.

명령어 자체는 간단하지만 말 그대로 포맷하는 것이므로, 기존의 네임노드나 데이터노드들에 존재하던 블록들에 대한 메타데이터가 사라지기 때문에 주의해야 한다.

네임노드를 포맷하면 새로운 hdfs 로 초기화되며, 기존 블록들이 디스크에 그대로 남아 있다고 할지라도 hdfs 상에서 접근이 불가능하다.

포맷은 ```hdfs namenode -format`` 과 같이 수행할 수 있다.

마지막으로 실행이 잘 되는지 확인하기 위해 마스터 노드에서 start-all.sh 스크립트를 실행한다.

이 스크립트는 여러 설정들을 읽고 dfs 와 yarn 을 실행시키는 스크립트이며, 정상적으로 실행될 경우에는 Starting 어쩌고저쩌고를 출력하며 namenode, datanode, secondary namenode, resource manager, node manager 등의 대몬들을 시작시킬 것이다.

문제 없이 켜질 경우 각 노드에서 ```jps```로 대몬이 올라와있는지 확인해볼 수 있고, 기본적으로 8088 포트에서 리소스매니저를, 9870 포트에서는 네임노드의 웹 UI 를 확인할 수 있다.