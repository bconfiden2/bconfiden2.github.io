---
layout: post
title: "SequenceFile.Reader로 바이너리 형태의 시퀀스파일 직접 읽어오기"
categories: bigdata
tags: hadoop
---

맵리듀스에서는 일반적으로 TextInput(Output)Format 을 사용하여 텍스트파일을 읽거나 출력하지만, 특정 데이터 구조를 유지한 상태인 바이너리 형태로도 읽거나 쓸 수 있는데, 이를 SequenceFile 이라고 한다.

즉, 지정한 Writable 형태에 맞게 바이너리 형태의 파일을 매퍼의 입력이나 리듀서의 출력으로 설정 가능하다.

실제로 생성된 시퀀스파일을 확인해보면, 아래처럼 이상한 문자들로 인코딩되는 것을 확인할 수 있다.

```bash
$ cat part-r-00000
SEQtestWritables.KeyWritabletestWritables.ValueWritable4A�#�g~Z�����0�K�����v&�>T� �/ƾ�UɿpȾ�q��8i�>�?�`��r?�ܖ>...
```

특정 잡의 리듀서에서 시퀀스파일 형태로 출력한 데이터가 있다고 했을 때, 이것이 다른 잡의 시퀀스파일 형태의 입력으로써 들어가게 되는 경우에는 맵리듀스의 프레임워크 내부적으로 잘 처리해서 읽어오기 때문에 문제가 없다.

그러나 이런 시퀀스파일을 직접 읽어와야 하는 경우에는 애로사항이 발생한다.

<br>

일반적으로 hdfs 의 특정 파일을 읽기 위해서 하둡에서는 FileSystem 이라는 객체에 다양한 메써드를 구현해놓았다.

[FileSystem](https://hadoop.apache.org/docs/stable/api/org/apache/hadoop/fs/FileSystem.html) 레퍼런스를 보면 open, close, create 등의 다양한 함수들이 있기 때문에, 아래처럼 프로그램에서 Path 객체를 넣어 파일을 불러올 수 있게 해준다.

```java
Configuration conf = getConf();
FileSystem fs = FileSystem.get(conf);
FSDataInputStream in = fs.open(new Path("filename"));
// in.readInt()
// ...
```

여기서 conf 는 Configuration 객체로, 일반적으로 맵리듀스 프레임워크에서는 getConf()나 매퍼/리듀서의 context.getConfiguration() 등을 통해 가져올 수 있다.

open 은 FSDataInputStream 객체를 반환하는데, 이 객체는 java.io.DataInput 인터페이스를 구현하고 있기 때문에 각종 타입을 read 해올 수 있는 것이다.

이처럼 매퍼나 리듀서의 setup 함수에서 hdfs 의 특정 파일을 메모리로 로드해오는 경우가 있는데, 이러한 시퀀스파일은 파일시스템 api 에서 제공되는 open() 으로 열어도 의미가 없다.

파일을 오픈 할 수는 있지만, open()의 결과로 반환된 FSDataInputStream 으로 아무리 값들을 읽어와봤자 원하던 값이 나오지 않는다.

이는 시퀀스파일이 바이너리 형태로써, 저장되어있는 자료구조들을 유지하기 위한 정보들을 헤더에 저장하고 있기 때문이다.

이 헤더에는 저장하고있는 포맷에 대한 정보, 키-값에 해당하는 클래스 정보, 버전과 압축 형태, 압축 사용시 코덱 클래스 정보 등이 들어있다.

앞서 파일을 텍스트로 확인했을 때, 앞부분에 등장한 영어들이 이런 메타데이터들이라고 보면 된다.

<br>

아무튼 시퀀스파일을 직접 읽어가기 위해서는 이러한 헤더를 따로 읽어내서 처리해야하기 때문에, 하둡에서는 SequenceFile.Reader 를 제공하며, 아래처럼 사용할 수 있다.

```java
KeyWritable key = new KeyWritable();
ValueWritable value = new ValueWritable();

@Override
protected void setup(Mapper<Text, Text, Text, Text>.Context context) throws IOException, InterruptedException {
    
    Configuration conf = context.getConfiguration();
    FileSystem fs = FileSystem.get(conf);
    SequenceFile.Reader reader = new SequenceFile.Reader(conf, SequenceFile.Reader.file(new Path("filename")));
    while(reader.next(key, value))
    {
        // key, value 에 키-값이 들어옴
    }
}
```

하둡에서 제공하는 [SequenceFile.Reader](https://hadoop.apache.org/docs/r2.8.0/hadoop-project-dist/hadoop-common/api/org/apache/hadoop/io/SequenceFile.Reader.html) 레퍼런스를 참고하면, SequnceFile.Reader 를 생성할 때 Configuration 정보와 옵션 정보들을 넣어줘야 한다.

Configuration 같은 경우에는 위와 마찬가지로 프레임워크 측면에서 동일하게 넘어오고 있는 객체를 사용할 수 있다.

이 때 넣을 수 있는 옵션 중에는 대표적으로 파일경로가 있는데, 그 외에는 레퍼런스에서 반환값이 SequenceFile.Reader.Option 인 스태틱 함수들을 확인하면 된다.

이렇게 리더 객체를 생성하게 되면, 객체에 달려있는 next 메써드로 시퀀스파일에서 키-값쌍 데이터를 하나씩 읽어서 반환한다.

현재 key 와 value 는 모두 직접 구현한 writable 인데, 이렇게 Writable 이 구현되어있는 객체를 넘겨주게 되면 next에서는 해당 객체가 오버라이드하고있는 readFields 대로 데이터를 채워넣어준 뒤 true 를 반환하며, 더 이상 읽을 값이 없을 경우에는 false 를 반환한다.

```java
public class ValueWritable implements Writable {
    public int value;
    // ...

    @Override
    public void write(DataOutput out) throws IOException {
        // out.writeInt(value)
        // ...
    }
    @Override
    public void readFields(DataInput in) throws IOException {
        // value = in.readInt()
        // ...
    }
}
```

이 때 동일한 객체를 넘겨주고 readFields 에서는 일반적으로 멤버 변수의 값만 교체하는 방식이기 때문에, 읽어온 키값에 대해 처리할 때 주의해야 한다.

예를 들어 키나 값에 대해 캐싱해놓을 필요가 있을 경우에는, 매번 새로운 객체를 생성하여 reader 에 넘겨주지 않는 이상 결과적으로 모든 값들이 동일한 객체를 가리키게 될 뿐인 것이다.

매퍼의 입력 포맷으로 SequnceFileInputFormat 이 지정된 경우에도, 내부적으로 이런 방식으로 시퀀스파일을 읽어간 뒤 리더에서 읽어오는 키값쌍마다 map 함수를 적용시켜주는 방식이라고 볼 수 있다.

하둡에서는 SequenceFile.Writer 역시 제공하고 있기 때문에, 맵리듀스 프레임워크에서 제공되는 context 에 쓰는 것 말고도 리더와 동일한 방식으로 시퀀스파일을 직접 쓸 수도 있다.