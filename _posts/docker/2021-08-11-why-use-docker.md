---
layout: post
title:  "도커란 무엇이고 왜 사용할까?"
subtitle:  "docker"
categories: study
tags: docker
---

도커(Docker)는 부두에서 일하는 노동자들을 뜻하는데, 노동자들이 컨테이너를 다루듯 도커도 컨테이너라는 기술을 바탕으로 만들어진 가상화 플랫폼이다.

도커를 알아보기 전에 먼저 가상화라는 것을 알아야 한다.

<br>

### 가상화

예를 들어 학교마다 수강신청 서버가 있을텐데, 수강신청 기간에는 몇천명이 동시에 접속을 하기 때문에 이 요청을 처리할 많은 컴퓨팅 파워를 필요로 한다.

그러나 그 외의 기간에는 학생들이 수강신청 서버에 접속할 일이 거의 없으므로, 기껏 돈 들여 산 서버들이 놀게 된다.

필요할 때만 서버가 유동적으로 늘어나고 줄어드는 그런 시스템이 구축되면 좋은데, 이런 개념으로 등장한 것이 가상머신이다.

어떤 물리적인 서버 위에 논리적으로 여러 컴퓨터를 두는 기술로, 하이퍼바이저를 두어 이 가상머신들을 관리한다.

가상머신들은 개별 컴퓨터처럼 동작하기 위해 각자 os 를 탑재하는데, 이 부분이 컨테이너 기술과의 큰 차이점이다.

<br>

### 컨테이너

가상머신들은 os 를 가지고 있지만, 컨테이너는 호스트 os 의 자원을 공유함으로써 컨테이너마다 따로 os 를 올리지 않아 가상머신에 비해 가볍다는 장점이 있다.

또한 **이미지**라는 것을 통해 컨테이너들을 똑같이 만들어내기 용이하다.

같은 이미지를 사용하여 컨테이너를 만들면, 컨테이너들 안에 설치되어있는 애플리케이션, 프로그램들이 동일한 환경으로 구성되어 있다.

우분투에 대한 파일시스템, 커널 등과 파이썬, 주피터 노트북 등을 잘 묶어서 이미지로 만들어 놓으면, 해당 이미지로 생성된 컨테이너들은 다 우분투에서 주피터 노트북을 동작시킬 수 있는 환경을 갖추게 되는 것이다.

마치 클래스를 한번 정의해놓고 객체를 생성하는 것과 비슷하다.



<br>

### 장점들

1. 이미지에 대해서만 관리하면 되기 때문에, 컨테이너들에 대한 일괄적인, 중앙집중적인 관리가 가능하다.
2. 서비스 규모를 늘려야 할 경우, 컨테이너만 생성해내면 되기 때문에 확장성이 좋다.
3. 개발, 배포, 테스트 서버에서 동일한 환경을 구축하는 것이 편리해진다.
4. 가상머신과는 다르게 os 가 올라가지 않아서 가볍다.

<br>

개발 환경을 구축하는 것이 제일 복잡하고 귀찮은 일이다.

데이터 분석을 하든, 서비스를 개발하든 실제로 코딩하기에 앞서 패키지 설치 및 의존 관계, 호환성 등을 모두 고려해야 한다.

개발 환경을 구축해서 프로그램을 완성시켰다고 하더라도, 수많은 배포 서버에도 동일한 환경을 구성하여 배포해야 하기 때문에, 이는 어려운 작업이 되지만, 도커가 이런 점을 잘 해결해준다.