---
layout: post
title:  "[리눅스] Wine 으로 카카오톡 설치하기"
subtitle:  ""
categories: devops
tags: linux
---

카카오톡은 공식적으로 윈도우와 맥만 지원하고 있기 때문에, 리눅스에서 사용하려면 Wine 과 같은 프로그램이 필요하다.

[Wine 을 설치](https://bconfiden2.github.io/study/2021/08/12/wine/)했으므로, 카카오톡을 Wine 을 사용해 설치해보자. ~~분명 수요가 꾸준히 있을텐데 왜 안 만드는지 모르겠다 진짜..~~

<br>

## 카카오톡 설치

우선 카카오톡 홈페이지에 들어가 **.exe 파일** 을 다운로드 받는다.

아래 명령어를 통해 카카오톡 한글 버전을 설치한다. 물론 exe 파일이 존재하는 경로를 넣어주는 건 기본.
```bash
LANG="ko_KR.UTF-8" wine KakaoTalk_Setup.exe
```

설치가 다 돼서 실행시켜봤는데 여전히 한글이 깨져서 나오면, ```~/.local/share/application/wine/Programs/카카오톡``` 경로로 들어간다.

```bash
cd ~/.local/share/application/wine/Programs/카카오톡
vi 카카오톡.desktop

# Exec=env WINEPREFIX="/home/name/.wine" wine C:\\\\ 어쩌구저쩌구로 되어 있을 텐데,
# Exec=env WINEPREFIX="/home/name/.wine" LANG="ko_KR.UTF-8" wine C:\\\\ 로 바꾼 뒤 저장.
```

<br>

## 방화벽 설정

카카오톡을 설치해서 한국어로 실행까지 잘 되는 모습을 확인하면 기분이 좋아지지만, 바로 로그인에서 에러가 발생한다.

바로 ```(오류코드: 50114) FriendList``` 이다.

카카오톡 서버 요청을 하여 응답을 받아오는 과정에서 우리 ~~킹갓리눅스~~가 컴퓨터를 지키기 위해 차단을 시키는 모양이다.

```sudo ufw enable``` 로 방화벽을 켜준 뒤, 아래 명령어를 통해 포트와 아이피들(*카카오톡 측에서 답변해준*)을 허용해주자.

```bash
sudo ufw enable

sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 995
sudo ufw allow 8080
sudo ufw allow 5223
sudo ufw allow 9282
sudo ufw allow 10000
sudo ufw allow 10001
sudo ufw allow 10002
sudo ufw allow 10003
sudo ufw allow 10004
sudo ufw allow 10005
sudo ufw allow 10006
sudo ufw allow 10007
sudo ufw allow 10008
sudo ufw allow 10009

sudo ufw allow from 210.103.248.0/21
sudo ufw allow from 203.133.160.0/19
sudo ufw allow from 113.29.128.0/18
sudo ufw allow from 103.27.148.0/23
sudo ufw allow from 61.251.98.128/25
sudo ufw allow from 203.238.180.0/24
sudo ufw allow from 203.246.172.0/24
sudo ufw allow from 203.217.224.0/19
sudo ufw allow from 110.76.140.0/22
sudo ufw allow from 103.246.56.0/22
sudo ufw allow from 1.201.0.0/21
sudo ufw allow from 210.103.240.0/21
sudo ufw allow from 27.0.236.0/22
sudo ufw allow from 211.231.96.0/20
sudo ufw allow from 139.150.0.0/21
sudo ufw allow from 219.249.189.0/24
sudo ufw allow from 219.249.190.0/24
sudo ufw allow from 219.249.210.0/24
sudo ufw allow from 219.249.213.0/24
sudo ufw allow from 219.249.216.0/24
sudo ufw allow from 219.249.226.0/23
sudo ufw allow from 219.249.231.0/24
```

로그인이 잘 된다!