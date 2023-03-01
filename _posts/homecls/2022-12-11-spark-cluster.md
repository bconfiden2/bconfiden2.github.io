---
layout: post
title: "스파크 Standalone 클러스터 구축"
tags: homecls
---

### 스칼라 설치

클러스터를 세팅하기에 앞서, 스파크에서 메인 언어로 사용하는 스칼라를 먼저 설치해준다.

스칼라 [공식 홈페이지](https://www.scala-lang.org/download/)에서 다운로드할 수 있으며, 특정 버전을 설치해야한다면 릴리스들을 확인한다.

현재는 2.11 버전을 쓸 일이 있어서, [2.11.12](https://www.scala-lang.org/download/2.11.12.html)를 설치하였다.

homebrew로는 직접 설치할 수 있지만, apt나 yum 같은 패지키 관리자는 지원해주지 않는 모양이기 때문에, deb 파일을 직접 받았다.

```bash
bconfiden2@h01:~/Downloads$ sudo dpkg -i scala-2.11.12.deb 
Selecting previously unselected package scala.
(Reading database ... 548977 files and directories currently installed.)
Preparing to unpack scala-2.11.12.deb ...
Unpacking scala (2.11.12) ...
Setting up scala (2.11.12) ...
Processing triggers for man-db (2.9.1-1) ...
```

<br>

스칼라로 짠 코드를 빌드하여 실행하기 위한 빌드 도구인 sbt(simple build tool) 역시 같이 설치해준다.

아래 명령어들로 sbt를 다운로드 받을 수 있는 저장소를 가져와서, apt에 인식시키고 설치한다.

```
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | sudo tee /etc/apt/sources.list.d/sbt_old.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add
sudo apt-get update
sudo apt-get -y install sbt
```

설치가 완료되면 마지막에 sbt 버전을 출력해보자.
```
bconfiden2@h01:~/Desktop$ sbt -V
downloading sbt launcher 1.8.2
[info] [launcher] getting org.scala-sbt sbt 1.8.2  (this may take some time)...
[info] [launcher] getting Scala 2.12.17 (for sbt)...
sbt version in this project: 1.8.2
sbt script version: 1.8.2
```

<br>

### 스파크 설치

스파크 실행 파일은 [아파치 아카이빙](https://archive.apache.org/dist/spark/)에서 받을 수 있다.

필요한 스파크 버전을 맞춰 다운로드하는데, 나는 일단 스칼라 버전에 맞춘 스파크 2.4가 필요하기 때문에 spark-2.4.0-bin-without-hadoop.tgz 를 받아왔다.

하둡 설치와 마찬가지로 /opt 에 압축을 풀어주고, 심볼릭 링크를 걸어주고, 환경 변수를 세팅해준다.

```bash
bconfiden2@h01:~$ sudo mv ~/Downloads/spark-2.4.0-bin-without-hadoop.tgz /opt
bconfiden2@h01:~$ cd /opt
bconfiden2@h01:/opt$ sudo tar -xzf spark-2.4.0-bin-without-hadoop.tgz
bconfiden2@h01:/opt$ sudo ln -s spark-2.4.0-bin-without-hadoop spark
bconfiden2@h01:/opt$ sudo vi ~/.bashrc
# ...
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_PATH=/opt/spark
export PATH=$SPARK_PATH/bin:$SPARK_PATH/sbin:$PATH

bconfiden2@h01:/opt$ source ~/.bashrc
```

<br>

클러스터 환경설정 파일들 몇가지를 수정해준다.

해당 파일들은 압축 풀어줬던 스파크 경로 아래에 conf 라는 디렉토리로 존재하므로, 심볼릭 링크를 통하면 `/opt/spark/conf`로 접근할 수 있다.

초기에는 각종 파일들에 대해 template 형식으로 제공해주기 때문에, 필요에 따라 복사하여 사용한다.

먼저 spark-env.sh 파일은 각종 환경변수들을 설정해두어, 스크립트로 클러스터를 실행할 때 읽어가서 적용한다.

어떤 환경변수들을 세팅할 수 있는지는 [spark-env.sh 문서](https://spark.apache.org/docs/latest/spark-standalone.html#cluster-launch-scripts)를 참고하며, 지금은 기본적인 변수들만 지정한다.

```bash
bconfiden2@h01:/opt/spark/conf$ cp spark-env.sh.template spark-env.sh
bconfiden2@h01:/opt/spark/conf$ vi spark-env.sh
# ...
SPARK_MASTER_HOST='192.16.100.141'
SPARK_WORKER_CORES=2
SPARK_WORKER_MEMORY=2g
```

<br>

다음으로는 스파크의 각종 프로퍼티들을 설정해주는 spark-defaults.conf 파일이다.

사용자가 스파크 잡을 제출할 때 spark-submit 뒤에 여러가지 옵션들을 지정하여 명령어를 실행할 수 있는데, 이 때 기본적으로 세팅할 프로퍼티들을 파일에 설정해두는 것이다.

어떤 프로퍼티들이 있고, 어떤 의미를 가지는지는 [spark-defaults.conf 문서](https://spark.apache.org/docs/latest/configuration.html#dynamically-loading-spark-properties)를 참고한다.

```bash
bconfiden2@h01:/opt/spark/conf$ cp spark-defaults.conf.template spark-defaults.conf
bconfiden2@h01:/opt/spark/conf$ vi spark-defaults.conf
# ...
spark.master    spark://h01:7077  
spark.driver.maxResultSize      4g
```

<br>

마지막으로는 클러스터의 워커노드들을 지정해주는 파일로, 하둡에서의 etc/hadoop/workers 같은 역할이다.

원래 홈클러스터는 그램 노트북 하나를 추가하여 3대이지만 연구실에 두고 왔기 때문에 2대로만 진행하고 있어, 워커 노드를 h02 하나만 넣어준다.

```bash
bconfiden2@h01:/opt/spark/conf$ cp slaves.template slaves
bconfiden2@h01:/opt/spark/conf$ vi slaves
# ...
h02
```

워커노드들에 rsync를 사용하여 동일하게 복사해주고, 클러스터를 실행한다.

```bash
bconfiden2@h01:~$ rsync -avh /opt/spark-2.4.0-bin-without-hadoop h02:/opt
bconfiden2@h01:~$ rsync -avh /opt/spark-2.4.0-bin-without-hadoop h03:/opt # 지금은 없음 !
```
```bash
bconfiden2@h01:~$ cd /opt/spark/sbin
bconfiden2@h01:/opt/spark/sbin$ ./start-all.sh
starting org.apache.spark.deploy.master.Master, logging to /opt/spark/logs/spark-bconfiden2-org.apache.spark.deploy.master.Master-1-h01.out
# ...
# ...
```