---
layout: post
title: "도커에서 부모 이미지와 자식 이미지"
tags: docker
---

도커파일을 통해 이미지를 빌드할 때, RUN 명령어들은 각자 독립적으로 시행된다.

위에서부터 아래로 도커파일을 읽으면서, 대몬은 임시 컨테이너를 만들어 명령을 수행한 뒤 해당 컨테이너를 이미지로 커밋한 뒤 종료시키고, 아래에 있는 또다른 명령어는 방금 만들어진 이미지를 기반으로 또다시 임시 컨테이너를 만들어 새로운 이미지로 커밋하는 방식이다.

이미지를 빌드하기 위한 명령어들이 트리 구조로 연결되어, 각 단계의 이미지들이 부모-자식 관계가 되는 것이다.

이 때 최종적으로 빌드된 이미지의 크기에 주의해야 할 점이 있다.

Dockerfile 을 통해, 부모 이미지로부터 생성된 이미지는 해당 부모이미지를 복사해서 갖고있는것이 아니라 >이미지를 공유한다.

예를 들어, 우분투 이미지를 기반으로 만들어졌다면 해당 레이어를 참조하는 것이지, 부모 이미지가 가지고 >있던 설정들을 복사해오는 것이 아니다(값 복사 vs 레퍼런스).

그렇기 때문에 이미지를 삭제(```docker rmi```)할 경우에는, 해당 이미지를 부모로 가지던 다른 이미지들은 dangling 상태(<none> <none>)으로 남아있게 된다.

이런 상황 속에서 아래의 도커파일을 확인해보자.

```Dockerfile
FROM ubuntu:20.04
RUN mkdir /data
COPY data_low.csv /data/low.csv
RUN rm /data/low.csv
```

우분투 이미지를 기반으로 해서, 루트 디렉토리에 data 를 만들고, 호스트OS의 빌드컨텍스트 안에 있던 csv 파일을 해당 경로에 복사한 뒤, 다시 데이터를 지운 이미지를 만드는 것이다.

물론 실질적으로는 데이터를 다른 RUN 명령어를 통해 활용하겠지만 일단은 문제점만 확인하기 위해 말도 안되는 도커파일을 가져온 것 뿐이다.

일반적으로 생각했을 때는 최종 이미지의 크기가 ubuntu:20.04 와 동일해야 한다.

데이터를 복사해왔지만 마지막엔 지우고 커밋했기 때문이다.

그러나 앞서 말했듯, 도커파일로 빌드될 때는 각 명령어들이 독립적으로 컨테이너화 되었다가 커밋되며, 자식은 부모로 설정된 이미지를 참조할 뿐이기 때문에 예시의 도커파일로 나오는 최종 이미지는 중간단계들의 이미지를 부모로 가지고 있다.

아래의 빌드 과정을 확인해 보면, 최종이미지인 05dc09fe698c 는 2f0c815d7853 - 8d53a793f2e7 - 86d6e4244396 - 02cd9233771b - fb52e22af1b0 순으로 관계가 이루어진다.
```
bconfiden2@server:~/docker$ sudo docker build -t test:1.0 -f Dockerfile .
Sending build context to Docker daemon  14.89MB
Step 1/4 : FROM ubuntu:20.04
 ---> fb52e22af1b0
Step 2/4 : RUN mkdir /data
 ---> Running in 02cd9233771b
Removing intermediate container 02cd9233771b
 ---> 86d6e4244396
Step 3/4 : COPY data_low.csv /data/low.csv
 ---> 8d53a793f2e7
Step 4/4 : RUN rm /data/low.csv
 ---> Running in 2f0c815d7853
Removing intermediate container 2f0c815d7853
 ---> 05dc09fe698c
Successfully built 05dc09fe698c
Successfully tagged test:1.0
```

그래서 부모 이미지가 이미 data_low.csv 를 포함하여 커밋이 되었기 때문에, 그 아래에서 데이터를 삭제하여 커밋한다고 할지라도 부모 이미지참조하면서 해당 크기가 반영된다.

이러한 문제점은, 하나의 RUN 명령어에 여러 커맨드를 입력해주면 된다.

예를 들어, && 같이 터미널 명령어들을 묶어준다면, 해당 RUN 은 하나의 임시 컨테이너에서 실행된 뒤 이미지로 만들어지기 때문에 데이터가 지워진 뒤 커밋될 수 있는 것이다.

이외에도, ```docker export```를 사용하여 컨테이너에서 파일시스템만을 추출한 뒤 ```docker import```로 이미지를 만들 수 있다.

```bash
bconfiden2@dmlab-bear0:~/docker-pyspark-streaming/etc$ sudo docker run -d test:1.0
0e755c0cbbf438c896093843be6df82da2bdad7cf3d386cfd78468e83052fdb0

bconfiden2@dmlab-bear0:~/docker-pyspark-streaming/etc$ sudo docker export 0e755c0cbbf4 | sudo docker import - test:2.0
sha256:d3ef7cf2ab4b4e95da81bfa12b0e8fc25babeaebf5631da7c4257be74ac7b08c

bconfiden2@dmlab-bear0:~/docker-pyspark-streaming/etc$ sudo docker images
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
test           2.0       d3ef7cf2ab4b   5 seconds ago    72.8MB
test           1.0       9c9aa9b608e0   41 seconds ago   87.5MB
```

앞에서 빌드했던 test:1.0 이미지에서 파일시스템만을 export 로 뽑아낸 뒤, test:2.0 이라는 이미지로 import 한 결과 데이터 크기만큼(현재는 약 15MB) 이미지 사이즈가 줄어든 것을 확인할 수 있다.
