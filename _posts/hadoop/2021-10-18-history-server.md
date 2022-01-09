---
layout: post
title: "[맵리듀스] 히스토리 서버는 왜 사용할까"
subtitle: ""
categories: bigdata
tags: hadoop
---

맵리듀스 잡(혹은 하이브/피그와 같이 맵리듀스를 기반으로 하는 프로그램)을 돌리는 과정에서 간혹 잡의 상태를 읽으려고 할 때 아래와 같은 에러가 발생하는 경우가 있다.

```bash
2021-10-18 10:51:11,209 [main] INFO 
org.apache.hadoop.mapred.ClientServiceDelegate - Application state is completed. FinalApplicationStatus=SUCCEEDED. **Redirecting to job history server**
2021-10-18 10:51:11,213 [main] INFO  org.apache.hadoop.ipc.Client - Retrying connect to server: X.X.X.X/X.X.X.X:10020. Already tried 0 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
2021-10-18 10:51:12,213 [main] INFO  org.apache.hadoop.ipc.Client - Retrying connect to server: X.X.X.X/X.X.X.X:10020. Already tried 1 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
2021-10-18 10:51:13,213 [main] INFO  org.apache.hadoop.ipc.Client - Retrying connect to server: X.X.X.X/X.X.X.X:10020. Already tried 2 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
...
```

JobTracker 나 ResourceManager 는 맵리듀스 잡이 돌아갈 때 해당 정보들을 메모리에 올려놓고 관리한다.

그러나 모든 잡들에 대해서 기억하기에는 메모리에 한계가 있기 때문에, 잡이 종료된 이후에는 더이상 메모리에 올려놓지 않고, 히스토리 서버로 하여금 종료된 잡들에 대한 정보를 트래킹할 수 있게끔 구성한 것이다.

예를 들어 아래처럼 맵리듀스에서 기본적으로 제공해주는 TaskCounter 나 사용자가 필요에 맞게 쓰는 다양한 카운터들의 값을 읽어오는 경우가 있을 것이다.

```
job.getCounters().findCounter(TaskCounter.MAP_OUTPUT_BYTES).getValue();
job.getCounters().findCounter(UserDefinedCounters.NUM_CHANGES).getValue();
```

잡트래커나 리스소매니저의 메모리에도 올라와있지 않은 상황이라면, 프로그램은 히스토리서버에 응답을 요청하겠지만 만약 꺼져있을 경우에는 반복적으로 요청을 보내는 것이다.

따라서 맵리듀스를 돌릴 때 히스토리 서버를 켜주도록 하자.

<br>

## 실행시키기

히스토리 서버를 실행시키는 것은 간단하다.

설치해놓은 하둡 경로 아래에 있는 sbin 디렉토리에는 dfs, yarn 등 다양한 프로그램들을 실행시킬 수 있는 쉘스크립트들이 존재하는데, 여기에 히스토리 서버를 실행시키는 쉘스크립트도 있다.

```bash
hadoop@hadoop:/opt/hadoop/sbin$ bash $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver

# 실행되면 jps 에 JobHistoryServer 등장!
hadoop@hadoop:/opt/hadoop/sbin$ jps
25168 NameNode
25376 DataNode
23762 JobHistoryServer
25666 SecondaryNameNode
25955 ResourceManager
26170 NodeManager
14058 Jps
```

위와 같이 히스토리 서버를 시작시킬 수 있지만, 해당 스크립트를 읽어보면 대략적으로 ```$HADOOP_HOME/libexec/yarn-config.sh``` 를 실행시킨 뒤 exec 으로 대체하는 것으로 보이는데, 파악하기가 힘들다.

쉘스크립트도 단순한 실행 로직을 넘어서 실질적인 부분에 대한 공부가 정말 많이 필요하다는 걸 느꼈다.

히스토리 서버는 하둡에서 19888 포트를 통해 웹UI 를 제공하고 있어서, GUI 로도 상태를 확인할 수 있다.

해당 페이지에서는 애플리케이션 마스터 정보, 맵태스크, 리듀스태스크들이 어떤 노드에서 시간을 얼마가 걸렸는지 등 맵리듀스가 수행되는 과정을 볼 수 있기 때문에, 파티셔닝에 문제가 있었는지도 점검이 가능하다.