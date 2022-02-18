---
layout: post
title: "[도커파일] 멀티 스테이지 빌드란?"
categories: devops
tags: docker
---

도커파일로 이미지를 빌드하는 경우 COPY, ADD, RUN 으로 어떤 작업을 수행할때마다 매번 새로운 컨테이너를 만든 뒤 커밋해서 레이어를 쌓는다.

예를 들어 아래의 도커파일은 apt 저장소를 업데이트한 레이어 위에 git 을 설치한 레이어가 추가되어 최종 이미지가 된다.

```Dockerfile
FROM ubuntu
RUN apt-get update
RUN apt-get install git
```

그러나 아래의 도커파일은, 최종 이미지의 기능 자체는 같지만 RUN 구문이 하나이기 때문에 레이어가 하나가 되는 것이다.

```Dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install git
```

레이어들은 이전 이미지와 현재 이미지의 차이점을 저장할 뿐이기 때문에, 다른 이미지와 레이어를 공유할 수 있다.

실제로 도커 허브 같은 레지스트리에서 로컬에 없는 이미지를 다운받으려고 할 때, 해당 이미지의 여러 레이어들을 검사하여 없는 레이어만 받아온다.

이는 docker build 명령어에서도 동일하게 적용되는데, 기존에 빌드했던 도커파일 아래에 구문 몇개만 추가할 경우, 빌드시 모든 구문을 새로 하지 않고 가지고 있던 레이어에 새로 추가된 구문들에 대한 레이어만 쌓는다.

이렇게 여러 이미지가 레이어를 공유한다고 하더라도 레이어는 공간을 차지하기 때문에, 레이어가 많아질수록 최종 이미지가 무거워진다.

또한 이미지를 빌드 중에, 사용하려고 하는 애플리케이션과 관련된 것들을 설치하다보면, 실제로는 사용하지 않는 그 외의 실행파일들이 많이 포함되게 된다.

이런 불필요한 내용들을 제거하고 필요한 바이너리만 가져오기 위해서 기존에는 ```빌더 패턴```이라는, 도커파일 두개를 활용하는 방식을 사용했다.

예를 들어 아래는 앱 빌드에 필요한 디펜던시들을 설정하고 바이너리를 빌드하기 위한 도커파일이고,

```Dockerfile
FROM golang:1.16
WORKDIR /go/src/github.com/alexellis/href-counter/
COPY app.go ./
RUN go get -d -v golang.org/x/net/html && CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .
```

아래는 배포를 위해 위의 도커파일에서 빌드한 실행파일만을 복사해오는 도커파일이다.

```Dockerfile
FROM alpine:latest  
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY app ./
CMD ["./app"]
```

마지막으로는 첫번째 도커파일을 빌드해서 필요한 애플리케이션을 가져와 두번째 도커파일을 완성시키는 스크립트로, 이렇게 목표로 하는 하나의 이미지를 만들기 위해 관리해야되는 파일이 많아지며 복잡해진다.

```bash
#!/bin/bash
docker build --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy \  
    -t alexellis2/href-counter:build . -f Dockerfile.build

docker container create --name extract alexellis2/href-counter:build  
docker container cp extract:/go/src/github.com/alexellis/href-counter/app ./app  
docker container rm -f extract

docker build --no-cache -t alexellis2/href-counter:latest .
rm ./app
```

<br>

이를 위해 하나의 도커파일에서 여러개의 FROM 을 사용하는 멀티 스테이지 빌드가 등장한다.

각각의 FROM 절에서는 서로 다른 베이스 이미지를 사용할 수도 있고, 각 FROM 마다 다른 스테이지가 새로 시작된다고 볼 수 있다.

또한 이런 스테이지들 사이에서 안에 있는 내용들을 서로 COPY 해갈 수도 있기 때문에, 빌더 패턴에서처럼 도커파일을 두개로 나눠 관리할 필요가 없어지는 것이다.

앞의 도커파일들을 멀티스테이지 방식으로 하나로 합친 코드는 아래와 같다.

```Dockerfile
FROM golang:1.16 AS build
WORKDIR /go/src/github.com/alexellis/href-counter/
RUN go get -d -v golang.org/x/net/html  
COPY app.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM alpine:latest  
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /go/src/github.com/alexellis/href-counter/app ./
CMD ["./app"]
```

첫번째 도커파일이 첫번째 스테이지로 들어가고, build 라는 이름을 갖게 된다.

두번째 도커파일이 두번쨰 스테이지로 들어가며, COPY 구문에서 --from=builder 로 첫번째 스테이지의 특정 디렉토리로부터 파일들을 복사해오는 것이다.

--from 에서는 다른 스테이지 뿐만 아니라 외부 이미지로부터도 가져올 수 있으며, 이전 스테이지를 베이스로 삼는 것 역시 가능하다.

이러한 멀티스테이지 빌드 방식은, 도커파일을 가독성 좋고 유지보수 하기 쉽게 관리하는데 도움이 많이 된다.

뿐만 아니라 배포를 위한 스테이지에서는 베이스 이미지를 alpine 이나 distroless 같은 경량화 이미지를 사용함으로써, 크기도 줄이고 보안도 강화할 수 있다.

