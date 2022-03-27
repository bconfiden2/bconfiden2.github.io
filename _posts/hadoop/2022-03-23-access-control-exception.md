---
layout: post
title: "트러블슈팅 - 클러스터 세팅 후 최초로 애플리케이션 제출시 발생하는 AccessControlException"
tags: hadoop
---

클러스터에 하둡을 설치하고 시험삼아 간단한 맵리듀스 프로그램을 제출하는데, 계속 아래와 같은 메시지가 뜬다.

```bash
bconfiden2@h01:~$ hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.1.jar wordcount input output
Exception in thread "main" org.apache.hadoop.security.AccessControlException: Permission denied: user=bconfiden2, access=WRITE, inode="/":hadoop:supergroup:drwxr-xr-x
at org.apache.hadoop.hdfs.server.namenode.FSPermissionChecker.check(FSPermissionChecker.java:319)
        at org.apache.hadoop.hdfs.server.namenode.FSPermissionChecker.checkTraverse(FSPermissionChecker.java:259)
        at org.apache.hadoop.hdfs.server.namenode.FSPermissionChecker.checkPermission(FSPermissionChecker.java:205)
        어쩌고 저쩌고...
```

에러 메시지를 읽어 보면, 대략적으로 특정 경로(루트)에 쓰기 권한이 없어서 발생하는 에러라고 해석된다.

일반적으로 이런 권한 문제는 해당 파일시스템(hdfs)에 사용자의 쓰기 권한 등을 설정해주면 해결되지만, 이미 소유자나 그룹 등의 세팅 등은 마쳐놓았기 때문에 약간 이해가 되지 않았다.

게다가 현재 제출한 애플리케이션은 에러 메시지에서 지정된 루트에다가 뭔가 쓰는 프로그램이 아니기도 하다.

즉, 입력한 hdfs의 경로로부터 데이터를 읽어오고, 입력한 경로로 결과를 출력하는 프로그램에서, 입출력 경로를 둘 다 사용자의 홈디렉토리로 지정한 상태이다.

또한 홈디렉토리에 사용자의 읽기/쓰기 권한 역시 정상적으로 설정되어있음을 확인하였는데, 뜬금없이 루트에 쓰기 권한이 없다는 에러가 발생하고 있는 것이다.

<br>

결과적으로 해당 이슈는 하둡에서 애플리케이션들에 대한 메타데이터들(각 사용자별 제출 기록 등등)을 관리하기 위해 /tmp 디렉토리 아래에 데이터를 저장하기 때문에 발생하는 것으로 확인되었다.

설치 후 처음 애플리케이션이 제출된 상황에서 이런 정보를 ```/tmp/hadoop-yarn/staging``` 에 저장하려고 했으나, 해당 경로가 없다보니 tmp를 만드려고 시도한 것이다.

그런데 tmp는 루트 아래에 있기 때문에 루트에 경로를 생성하려다가 권한 이슈가 발생하게 된 것이다.

따라서 하둡 대몬들을 실행시켰던 관리자 계정으로 /tmp 를 만들어주고, 해당 경로의 소유자 및 접근 권한 등을 풀어줌으로써 문제를 해결했다.

```bash
hadoop@h01:~$ hdfs dfs -chown -R hadoop /tmp
hadoop@h01:~$ hdfs dfs -chmod -R 777 /tmp
```

소유자는 하둡 클러스터 관리 계정인 hadoop 으로 지정해주는 대신 권한을 777 로 세팅함으로써 일반 유저들이 제출한 애플리케이션의 결과들을 각자 기록할 수 있게 만들어준다.

이후에도 사용자 애플리케이션들이 해당 디렉토리 아래에 로그들을 남겨놓기 때문이다.