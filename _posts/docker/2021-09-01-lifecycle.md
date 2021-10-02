---
layout: post
title: "[도커] 컨테이너의 라이프사이클(life cycle)"
subtitle: ""
categories: study
tags: docker
---

이미지를 가지고 컨테이너를 생성하고, 실행시키고, 종료하는 과정에서 변화하는 컨테이너의 상태를 ```라이프 사이클```이라고 한다.

아래는 컨테이너의 라이프 사이클을 잘 요약한 그림이다.

<figure style="display:block; text-align:center;">
  <img src="https://t1.daumcdn.net/cfile/tistory/99F72A3B5B7B7CB82E?download">
  <figcaption style="text-align:center; font-size:12px; color:#808080">
    https://0902.tistory.com/4
  </figcaption>
</figure>

<br>

### pull

우선 컨테이너를 생성하기 위해서는 이미지가 필요한데, 이는 ```pull```을 활용해 가져올 수 있다.

기본적으로 널리 사용되는 도커허브 레지스트리에서 이미지를 다운로드 받지만, 개인 레지스트리가 있을 경우 이미지명 뒤에 호스트를 명세해줌으로써 활용할 수 있다.

```docker images```를 사용하여 가지고 있는 이미지들을 확인 가능하다.

```bash
bconfiden2@bconfiden2:~$ sudo docker images
REPOSITORY                                   TAG       IMAGE ID       CREATED         SIZE
node                                         latest    1016313cda78   5 days ago      907MB
mysql                                        5.7       6c20ffa54f86   2 weeks ago     448MB
ubuntu                                       latest    1318b700e415   5 weeks ago     72.8MB
python                                       3.8.5     28a4c88cdbbf   11 months ago   882MB
```

이미지는 ```rmi 이미지명``` 명령어로 제거할 수 있다.

<br>

### create

이미지를 가져왔으면, 해당 이미지를 가지고 컨테이너를 생성한다. 이를 ```create```이라고 한다.

create 된 컨테이너는, 말 그대로 생성만 된 것이고 실제로 구동되고 있지는 않다. 그림에서 보듯이 create 이후에 컨테이너의 상태는 **Created** 되어 있다.

실행되었다가 종료된 컨테이너들(stopped)과, 만들어지고 한번도 시작된 적 없는 컨테이너(created)의 상태를 구분하기 위해 다르게 표시한다.

```bash
bconfiden2@bconfiden2:~$ sudo docker create ubuntu:latest
662259f48f6134d32a8ba5e468dcb13e85168df4c3bd098c5e4dc4e37f07d834

bconfiden2@bconfiden2:~$ sudo docker ps -a
CONTAINER ID   IMAGE                                        COMMAND                  CREATED         STATUS                     PORTS     NAMES
662259f48f61   ubuntu:latest                                "bash"                   3 seconds ago   Created                              inspiring_cartwright
```

<br>

### start

이렇게 생성된(혹은 실행되었다가 종료된) 컨테이너를 실행하는 것이 ```start```이다.

그러나 우분투 이미지를 가지고 생성한 컨테이너를 실행시킨 뒤, 프로세스를 확인해보면 Exited 되어있다.
```bash
bconfiden2@bconfiden2:~$ sudo docker start inspiring_cartwright
inspiring_cartwright
bconfiden2@bconfiden2:~$ sudo docker ps -a
CONTAINER ID   IMAGE                                        COMMAND                  CREATED      STATUS                     PORTS     NAMES
662259f48f61   ubuntu:latest                                "bash"                   2 days ago   Exited (0) 3 seconds ago             inspiring_cartwright
```

사실 컨테이너가 실행시킨다는 것은 COMMAND를 실행시킨다는 뜻으로, 여기서는 bash 를 실행시킨 뒤 bash 프로그램이 종료되면서 컨테이너도 정상적으로 종료된 것이다.

즉, 명령을 실행하고 해당 프로그램을 띄우는게 아닌 결과만 보여준다.

그렇기 때문에 우분투라는 컨테이너를 정말 어떤 우분투 서버처럼 접속해서 사용하고 싶다면 create 할 때 표준입출력과 쉘을 붙여주는 ```-i -t``` 옵션을 넣어줘야 한다.

```bash
# 컨테이너 생성 시 -it 옵션
bconfiden2@bconfiden2:~$ sudo docker create -it --name ubuntu_test ubuntu:latest
645bdabde6fe25f8a2b8c45c44cfd80210d663368e82f9a71d359d2e0176ed25
bconfiden2@bconfiden2:~$ sudo docker start ubuntu_test
ubuntu_test
# 컨테이너를 실행하니 Exited 가 아닌 Up 상태에 놓여있음
bconfiden2@bconfiden2:~$ sudo docker ps -a
CONTAINER ID   IMAGE                                        COMMAND                  CREATED          STATUS                    PORTS     NAMES
645bdabde6fe   ubuntu:latest                                "bash"                   20 seconds ago   Up 4 seconds                        ubuntu_test
```

<br>

### attach / detach

우분투 컨테이너 안에서 쉘과 표준입출력이 붙어 종료되지 않고 실행중에 있지만, 아직 컨테이너에 들어간 상태는 아니다. 들어가기 위해서 ```attach```를 사용한다.

```
bconfiden2@bconfiden2:~$ sudo docker attach ubuntu_test
# 컨테이너에 접속된 상태
root@645bdabde6fe:/#
```

컨테이너의 쉘에서 빠져나오고 싶다면, 터미널에 exited 를 입력해 종료할 수 있다. 

exited 로 빠져나올 경우, 컨테이너를 종료시키는 것이므로 만약 어떤 프로그램을 실행시켜놓았다면 같이 종료된다는 점에 주의해야 한다.

종료시키지 않고 다시 원래 쉘로 돌아오고 싶을 경우(detach)에는 *Ctrl + p, q* 를 누르면 된다.

쉘이 없는 컨테이너(백그라운드 등으로 실행시키는) 등에 쉘을 붙여서 접속할 때는 ```exec```을 사용한다. exec도 마찬가지로 -it 옵션을 주고, 실행시킬 쉘 프로그램(/bin/bash)를 넣어준다.

<br>

### stop / kill

실행중인 컨테이너를 중지하고 싶을 때에는 ```stop``` 혹은 ```kill```을 사용하는데, stop은 정상적으로 종료시키고, kill은 강제종료시킨다.

아래에서 test는 stop으로 종료시킨 반면 test2는 kill로 강제종료 시킨 컨테이너인데, Exited 값이 0 이 아닌 137 임을 확인할 수 있다.

```bash
bconfiden2@bconfiden2:~$ sudo docker ps -a
CONTAINER ID   IMAGE                                        COMMAND                  CREATED          STATUS                       PORTS     NAMES
3301676b21e3   ubuntu:latest                                "/bin/bash"              29 seconds ago   Exited (137) 4 seconds ago             ubuntu_test2
645bdabde6fe   ubuntu:latest                                "bash"                   10 minutes ago   Exited (0) 8 seconds ago               ubuntu_test
```

<br>

### rm

종료된(혹은 Created된 상태의) 컨테이너들은 완전히 사라진 것이 아니다.

그렇기 때문에 종료되어있는 컨테이너와 같은 이름의 컨테이너를 생성하려고 할 경우, 이름이 겹쳐 생성하지 못하는 에러가 자주 발생한다.

종료된 컨테이너들을 완전히 삭제(destroy)하고 싶을 때는 ```rm```을 사용한다.

실행 중인 컨테이너를 강제로 삭제하는 것은 권장사항은 아니지만, ```rm -f```처럼 -f 옵션을 주어 강제삭제를 시킬 수도 있다.