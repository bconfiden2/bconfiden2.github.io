---
layout: post
title: "Github에 ssh-key 등록하기"
tags: git
---

2021년 8월 13일부터 비밀번호를 이용한 인증을 지원하지 않는 대신, 액세스 토큰을 활용해야 한다.

즉 아래처럼 web URL을 통해 푸시하는 경우 아이디와 비밀번호를 입력하는 것이 아니라, 원격 깃허브에서 Personal Access Token 을 발급받아 사용해야하는데, 이런 과정이 너무 귀찮다.

```bash
bconfiden2@h02:~/bconfiden2.github.io$ git remote -v
origin	https://github.com/bconfiden2/bconfiden2.github.io (fetch)
origin	https://github.com/bconfiden2/bconfiden2.github.io (push)

bconfiden2@h02:~/bconfiden2.github.io$ git push origin master
Username for 'https://github.com': bconfiden2
Password for 'https://bconfiden2@github.com':
remote: Support for password authentication was removed on August 13, 2021. Please use a personal access token instead.
remote: Please see https://github.blog/2020-12-15-token-authentication-requirements-for-git-operations/ for more information.
fatal: Authentication failed for 'https://github.com/bconfiden2/bconfiden2.github.io/'
```

대신 ssh key를 등록해놓으면, 매번 액세스 토큰이나 비밀번호 등을 입력하지 않고도 인증 과정을 통과할 수 있어서 편리하다.

<br>

우선 자신의 로컬 머신에서 ssh key를 생성해야 한다.

기존에 사용하던 키가 있으면 굳이 만들 필요 없고, 없다면 ```ssh-keygen```으로 간단하게 만들 수 있다.

```bash
bconfiden2@h02:~$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/bconfiden2/.ssh/id_rsa): /home/bconfiden2/.ssh/my_key
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/bconfiden2/.ssh/my_key
Your public key has been saved in /home/bconfiden2/.ssh/my_key.pub
The key fingerprint is:
SHA256:N3c6W7Wp5L5tDT7JwXU7XFHq4e7kva/s2clVM4Q9Ax4 bconfiden2@h02
The key's randomart image is:
+---[RSA 3072]----+
|             E  o|
|            . =o |
|             oo=.|
|             o..*|
|        S o ..=+*|
|         . o ++=*|
|            o++*+|
|            oOO=+|
|            o*XB*|
+----[SHA256]-----+
```

맨 처음에 사용자가 만들 키를 저장할 위치를 물어보는데, 기본적으로는 홈디렉토리의 .ssh 아래에 id_rsa 라는 이름으로 지정되지만 바꾸고 싶은 경우 자신이 원하는 곳에 위치시키면 된다.

뒤에서 참조해야하기 때문에 경로는 기억하고 있어야 한다.

나의 경우는 이미 같은 경로에 id_rsa 라는 이름의 ssh key 를 만들어놓고 사용중이었기 때문에, 지금은 my_key 라는 이름으로 저장했다.

ssh-keygen 과정에서 두번째로 물어보는 passphrase의 경우에는, 비밀번호를 입력하여 키를 사용할 때 추가적인 인증과정이 붙어 더 안전하지만, 매번 비밀번호를 입력하기가 귀찮을 것 같다면 공백으로 두고 그냥 넘어가도 무방하다.

```bash
bconfiden2@h02:~$ ls ~/.ssh
id_rsa  id_rsa.pub  my_key  my_key.pub
```

my_key라는 개인키와, my_key.pub 이라는 공개키 한 쌍이 생성된 것을 확인할 수 있다.

<br>

사용할 ssh key가 준비되었으면 Github에 들어가서 키를 등록해준다.

우상단에 있는 프로필에서 세팅에 들어가면,

<img src="https://user-images.githubusercontent.com/58922834/215728107-e0d7a9a9-54c1-4076-a269-fa9a0b3d65a7.png">
<br>

좌측 사이드바에 ```SSH and GPG keys``` 탭이 있는데, 해당 탭에서는 현재 자신이 등록해놓은 키들을 확인할 수 있으며, New SSH key 버튼을 클릭하면 아래와 같은 화면이 나온다.

<img src="https://user-images.githubusercontent.com/58922834/215728140-4740b350-1419-4125-8cb6-991ae019a229.png">
<br>

Title 항목에는 자신이 식별할 이름을 임의로 지정하여 넣어준다.

Key 부분에는 앞서 만들어놨던 ssh key의 공개키(일반적으로 [keyname].pub 파일)의 값을 넣어줘야하므로, cat 을 통해 확인한다.

```bash
bconfiden2@h02:~$ cat ~/.ssh/my_key.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCvpl5muEfet7OFB7MU4umnunJWghJBYjMZs+yZJ6IvvGGPTUI8tqyS5+YD/VEwQeECMYwyf3xAJ5C0j0XN80yXLiUQx2c+PbStuhBpZd5Jo0DlejNqUgKAe8nSSU7kV++6cQf7mnKpQbZoRQUyGxaP8kp2inN/i6A4Qkaz3aX3od7fRfaQsF5w9uw7AbfCsn8BzHvXs+/A7H4V7w4NIbDpJhD+Y/2Ts6W8fFesdXOZtuYvId7/7BaPC4olxNLIPLnLw9wTOE9plUZVO7YvrHUzIsPsDU9sCYrHnqHfSPvLVaAl5rE81/OlxbpIPrvRpmpy+HHIbAOZl+aNT1oD+jAMGxbViI7WK0PYRuZGH1nm7vBJTiHopQ/pUWav3dNm261asxBIFuRDfpf5e/dlWv0JvkI7CsUzkw5AAsmnD5vmh2y12C9r06j2IjEXQ8frBWDaS/KDOpn+VAmh0CSP+BCbWJkXe4m9V4zrskx85EU0IXC5bRyUCWy3yS3LmPsxjWM= bconfiden2@h02
```

이 때, 맨 마지막에 있는 불필요한 공백 등이 추가될 경우 제대로 인증되지 않을 수 있으니 주의해서 복사한다.

또한 공개키가 아닌 개인키(.pub 이 붙지 않은 파일)를 넣지 않도록 주의해야 한다.

<br>

깃헙에 ssh key 등록까지 마쳤으면, 내 로컬 컴퓨터가 깃헙의 서버와 ssh 통신이 정상적으로 이루어지는지 확인하기 위해 ```ssh -T git@github.com```으로 테스트한다.

일반적으로는 아래처럼 메시지 한줄을 출력해주고 정상적으로 종료되어야 하지만,

```bash
bconfiden2@h02:~$ ssh -T git@github.com
Hi bconfiden2! You've successfully authenticated, but GitHub does not provide shell access.
```

간혹 응답 없이 무한정 대기를 타고 있는 경우가 있다.

이 경우 ssh config 파일을 수정하여 github.com 과 통신할 때의 설정들을 세팅해준다.

```bash
bconfiden2@h02:~$ vi ~/.ssh/config
Host github.com
    HostName ssh.github.com
    Port 443
    IdentityFile ~/.ssh/my_key
    User git
```

호스트명과 사용자, 포트는 동일하게 설정해주고 IdentityFile 부분에만 자신이 등록해놨던 키의 경로를 넣어준 뒤 저장하면, 정상적으로 깃헙 서버가 메시지를 응답해주는 걸 확인할 수 있다.

이 과정까지 마치면 원격 레포에 푸시하는 등의 작업에서 추가적인 인증 과정을 거치지 않아도 된다.

이를 확인하기 위해 앞서 https 로 등록되어있던 origin 을, ssh 기반 URI 로 변경해준다.

```bash
bconfiden2@h02:~/bconfiden2.github.io$ git remote set-url origin git@github.com:bconfiden2/bconfiden2.github.io.git

bconfiden2@h02:~/bconfiden2.github.io$ git remote -v
origin	git@github.com:bconfiden2/bconfiden2.github.io.git (fetch)
origin	git@github.com:bconfiden2/bconfiden2.github.io.git (push)
```

```bash
bconfiden2@h02:~/bconfiden2.github.io$ git push
Everything up-to-date
```

원격 레포에 ssh 프로토콜을 사용하여 접근하기 때문에 맨 앞에서와 같이 사용자명과 비밀번호 입력 칸이 나오지 않고 등록된 ssh key를 통해 바로 인증이 된다.