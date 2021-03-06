---
layout: post
title: "사용자 계정 비밀번호 관리"
tags: linux
---

사용자 계정의 비밀번호를 깜박했을 때는, 관리자 계정(```sudo 그룹```)을 통해 비밀번호를 바꿔야 한다.

비밀번호를 변경하기에 앞서서 비밀번호를 확인할 수 있는 방법에 대해 알아보았는데, 사용자 계정의 정보나 비밀번호를 관리하는 파일들이 있다고 한다.

<br>

## /etc/passwd

리눅스에 로그인할 때 사용되는, 사용자 계정의 정보를 가지고 있는 파일이다.

여러 정보들이 콜론 단위로 관리되며, ```사용자명 : 비밀번호(x) : uid : gid : 설명 : 홈디렉토리 : 실행 프로그램```과 같은 형태로 관리된다.

비밀번호 부분에는 암호화된 비밀번호를 저장했었지만, 현재는 그저 x 로 표시하고 아래에서 볼 /etc/shadow 에서 저장하고 있다.

아래와 같이 계정의 정보를 직접 확인해보면, 홈 디렉토리는 /home/bconfiden2 로, 실행 프로그램으로는 로그인 쉘인 배쉬쉘이 지정되어 있음을 확인할 수 있다.

```bash
bconfiden2@bconfiden2:~$ sudo cat /etc/passwd | grep bconfiden2
bconfiden2:x:1000:1000:bconfiden2,,,:/home/bconfiden2:/bin/bash
```

<br>

## /etc/shadow

```/etc/shadow```는, 사용자들의 암호화된 비밀번호들을 관리하는 파일이다.

암호화된 패스워드 및 계정의 유효 기간 등을 기록하고 있으며, ```사용자명 : 비밀번호(해시) : 최근 비밀번호 변경일 : 비밀번호 변경을 위한 대기일 수 : 유효기간 : 경고시간 : 유예기간 : 비밀번호 만료 이후 계정을 사용하지 못하게 되는 기간 : 0``` 와 같은 형태로 정보를 관리하고 있다.

```bash
bconfiden2@bconfiden2:~$ sudo cat /etc/shadow | grep bconfiden2
bconfiden2:$6$SiWEFQS9RJKvx3fy$3...어쩌구저쩌구:18840:0:99999:7:::
```

실제로 확인해보면 위와 같이 뜨는데, 처음의 bconfiden2 가 계정이름이 되고, 그 사이에 있는 괴랄한 문자열이 내 비밀번호에 대한 해시값이 된다.

다음의 18840은 최근 비밀번호 변경일로, 1970년 1월 1일을 기준으로하여 경과한 날짜이다.

비밀번호에 대해 유효기간 등을 따로 설정하지 않았기 때문에 나머지 값들은 모두 디폴트로 설정되었다.

<br>

## passwd

sudo 유저만이 접근할 수 있는 파일에서 비밀번호를 관리는 하지만 모두 암호화시켜서 저장하고 있기 때문에, 아무리 관리자라고 할지라도 비밀번호를 마음대로 확인할 수는 없다(~~당연한 얘기인듯~~).

따라서 비밀번호를 직접 변경시켜줘야 하는데, ```passwd``` 와 ```chage``` 등의 명령어가 있다.

둘은 패스워드에 대한 만료기간이나 정보 등을 설정하는 측면에서는 유사하지만, chage 는 비밀번호 자체를 변경할 수는 없다.

같은 기능일지라도 두 명령어의 옵션이 다르기 때문에, 일단은 그냥 passwd에 대해서만 봐둬도 괜찮을 듯 하다.

터미널에 ```passwd```만 입력할 경우에는 현재 로그인되어 있는 사용자의 비밀번호를 변경하게 되므로, 특정 사용자 계정의 비밀번호를 변경하고 싶을 때는 ```sudo passwd 사용자```처럼 사용해야 한다.

이외에도 다양한 옵션을 줄 수 있다.

```bash
-S : (대문자임) 사용자의 패스워드 정보를 출력(이렇게 볼 바엔 /etc/shadow 확인하자)
-l : 사용자가 패스워드로 로그인하지 못하게 lock
-u : 패스워드 로그인 잠금을 unlock
-e : 다음 로그인 시 반드시 패스워드를 변경하도록 강제
-x : 패스워드의 유효기간을 설정
-w : 만료 전에 경고해줄 날짜 설정
-i : 패스워드가 만료된 이후에 실제 로그인을 막기까지의 유예 기간에 대해 설정
```

관리자로써 다른 사용자의 비밀번호를 초기화 시켜줄 때, ```sudo passwd -e 사용자```처럼 비밀번호를 반드시 바꾸게끔 하는 것이 좋다.