---
layout: post
title:  "ssh config options"
subtitle:  ""
categories: study
tags: linux
---

ssh 를 통해 원격 호스트에 접속할 때 옵션들을 다양하게 설정할 수 있다.

예를 들어 ssh key 를 사용할 경우 ```-i keyname``` 을 붙이고, 포트번호는 ```-p 1234``` 처럼 붙이고, 사용자 이름, 터널링 등등 한번 접속하기 위해 많은 옵션들이 필요할 때도 있다.

동일한 명령어로 자주 접속하는 서버가 있을 경우에는 ```history | grep KEYWORD```를 통해 히스토리에서 찾아 접속할 수 있겠지만, 이마저도 귀찮아질 때는 config 파일을 통해 더욱 편하게 관리할 수 있다.

<br>

## ssh config

ssh 접속을 관리하는 config 파일은 ```~/.ssh/config```에 존재한다.

파일 내용은 일반적으로 아래와 같은 형태로 구성된다.
```bash
Host hostname
    SSH_OPTION value
    SSH_OPTION value

Host hostname2
    SSH_OPTION value
    SSH_OPTION value
    SSH_OPTION value

# --Example--
Host 단축명령어
    HostName 원격호스트
    User 사용자계정
    Port 포트번호
    IdentityFile SSH키
    LocalForward 1234 localhost:1234
```

즉 ```ssh 사용자계정@원격호스트 -p 포트번호 -i SSH키 -L 1234:localhost:1234``` 처럼 썼던 명령어를, config 파일을 설정해놓음으로써 ```ssh 단축명령어```처럼 줄여서 사용하게 할 수 있는 것이다.

하둡서버에서 돌아가는 잡이나 노드 상태를 보기 위해서 서버의 8088 이나 9870 같은 포트에 터널링을 매번 해줘야 했는데, config 파일을 통해 아주 간편하게 접속할 수 있게 됐다.

Example 외에 다양한 다른 옵션들에 대해서는 [SSH_CONFIG 의 Man page](https://nxmnpg.lemoda.net/ko/5/ssh_config)를 참고하자.

<br>

## Patterns

Host 부분에 와일드카드 등의 패턴을 사용함으로써 그 패턴에 해당되는 호스트들에게 동일한 세팅을 해줄 수 있다.

예를 들어 *server1, server2, server3* 라는 호스트에, 전부 같은 SSH키와 4444 포트를 사용해서 접속한다고 할 때, 아래처럼 ```*```을 사용해서 한방에 전달해줄 수 있다. ```*```은 모든 것에 매칭되는 표현이다.
```bash
Host server*
    Port 4444
    IdentityFile SSH키
```

이외에도 ```?``` 는 한개의 문자에만 매칭된다. 예를 들어 ```10.0.0.?``` 의 경우는 ```10.0.0.0 ~ 10.0.0.9```에만 매칭된다.

```!``` 는 느낌표 뒤에 오는 표현을 탐색에서 제외시킨다. 예를 들어 ```10.0.0.? !10.0.0.1```는 ```10.0.0.[0-9]``` 에서 5를 제외한 나머지들에게만 매칭된다.

<br>

이렇게 config 파일에 명시해서 사용하는 방식의 장점 중 하나가, **각 접속마다 다른 ssh 키들을 사용** 할 때 편리해진다는 것이다.

해당 호스트의 IdentityFile 에다가 ssh-key 를 매칭시켜주면 되기 때문에, 어느 서버에 어떤 키를 사용해서 접속할 지 외우고 있을 필요가 없다.

다만 이런 ssh 접속을 설정하는 config 파일은 중요한 정보들이 들어있을 수 있기 때문에, 시스템의 다른 사용자들이 읽을 수 없도록 ```chmod 440 ~/.ssh/config```와 같이 권한에 제약을 두어야 한다. ~~대부분은 .ssh 디렉토리 자체에 권한 제약이 걸어두긴 하지만..~~

<br>

## /etc/ssh/ssh_config 와의 차이

/etc/ssh 아래에도 ssh_config 라는 파일이 존재하는데, 이는 시스템 전체에서의 설정 파일이고 우리가 지금껏 수정한 ~/.ssh/config 는 사용자의 설정 파일이다.

ssh 접속을 할 때 ```-v``` 옵션을 주어서 자세히 확인해보면, 아래처럼 ```$HOME/.ssh/config``` 를 먼저 읽은 뒤 ```/etc/ssh/ssh_config``` 파일을 참조하는 것을 볼 수 있다.
```
OpenSSH_8.2p1 Ubuntu-4ubuntu0.2, OpenSSL 1.1.1f  31 Mar 2020
debug1: Reading configuration data /home/bconfiden2/.ssh/config
debug1: /home/bconfiden2/.ssh/config line 6: Applying options for OOOO
debug1: Reading configuration data /etc/ssh/ssh_config
...
```