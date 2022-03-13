---
layout: post
title: "맵리듀스 프로그램에서 셔플되는 로컬 데이터들의 위치"
tags: hadoop
---

맵리듀스 프로그램의 입력 혹은 출력은 하둡 분산파일시스템인 hdfs 상에 저장되기 때문에, 하둡 설정파일에서 명시된 datanode 위치를 따라간다.

그러나 매퍼는 자기가 출력한 임시 결과물들을 굳이 hdfs 에 저장할 필요가 없어서 로컬 파일시스템에 저장해두고 리듀서들이 그걸 네트워크를 통해 가져가기 때문에, 이 때 셔플 데이터들은 데이터노드에 저장되지 않는다.

이 임시 데이터들을 보관하는 경로를 하둡의 configuration 에서 지정할 수 있다.

경로에 해당하는 속성은 ```hadoop.tmp.dir```이며, 이 속성을 ```$HADOOP_HOME/etc/hadoop/core-site.xml```에서 설정해놓고 하둡을 실행시키면 된다.

하둡의 각종 설정파일들에서 담당하는 프로퍼티들은 만약 사용자가 따로 지정하지 않을 시 기본 값들을 가져다 쓰는데, 이는 ```$HADOOP_HOME/share/doc/hadoop/hadoop-project-dist``` 에서 확인할 수 있다.

core-site.xml 에 해당하는 기본파일은 위의 경로 안에 있는 ```hadoop-common/core-default.xml``` 파일이다.

```bash
user@hadoop:~$ cat /opt/hadoop/share/doc/hadoop/hadoop-project-dist/hadoop-common/core-default.xml
...
<property>
  <name>hadoop.tmp.dir</name>
  <value>/tmp/hadoop-${user.name}</value>
  <description>A base for other temporary directories.</description>
</property>
...
```

hadoop.tmp.dir 프로퍼티의 기본값은 ```/tmp/hadoop-user```이기에, yarn 에서는 이 경로 아래에다가 nm-local-dir 을 만들고 임시 데이터들을 애플리케이션마다 저장한다. 

/opt/hadoop/share/doc/hadoop/hadoop-yarn/hadoop-yarn-common/yarn-default.xml 를 확인해보면 ```yarn.nodemanager.local.dirs```의 값이 hadoop.tmp.dir/nm-local-dir 로 설정되어있음을 확인할 수 있다.

맵리듀스 프로그램을 돌려놓고 해당 경로를 실시간으로 확인해봐도 뭔가가 자꾸 생겼다가 사라졌다 하는 모습을 볼 수 있다.

만약 노드마다 디스크를 여러장 꽂아놓고, 해당 디스크를 데이터노드로 설정함으로써 hdfs 의 크기를 늘렸다고 하더라도, 셔플데이터의 경로를 지정해두지 않으면 맵리듀스 과정에서 디스크 부족 현상이 발생한다.

10TB 짜리 디스크를 가지고 있더라도, 파티션으로 나눠 대부분의 용량을 데이터노드가 가져갔다면 /tmp 에 쓸 수 있는 용량이 많이 없기 때문이다.

hadoop.tmp.dir 속성의 value 부분에는 여러 경로를 쉼표로 구분하여 넣어줄 수 있으므로, 맵리듀스 프로그램을 효율적으로 돌리기 위해서는 이 속성도 신경 써야 한다.