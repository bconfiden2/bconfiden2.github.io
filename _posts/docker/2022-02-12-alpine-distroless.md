---
layout: post
title: "경량화된 도커 이미지들, alpine 과 distroless"
tags: docker
---

개발과 배포에 있어서 컨테이너를 사용하는 일은 굉장히 흔해졌고, 그에 따라 이미지를 가볍게 만드는 것 역시 중요해진다.

이미지가 가벼워질수록 변경하거나 배포하는데 비용이 덜 들기 때문이다.

이러한 문제들을 해결하기 위해서는 일반적으로 베이스가 되는 이미지들을 경량화시킨 alpine 이미지를 사용한다.

alpine 이미지는 musl libc 와 busybox 를 기반으로 만든 경량화된 리눅스 배포판이라고 볼 수 있다.

그러나 알파인 같은 경우에는 기본 라이브러리들로 인해 발생하는 취약점들에 대한 리스크를 지니고 있다.

이미지 내에 원하는 기능 말고 다른 불필요한 실행파일들이나 라이브러리들이 존재한다는 뜻은, 취약점이 늘어나는 것과 같기도 하다.

<br>

distroless 는 alpine 의 취약점들을 해결하기 위해 구글이 만든 이미지들이다.

distroless 이미지들은 애플리케이션과 그 애플리케이션을 위한 런타임 실행 환경에 관련된 것들만 이미지에 존재한다.

이 안에는 일반적인 리눅스 배포판에 존재하는 기본적인 실행파일들, 쉘, 패키지 매니저마저도 포함되어있지 않기 때문에 컨테이너를 더 안전하게 만들 수 있다.

그러나, 전부 제외시켜버렸기 때문에 컨테이너에 쉘을 붙여 들어갈 수도 없게 된다.

사용자가 컨테이너에서 발생하는 문제점들을 직접적으로 디버깅 할 수 없는 등의 단점도 있지만, 그만큼 공격자 역시 컨테이너에서 활동할 수 없다는 장점이 되기도 한다.

<br>

## trivy로 취약점 테스트

[trivy](https://github.com/aquasecurity/trivy) 는 컨테이너 이미지나 파일시스템 등의 취약점을 검사해주는 오픈소스로, 아래처럼 간단하게 설치하여 사용할 수 있다.

```bash
$ sudo apt-get install wget apt-transport-https gnupg lsb-release
$ wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
$ echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list
$ sudo apt-get update
$ sudo apt-get install -y trivy
```

이를 이용하여 distroless 와 alpine 이미지의 차이를 확인해보자.

우선 distroless 이미지를 기반으로 하는 도커파일이다.

```Dockerfile
FROM node:8 as build

WORKDIR /app
COPY package.json index.js ./
RUN npm install

FROM gcr.io/distroless/nodejs

COPY --from=build /app /
EXPOSE 3000
CMD ["index.js"]
```

distroless 이미지에 배쉬 쉘이 없다보니, npm install 이 불가능했기 때문에 멀티 스테이지 빌드 방식을 사용하여 일반 node 이미지에서 작업한 뒤 옮겨왔다.

해당 이미지를 trivy 로 검사한 결과는 아래와 같다.

```bash
$ sudo trivy image nodejs-distroless
...
nodejs_distroless (debian 11.2)
=========================
Total: 19 (UNKNOWN: 0, LOW: 12, MEDIUM: 3, HIGH: 1, CRITICAL: 3)
...
```

다음으로는 alpine 을 기반으로 하는 도커파일과 trivy 결과이다.

```Dockerfile
FROM node:8-alpine

WORKDIR /app
COPY package.json index.js ./
RUN npm install

EXPOSE 3000
CMD ["npm", "start"]
```

```bash
$ sudo trivy image nodejs-alpine
...
nodejs-alpine (alpine 3.11.2)
===========================
Total: 48 (UNKNOWN: 0, LOW: 2, MEDIUM: 12, HIGH: 31, CRITICAL: 3)
...
```

<br>

## 결과 비교

distroless 기반 이미지는 취약점이 총 19개인 반면, alpine 은 48개가 발견되었다.

이미지의 크기도 같이 확인을 해보면,

```bash
$ sudo docker images
REPOSITORY                 TAG        IMAGE ID       CREATED          SIZE
nodejs-distroless                latest     66b04a14a5d4   11 minutes ago   118MB
nodejs-alpine                latest     4ba20429ef19   13 minutes ago   76.9MB
```

이미지 크기의 경우에는 alpine 이 조금 더 가벼운 편이지만, 취약점에 대해서는 distroless 가 훨씬 더 적은 것을 확인할 수 있다.

이미지에 포함된 실행파일들은 모두 취약점을 같이 가져간다고 볼 수 있기 때문에, 보안이 중요한 환경에서는 애플리케이션에을 제외한 나머지를 전부 제거한 distroless 이미지를 사용하는 것이 좋다.

alpine 같은 경우에는 이미지가 작은 편이기 때문에 테스트 환경에서 효율적으로 보이지만, alpine 은 muslc라는, 더 공간 효율적으로 커널을 다루는 C 라이브러리를 기반으로 만들어졌다.

일반적인 다른 리눅스 배포판은 더 보편적인 glibc 라이브러리를 기반으로 하기 때문에, 호환성 이슈가 발생할 가능성이 있다는 점을 유의해야 한다.

필요에 맞게 사용하면 될 듯 하다.