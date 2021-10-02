---
layout: post
title:  "[도커] Ubuntu 20.04 에 간단하게 도커 설치하기"
subtitle:  "docker"
categories: study
tags: docker
---

사실 apt 로 key 추가하고, 저장소 업데이트 하고, 다시 또 뭘 다운 받는 복잡한 과정을 거칠 필요 없이, 아래의 코드 한줄이면 누군가가 잘 만들어놓은 스크립트가 다운로드를 전부 대신 해준다.

{% highlight bash %}
curl -fsSL https://get.docker.com/ | sudo sh
{% endhighlight %}

다만 ubuntu 나 centos 가 아닌 다른 리눅스일 경우에는 위의 과정들을 통해 직접 설치해야 한다.

[공식 문서](https://docs.docker.com/engine/install/debian/)를 따라하면 어렵지 않을?지도?

<br>

터미널에서 열심히 다운로드를 완료하면, 도커가 잘 설치되었는지 확인한다.

{% highlight bash %}
sudo docker version
{% endhighlight %}

<br>

정상적으로 설치되었다면 아래와 비슷한 결과가 출력된다.
{% highlight bash %}
Client: Docker Engine - Community
 Version:           20.10.7
 API version:       1.41
 Go version:        go1.13.15
 Git commit:        f0df350
 Built:             Wed Jun  2 11:56:38 2021
 OS/Arch:           linux/amd64
 Context:           default
 Experimental:      true

Server: Docker Engine - Community
 Engine:
  Version:          20.10.7
  API version:      1.41 (minimum version 1.12)
  Go version:       go1.13.15
  Git commit:       b0f5bc3
  Built:            Wed Jun  2 11:54:50 2021
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.4.9
  GitCommit:        e25210fe30a0a703442421b0f60afac609f950a3
 runc:
  Version:          1.0.1
  GitCommit:        v1.0.1-0-g4144b63
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
{% endhighlight %}