---
layout: post
title: "매퍼/리듀서에서 표준출력으로 디버깅하기"
categories: bigdata
tags: hadoop
---

잡을 제출하기 위한 드라이버 프로세스 부분에서는 System.out.println 등을 활용해 표준출력으로 아무거나 찍을 경우, 해당 프로세스를 실행시킨 노드의 표준출력에서 확인이 가능하다.

일반적으로는 매퍼나 리듀서에서 작업한 내용을 가지고 따로 카운터를 만들어 활용한 뒤, 아래처럼 드라이버 프로세스에서 잡이 끝나면 카운터 값을 확인하는 식으로 디버깅이 가능하다.

```java
@Override
public int run(String[] strings) throws Exception {
    Job job = Job.getInstance(conf, "test");
    job.setJarByClass(test.class);
    job.setMapperClass(testMapper.class);
    job.setMapOutputKeyClass(Text.class);
    job.setMapOutputValueClass(Text.class);
    job.setReducerClass(textReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    job.setInputFormatClass(TextInputFormat.class);
    job.setOutputFormatClass(TextOutputFormat.class);
    FileInputFormat.addInputPath(job, new Path(strings[0]));
    FileOutputFormat.setOutputPath(job, new Path(strings[1]));
    job.waitForCompletion(false);

    System.out.println("이 메시지는 드라이버 프로세스를 실행시킨 노드의 표준출력에 찍힘");
    // 매퍼 출력 레코드 수를 관리하는 카운터 값을 가져와서 출력
    System.out.println(job.getCounters().findCounter(TaskCounter.MAP_OUTPUT_RECORDS).getValue())
}

public static class testMapper extends Mapper<Object, Text, Text, Text> {
    @Override
    protected void map(Object key, Text value, Mapper<Object, Text, Text, Text>.Context context)
    throws IOException, InterruptedException {
        
        System.out.println("매퍼에서 블록에 있는 레코드마다 map 을 적용시킬 때 출력하고 싶음");
        System.out.println("드라이버의 표준출력에 찍히지 않음!");
    }
}
```

그러나 어떤 데이터를 어떤 매퍼가 가져가서 어떻게 출력하는지 등에 대한 정보 자체는 해당 매퍼에서 출력하는 것이 편한데, 이러한 출력값들은 당연히 드라이버를 실행시킨 노드에서 출력되지 않는다.

잡을 제출할 경우 YARN을 거쳐 워커노드들에 컨테이너가 생성된 뒤, 코드를 가져가 각각의 컨테이너들이 해당 노드에서 작업을 수행하기 때문이다.

그렇다면 알고리즘이나 작동 방식에 대한 매퍼나 리듀서별로 디버깅이 필요할 때는 어떻게 해야 할까?

<br>

하둡에서는 로그 경로로 지정해놓은 디렉토리 아래의 ```userlogs```에 여러 정보들을 저장한다.

로그 경로는 따로 설정하지 않았다면 기본적으로 하둡 홈 아래의 logs 로 지정되며, 이 아래의 userlogs 를 확인해본 결과는 아래와 같다.

```bash
$ ls -1 $HADOOP_HOME/logs/userlogs
application_1645073910576_0001
application_1645073910576_0002
application_1645073910576_0003
...
```

실행했던 애플리케이션별로 따로 디렉토리들이 만들어져있으며, 각 애플리케이션 아래에는 현재 노드에서 실행된 컨테이너들로 다시 구분된다.

```bash
$ ls -1 $HADOOP_HOME/logs/userlogs/application_1645073910576_0001
container_1645073910576_0001_01_000008
container_1645073910576_0001_01_000009
container_1645073910576_0001_01_000010
container_1645073910576_0001_01_000011
container_1645073910576_0001_01_000012
container_1645073910576_0001_01_000013
container_1645073910576_0001_01_000014
container_1645073910576_0001_01_000015
container_1645073910576_0001_01_000018
container_1645073910576_0001_01_000022
```

각각의 컨테이너에 해당하는 디렉토리 아래에는 다음과 같은 파일들이 존재한다.

```bash
$ ls -1 $HADOOP_HOME/logs/userlogs/application_1645073910576_0001/container_1645073910576_0001_01_000008
directory.info
launch_container.sh
prelaunch.err
prelaunch.out
stderr
stdout
syslog
```

이 파일들 중 stdout 이 맵리듀스 코드에서 매퍼나 리듀서에서 표준출력으로 찍은 내용이 담긴 파일이기 때문에, 원하는 애플리케이션에 찾아가 tail -f 등으로 실시간으로 확인할 수 있다.

<br>

이러한 정보들은 사실 리소스매니저 웹UI 에서도 확인이 가능하다.

웹UI 에서는 현재 실행중인 애플리케이션에 대해서 완료가 되기 전에는 맵이나 리듀스 진행 상황 등을 확인할 수 있는 페이지를 제공해주는데, 이 때 각 컨테이너별로 로그에 해당하는 링크도 들어가있다.

만약 이미 완료되어 히스토리서버로 넘어갔다고 하더라도, 히스토리 서버에서도 동일하게 제공되므로 문제는 없다.

1. 리소스매니저 웹UI

2. 원하는 애플리케이션의 Tracking UI 탭 클릭

3. 맨 아래 Attempt Type에서 원하는 상태(Failed, Killed, Successful)의 태스크 클릭

4. 확인하려는 컨테이너(Attempt)의 Logs 탭 클릭

로그를 확인하는 서비스는 기본적으로 각 노드마다 8042 포트에서 서비스되기 때문에, 클러스터에 속한 노드에서 브라우저를 열어 접속하는게 아닌 이상 ssh로 모든 노드들에 대해 터널링을 해줘야 한다.