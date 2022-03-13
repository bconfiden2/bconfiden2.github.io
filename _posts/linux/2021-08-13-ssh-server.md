---
layout: post
title:  "ssh 서버 구축하기"
subtitle:  ""
categories: devops
tags: linux
---

ssh는 **S**ecure **SH**ell 의 약자로, 보안 기능이 담긴 원격 접속 프로토콜이다.

우리는 각종 서버에 접속하기 위해서 우리의 로컬 데스크톱(노트북)에서 ssh 를 통해 서버에 접속한다.

이 때 로컬 컴퓨터에는 ssh 클라이언트 프로그램이, 서버 컴퓨터에는 ssh 서버 프로그램이 동작하고 있기 때문에 통신이 이루어진다.

그러나 꼭 서버컴퓨터가 아니더라도 연구실의 데스크톱을 24시간 켜놓고 ssh 서버를 돌려놓으면, 집에 와서도 ssh 로 접속할 수 있기 때문에 편리하다.

<br>

ssh 서버는 ```sudo apt-get install openssh-server```로 간단하게 설치할 수 있다.

설치를 한 뒤에는 ssh 가 응답할 포트번호를 열어주어야 하는데, 널리 쓰이는 ```22```번을 그대로 쓰는 것은 추천하지 않기 때문에 ```/etc/ssh/sshd_config```에서 포트 번호를 다른 어떤 값으로 바꿔주는 것이 좋다.

```bash
sudo vi /etc/ssh/sshd_config

# 아래 코드를 찾아 주석을 풀어준 뒤, 포트번호를 바꿔준다.
Port 22
```

포트 번호를 바꿔줬다면, 외부에서 해당 포트로 통신을 시도할 때 인바운드로 해당 포트가 허용되어있지 않다면 방화벽에 의해 막히게 된다.

**$PORT**-바꿔준 포트번호-를 방화벽에서 허용해주도록 하자.
```bash
sudo ufw enable
sudo ufw allow $PORT
```

포트번호를 바꿔준 뒤 ```sudo systemctl restart sshd```를 통해 ssh 서버를 재시작 시켜주면, 다른 컴퓨터에서 해당 포트번호로 ssh 접속이 가능하다.