---
layout: post
title: "도커파일 - 깃헙 블로그 구성하는 jekyll Dockerfile"
tags: docker
---

깃헙 블로그를 위한 ruby, jekyll, bundler 등 의존성을 맞추는 일이 생각보다 귀찮다.

어느 컴퓨터에 잘 세팅해놨다고 하더라도, 다른 컴퓨터에 새로 다운받아 포스팅 할 일이 있으면 다시 처음부터 세팅을 해줘야 한다.

매번 설치하기 번거로운 것 같아서, 아예 Dockerfile 을 통해 이미지를 하나 만들고, 블로그를 실행시킬 때 컨테이너를 생성해서 그 위에서 돌리게 하려고 한다.

도커파일은 다음과 같다.

```Dockerfile
FROM ubuntu:20.04

ENV LC_ALL C.UTF-8

RUN mkdir /blog
WORKDIR /blog

RUN apt-get update
RUN apt-get install -y ruby-full libffi-dev ruby-dev make gcc build-essential
RUN gem install jekyll bundler:1.17.2 

COPY Gemfile /blog
COPY Gemfile.lock /blog
RUN bundle install
RUN rm /blog/Gemfil*

EXPOSE 4000

CMD ["bundle","exec","jekyll","serve","--host","0.0.0.0"]
```

우선 기본적으로는 우분투 20.04 버전을 기반으로 한다.

도커허브 저장소에 지킬에서 공식적으로 올린 이미지가 있는 것 같지만(jekyll/jeykll:pages), 내가 보기 편하게 만드는 것이 좋을 것 같아서 직접 만들었다.

루트 아래에 /blog 라는 디렉토리를 만들어준 뒤, 작업 경로로 설정해준다.

컨테이너를 실행시킬 때 해당 위치에 볼륨을 붙여줄 것이기 때문에, 이 경로 안에서 gem 패키지들을 다 설치해줘야 한다.

먼저 apt 로 루비와 각종 패키지를 설치해준 뒤, 기본적으로 지킬과 번들러를 gem 으로 설치해준다.

또한 현재 내 블로그를 띄우기 위해 필요한 다른 Gemfile 들도 설치해줘야하기 때문에, 호스트OS에 있는 파일들을 복사해와서 bundle install 로 싹 깔아준다.

마지막으로, 4000번 포트를 개방해주고 컨테이너를 실행시킬 때 포워딩을 꼭 해주도록 한다.

여기까지만 하면 기본적인 것은 다 되지만, jekyll serve 시 인코딩 문제가 밑도끝도 없이 발생하기 때문에, 꼭 ```ENV LC_ALL C.UTF-8```을 넣어주자.

또한 기본적으로는 ```localhost``` 에서 띄워져 호스트에서도 접근이 안되므로, 모든 아이피를 허용해주는 ```--host 0.0.0.0``` 을 추가해서 실행해야 한다.