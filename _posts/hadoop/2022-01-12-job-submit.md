---
layout: post
title: "로컬에서 맵리듀스 프로그래밍/디버깅 후 클러스터에 제출하기까지"
tags: hadoop
---

인텔리제이에서 프로그램을 짜며 로컬 환경에서 테스트해보기 위해서는 우선 메이븐 플러그인이 포함된 프로젝트를 생성해준다.

프로젝트의 pom.xml 을 아래와 같이 수정하여, 메이븐 설정과 관련된 프로퍼티와 맵리듀스와 관련된 디펜던시를 추가해준다.

인텔리제이는 일반적으로 텍스트파일을 수정하면 자동적으로 저장되기 때문에, pom.xml 파일을 수정할 경우 알아서 패키지를 설치할 것이다(혹은 우하단에 팝업창 같은걸로 물어봄).

5분 정도 기다려주면 된다.

```pom.xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.6.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
            </configuration>
        </plugin>
    </plugins>
</build>

<dependencies>
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-mapreduce-client-core</artifactId>
        <version>3.2.1</version>
        <scope>provided</scope>
    </dependency>
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-mapreduce-client-jobclient</artifactId>
        <version>3.2.1</version>
        <scope>provided</scope>
    </dependency>
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-common</artifactId>
        <version>3.2.1</version>
        <scope>provided</scope>
    </dependency>
</dependencies>
<properties>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
</properties>
```

<br>

src/main/java 경로 아래에 패키지를 생성해준 뒤, 해당 패키지 아래에 원하는 클래스를 생성한다.

이 클래스에는 메인함수가 포함되어 있어서, 나중에 클러스터에 잡을 제출하기 위한 드라이버가 실행된다.

예를 들어 아래는 맵리듀스 세계관에서 hello, world 역할을 맡고 있는 워드카운트 프로그램을 위한 클래스와 메인함수, 드라이버, 그에 맞게 구현한 매퍼와 리듀서 코드이다.

```java
public class WordCount extends Configured implements Tool {
    public static void main(String[] args) throws Exception {
        System.out.println("main executed: " + ManagementFactory.getRuntimeMXBean().getName());
        ToolRunner.run(new WordCount(), args);
    }

    @Override
    public int run(String[] strings) throws Exception {
        Job job = Job.getInstance(getConf(), "word counting");
        job.setJarByClass(WordCount.class);

        job.setMapperClass(wcMapper.class);
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(IntWritable.class);

        job.setReducerClass(wcReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        job.setInputFormatClass(TextInputFormat.class);
        job.setOutputFormatClass(TextOutputFormat.class);

        FileInputFormat.addInputPath(job, new Path(strings[0]));
        FileOutputFormat.setOutputPath(job, new Path(strings[1]));

        job.waitForCompletion(false);

        return 0;
    }

    public static class wcMapper extends Mapper<Object, Text, Text, IntWritable> {
        Text k = new Text();
        IntWritable v = new IntWritable(1);

        @Override
        protected void map(Object key, Text value, Mapper<Object, Text, Text, IntWritable>.Context context)
        throws IOException, InterruptedException {
            StringTokenizer st = new StringTokenizer(value.toString());
            while(st.hasMoreTokens()) {
                k.set(st.nextToken());
                context.write(k, v);
            }
        }
    }

    public static class wcReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
        IntWritable v = new IntWritable();

        @Override
        protected void reduce(Text key, Iterable<IntWritable> values, Reducer<Text, IntWritable, Text, IntWritable>.Context context)
        throws IOException, InterruptedException {
            int cnt = 0;
            for(IntWritable iw : values) {
                cnt++;
            }
            v.set(cnt);

            context.write(key, v);
        }
    }
}
```

JVM은 실행시킬 클래스의 메인함수를 찾아가기 때문에, 나중에 jar 파일로 빌드해서 WordCount 클래스를 지정해주면, 메인함수가 실행되며 Tool 인터페이스를 구현한 run 함수를 실행시킨다.

run 에서는, Configured 에서 상속받은 getConf() 함수를 통한 설정값들을 가지고 잡을 하나 만든 뒤, 구현해준 매퍼와 리듀서 및 다른 클래스들도 알맞게 지정해 놓는다.

<br>

실제로 분산 클러스터에서 실행시키기까지는 그 과정이 그렇게 편하지는 않기 때문에, 가능하면 ide상에서 테스트해보고 디버깅하는 것이 좋다.

이를 위해 인텔리제이에서 테스트 클래스를 작성해서 돌려볼 수 있다.

메인 코드들은 프로젝트에서 src/main/java 아래에 작성하였는데, 테스트 클래스는 src/test/java 에 위치해야 한다.

메인 프로그램과 마찬가지로 해당 경로 아래에, 돌릴 클래스가 속한 패키지명과 같은 이름의 패키지를 생성해준 뒤 클래스를 만들어 아래와 같이 작성한다.

```java
package wordcount;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.util.ToolRunner;

public class WordCountTest {
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        conf.setInt("test1", 1);
        // 각종 설정값들 지정
        ToolRunner.run(conf, new WordCount(), new String[]{"input.txt", "output"})
    }
}
```

테스트 클래스에서 생성한 Configuration 이 그대로 넘어가고, 스트링 배열 객체가 메인 클래스의 String[] args 파라미터로 들어간다.

실행시키기 위해서는 우상단의 실행 모양을 누른다(원하는 테스트클래스가 없을 경우에는 Edit Configuration 에 들어가 직접 설정).

<br>

테스트클래스를 통해 원하는 맵리듀스 메인 클래스를 실행시키면, 기본적으로 표준출력에 해당하는 내용들만 인텔리제이의 콘솔에 찍히고 하둡에서 출력하는 로깅들은 가려진다.

이를 위해 src/test/resources 경로 아래에 log4j.properties 로 로깅 포맷을 변경이 가능하다.

```log
# Set root logger level to DEBUG and its only appender to A1.
log4j.rootLogger=INFO, A1

log4j.appender.A1=org.apache.log4j.ConsoleAppender
log4j.appender.A1.layout=org.apache.log4j.PatternLayout
log4j.appender.A1.layout.ConversionPattern=[ %d{yyyy-MM-dd HH:mm:ss} %-5p %x ] %-25C{1} :%5L - %m%n
```

위의 파일을 넣을 경우 클러스터에 실행할때와 비슷하게 각종 카운터값들이 찍히며, 에러가 발생했을 때의 메시지도 확인이 가능하다.

<br>

클러스터에 잡을 제출하기 위해서는 jar 파일로 빌드해야 한다.

터미널에서 프로젝트의 루트디렉토리로 간 뒤 ```mvn install```로 target 디렉토리 아래에 jar 파일을 생성할 수 있다.

해당 파일을 클러스터의 원하는 노드로 가져간 뒤에, ```hadoop jar test.jar wordcount.WordCount input.txt output```와 같이 원하는 클래스를 실행시키면, 우리가 작성했던 메인함수가 호출된다.

메인에서 잡을 만든 뒤 waitForCompletion을 통해 클러스터에 제출하며 맵리듀스 프로그램이 실행된다.

명령어 뒤에 넣어주는 텍스트들은 기본적으로 메인함수의 인자(```String[] args```)로 들어가기 때문에, 현재는 이를 통해 입력 파일이나 출력 경로 등을 지정해주고 있다.

인자들에 ```-D```를 붙일 경우에는 클러스터의 설정값들을 오버라이드한다는 뜻이 되며, 예를 들어 ```-Dmapreduce.job.reduces=10```과 같이 리듀서 개수를 지정하여 실행시킬 수 있다.

클러스터 설정에서 디폴트값은 리듀서가 1개이기 때문에, 따로 xml 파일에서 속성값을 설정해두지 않고 실행시킬 때 오버라이드도 하지 않으면 사실상 리듀서 1개로 비효율적인 분산처리를 하게 되므로 주의해야 한다.

그 외에도 프로그램에서 사용할 개인적인 설정값들도 지정 가능하다.