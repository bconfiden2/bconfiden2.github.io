---
layout: post
title: "[도커파일] docker build 와 Dockerfile"
subtitle: ""
categories: system
tags: docker
---

도커는 이미지를 활용해 컨테이너를 만들어서 사용하는데, ```Dockerfile``` 은 사용자가 주고 싶은 설정에 맞게 작성하여 이미지를 빌드할 수 있는 파일이다.

이미지를 만들 때 컨테이너를 생성하여, bash 쉘을 붙여 안에 들어가 직접 환경을 설정한 뒤 나와서 커밋하는 방법이 있지만, dockerfile 을 활용하는 것이 더 빠르고 간단하다.

또한 설치하는 패키지들을 명확하게 할 수 있고, 이미지 생성과 배포 과정이 ```docker build``` 명령어를 통해 자동화되기 때문에 dockerfile 이용이 권장된다.

<br>

## Build Image

docker build 명령어는 Dockerfile 을 읽어서 이미지를 빌드하는데, 도커파일이 위치한 로컬 파일시스템의 경로를 입력으로 넣어주며, 도커 대몬은 해당 경로와 그 아래의 모든 하위 경로들을 ```build context```로 취급한다.

그렇기 때문에 호스트의 루트를 빌드컨텍스트로 지정하는 것은, 하드디스크의 모든 파일들을 컨텍스트에 포함시키기 때문에 권장되지 않는다.

일반적으로 도커파일의 이름은 Dockerfile 을 사용하며, 컨텍스트의 루트에 위치시켜놓는다. 컨텍스트의 루트가 아닐 경우에는 -f 옵션을 주어서 도커파일의 위치를 명확하게 해준다.

예를 들어 빌드 컨텍스트는 이전 경로로 하지만 도커파일은 하위 디렉토리에 존재할 때 ```sudo docker build -f /path/to/a/Dockerfile ..```처럼 사용한다.

물론 도커파일이 빌드 컨텍스트 경로 아래에 존재해야 한다.

docker build 명령어에 -t 옵션을 줌으로써 빌드된 이미지의 이름과 태그를 지정해줄 수 있으며, 해당 이미지가 여러 태그가 붙을 경우에는 -t 옵션을 여러번 줄 수 있다.

도커파일은 한줄 한줄의 명령어가 독립적으로 실행되면서 각 결과들을 이미지에 새롭게 커밋한다.

빌드 시 내부적으로 명령어 하나를 수행할 때마다 새로운 임시 컨테이너를 생성하고, 그 안에서 작업을 수행한 뒤 이를 이미지로 커밋하는 일을 반복하고 있는 것이다.

예를 들어, ```RUN cd /tmp``` 가 있음에도 불구하고, 그 뒤의 명령어들은 새로운 컨테이너로 올라가기 때문에, 해당 경로 위에서 명령어들이 수행되지 않는다는 뜻이다.

한번 도커파일로 이미지를 빌드했다면, 그 다음 빌드 시에는 이전의 빌드에서 사용했던 캐시를 활용하여 반복적인 불필요한 빌드를 하지 않는다.

그러나 만약에 패키지 설치나 git clone 등으로 소스코드 등을 다운로드 받아야할 경우에는, 캐시된 레이어를 그대로 가져다 쓴다면 업데이트된 패키지를 받아오지 못하는 문제가 발생할 수 있다.

이런 경우에는 사용자의 필요에 따라서 ```--no-cache``` 옵션을 추가해서 빌드하면 된다.

또한 빌드를 효율적으로 하기 위해서 ```.dockerignore``` 파일을 작성함으로써 .gitignore 마냥 무시할 파일들을 명세할 수 있다.

<br>

## Format

도커파일은 ```INSTRUCTION arguments``` 형태로 내용들을 작성한다.

INSRUCTION 부분에는 다양한 명령어들이 있는데, 이들은 대소문자를 구별하지는 않는다. 그러나 arguments 들과 구별하기 위해 관행적으로는 대문자로 사용한다.

대몬이 도커파일을 읽어서 이미지를 빌드할 때, Dockerfile 의 위에서부터 순서대로 실행시킨다.

이 때 Dockerfile 은 반드시 ```FROM``` 명령어부터 시작해야하는데, 이는 해당 이미지가 어떤 이미지를 부모로 삼아 빌드할 것인지를 명세하는 INSTRUCTION 중 하나이다. 

도커파일에서의 주석은 ```#```으로 표시할 수 있고, 주석들은 이미지 빌드 과정에서 명령어가 실행될 때 제거된다.

즉, 아래처럼 디폴트 escape 문자로 지정된 ```\```를 사용하여, 개행이 들어간 하나의 INSTRUCTION 사이에 주석이 들어가도 문제가 발생하지 않는다는 뜻이다.

```dockerfile
FROM ubuntu:\
# This is a comment!
20.04
RUN ...
```

<br>

## docker build options

| option | Description |
| --- | --- |
| ```-t```, ```--tag``` | 'name:tag' 형식의 값을 줌으로써 빌드된 이미지의 이름과 태그를 지정한다. |
| ```--rm``` | '--rm=(true/false)' 처럼 사용하며, 디폴트는 true 이다. 빌드 성공시 빌드할때 생성되었던 임시 컨테이너들을 삭제할지 결정한다. |
| ```--force-rm``` | 임시 컨테이너들을 무조건 삭제한다. |
| ```--no-cache``` | 이미지를 빌드할 때 캐시되어있는 레이어들을 사용하지 않는다. |
| ```-f```, ```--file``` | 도커파일의 경로를 지정해주며, 디폴트값은 '빌드컨텍스트/Dockerfile' 이다. |
| ```-q```, ```--quiet``` | 빌드되는 과정을 출력하지 않고, 대신 빌드 성공시 이미지 ID 를 출력한다. |

이외에도 [공식문서](https://docs.docker.com/engine/reference/commandline/build/#options)에서 다양한 다른 옵션들을 확인할 수 있다.

<br>

## Sample Dockerfile

```dockerfile
FROM ubuntu:20.04   # 부모 이미지 설정

COPY test.sh /root  # 복사해올 파일은 빌드컨텍스트 안에 위치해야 함

ADD test.tar.gz /root

ENV TEST_HOME=/opt/test     # 변수 설정
ENV FOO=/bar

RUN apt-get update      # 각 명령어들이 독립적으로 실행됨
RUN apt-get install -y wget
RUN apt-get install -y openjdk-8-jdk

WORKDIR /opt

EXPOSE 8088 8888

CMD ["/bin/bash", "/root/test.sh"]
```
