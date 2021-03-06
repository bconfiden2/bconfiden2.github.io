---
layout: post
title: "M1 Mac에서 이미지 빌드 시 쿠버네티스에서의 exec format error"
tags: docker
---

기존에는 우분투에 도커를 직접 설치하여 쓰다가, 아이맥에서 도커 데스크탑만 설치하면 된다는 사실을 얼마 전에 알았다.

평소에 연구실 서버나 집에 있는 데스크탑에 접속하여 작업하거나 이미지를 빌드했었는데, 아이맥에서 바로바로 테스트하고 빌드할 수 있어서 편하게 느끼고 있었다.

그러나 이렇게 빌드한 이미지를 사용하여, 우분투 기반 노드들로 띄워져 있는 쿠버네티스 클러스터에 파드를 실행시키니까 자꾸 ```exec format error```가 발생하였다.

도커파일을 아무리 봐도 문제가 없어 보이고, 맥에서 직접 도커 컨테이너를 띄울 때 역시 정상적으로 작동하니까 미쳐버릴 뻔 했다.

그러던 와중 [https://kimjingo.tistory.com/221](https://kimjingo.tistory.com/221)에서 동일한 이슈를 다룬 포스팅을 발견하게 됐다. 감사합니다...

<br>

일반적으로 exec format error는 도커파일에서 컨테이너가 기본적으로 실행시킬 명령을 세팅하는 ENTRYPOINT나 CMD가 잘못 설정되었을 때 발생하는 에러인데, 나의 경우는 로컬에서 문제 없는 것을 확인했다.

요약하자면 결국 ARM 기반에서 빌드된 이미지를 AMD 기반에서 실행시켰기 때문이다.

docker에서는 이런 문제를 해결하고자 다양한 플랫폼 별로 빌드할 수 있는 buildx 를 지원해주고 있기 때문에, ```docker buildx [--platform linux/amd64] ...```처럼 amd64 아키텍쳐를 지정해서 빌드해주면 해결된다.