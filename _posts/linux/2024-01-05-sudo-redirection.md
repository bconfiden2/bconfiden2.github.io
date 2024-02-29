---
layout: post
title: "sudo 권한이 필요한 위치에 redirection 하기"
tags: linux
---

표준출력의 결과물을 redirection 하여 파일로 보내고 싶지만, 해당 파일이 루트 권한으로만 접근 가능한 경우에 아래와 같이 실행하면 에러가 발생한다.

```
bconfiden2@h02:~$ sudo echo test > /etc/testfile
-bash: /etc/testfile: Permission denied
```

이는 echo test 라는 명령어를 sudo로 실행한 것이지, redirection에 sudo로 실행한 것이 아니기 때문이다.

쉘에서는 redirection을 수행하기 위해 자식 프로세스를 생성하여 넘겨주는 것이기에, 부모 프로세스에 적용된 sudo와는 무관하다.

그렇다고 ```echo test > sudo /etc/testfile``` 이런 식의 말도 안되는 구조를 가질 수는 없기 때문에,

sudo 권한을 가지는 쉘을 실행시킨 뒤 해당 쉘에 재지정까지의 명령어를 실행하도록 하면 된다.

```
bconfiden2@h02:~$ sudo bash -c 'echo test > /etc/testfile'
bconfiden2@h02:~$ cat /etc/testfile 
test
```

또는, 앞의 표준출력을 파이프로 넘겨준 뒤, tee 명령어를 sudo로 실행시키는 방법도 있다.

```
bconfiden2@h02:~$ echo test | sudo tee /etc/testfile
test
```