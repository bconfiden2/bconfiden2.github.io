---
layout: post
title: "[도커] 컨테이너들을 독립적으로 구성하는 기술 - 리눅스 네임스페이스"
categories: devops
tags: docker
---

리눅스라는 운영체제는 크게 사용자 영역과 커널 영역으로 나눌 수 있는데, 이 중 커널이 모든 핵심을 차지한다고 할 수 있다.

커널은 사용자의 직접적인 접근을 제한하여, 시스템 콜 등의 요청에 맞게 하드웨어 자원들을 나눠주고 관리하는 영역이기 때문이다.

일반적인 리눅스 배포판들(Ubuntu, CentOS 등등)은 모두 리눅스 재단에서 관리하는 이러한 커널에 기반을 두고, 사용자 영역을 각자 다르게 가져가는 것 뿐이기 때문에 모두 리눅스인 것이다.

도커에서는 우분투 이미지를 사용하여 해당 컨테이너를 띄울 수도 있고, CentOS 이미지를 사용하여 띄울 수도 있다.

어떻게 이런 다양한 리눅스 배포판들을 하나의 호스트에서 다른 컨테이너로 실행시킬 수 있을까?

<br>

도커 컨테이너는 리눅스의 컨테이너 기술을 기반으로 하여 호스트OS 위에서 독립적인 프로세스로 실행되며, 호스트의 자원을 공유해 사용한다.

이러한 리눅스 컨테이너는 여러 기술들이 합쳐져 있는데, 그 중 namespace 라는 기술은 특정 시스템을 격리시키는 가상화 기술이다.

이 때 커널 영역을 격리시키는 것이 아닌 사용자 영역을 분리시키는 것으로, 실제로는 동일한 커널을 사용하는 상태에서 사용자 영역만을 가상화 시킨다.

일반적으로 도커 컨테이너와 비교되는 가상머신과의 차이점은 이것으로, 하이퍼바이저는 하드웨어를 가상화하는 반면에 컨테이너는 동일한 하드웨어(를 관리하는 커널) 위에서 사용자 영역의 실행 환경을 구분한다.

동일한 커널을 기반으로 하는 여러가지 리눅스 배포판들이 하나의 호스트 위에서 실행 가능한 이유가 이 때문이다.

컨테이너들이 사용하는 커널 영역은 동일하므로 그대로 가져가고, 배포판 별로 사용자 영역은 다르지만 이를 네임스페이스별로 가상화시켜서 사용자 영역을 독립적으로 가져가는 것이다.

호스트와 컨테이너들이 커널을 공유하고 있기 때문에, 호스트OS에서 커널에 대한 작업이 발생할 경우에는 도커 컨테이너들이 전부 영향을 받으므로 이런 점은 주의해야 한다.

<br>

리눅스 커널은 여러 네임스페이스들을 지원하는데, 그 중 도커가 사용하는 네임스페이스들은 아래와 같다.

- pid/pid_for_children : 프로세스 ID를 격리, 독립적인 프로세스 공간
- net : 네트워크 환경 분리, 중복 포트 바인딩 등의 네트워크 충돌 문제 방지
- uts : 호스트명 격리
- ipc : 프로세스들 간에 독립적인 ipc 확보
- mnt : 네임스페이스 간 독립적인 파일시스템 마운트

```ls -al /proc/[PID]/ns```로 특정 PID(프로세스)가 사용중인 네임스페이스들을 확인할 수 있다.

아래처럼 호스트 OS의 1번 프로세스(init)를 확인해보면, 앞서 언급됐던(도커에서 사용하는) 네임스페이스들 외에도 커널에서 지원하는 네임스페이스들까지 쭉 리스트업된다.

```bash
$ sudo ll /proc/1/ns
total 0
dr-x--x--x 2 root root 0  1월 29 07:17 .
dr-xr-xr-x 9 root root 0  1월 29 07:16 ..
lrwxrwxrwx 1 root root 0  1월 29 09:58 cgroup -> 'cgroup:[4026531835]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 ipc -> 'ipc:[4026531839]'
lrwxrwxrwx 1 root root 0  1월 29 07:17 mnt -> 'mnt:[4026531840]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 net -> 'net:[4026532008]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 pid -> 'pid:[4026531836]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 pid_for_children -> 'pid:[4026531836]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 time -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 time_for_children -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0  1월 29 09:58 uts -> 'uts:[4026531838]'
```

기본적으로 모든 프로세스들은 init의 자식으로 연결되기 때문에 네임스페이스가 전부 동일하다.

사용자가 실행한 프로세스의 경우에는 소유권이나 소유 그룹은 루트가 아니지만, 네임스페이스 값은 1번 프로세스와 같다.

```diff <(sudo ls -al /proc/[PID_1]/ns | awk -F":" '{print $3}') <(sudo ls -al /proc/[PID_2]/ns | awk -F":" '{print $3}')```처럼 두개 프로세스에 대해서 네임스페이스 값들이 같은지 diff를 활용하여 직접 확인해볼 수도 있겠다.

이런 상황에서 아무 컨테이너나 띄운 뒤, 컨테이너에서 1번 프로세스를 확인해보자.

```bash
$ sudo docker run -it ubuntu:20.04
root@c38bfbaca17d:/$ ls -al /proc/1/ns
total 0
dr-x--x--x 2 root root 0 Jan 29 01:31 .
dr-xr-xr-x 9 root root 0 Jan 29 01:30 ..
lrwxrwxrwx 1 root root 0 Jan 29 01:31 cgroup -> 'cgroup:[4026531835]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 ipc -> 'ipc:[4026533613]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 mnt -> 'mnt:[4026533611]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 net -> 'net:[4026533616]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 pid -> 'pid:[4026533614]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 pid_for_children -> 'pid:[4026533614]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 time -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 time_for_children -> 'time:[4026531834]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0 Jan 29 01:31 uts -> 'uts:[4026533612]'
```

도커에서 사용하는 네임스페이스들(ipc, mnt, net, pid, pid_for_children, uts)에 대해서 호스트OS의 네임스페이스와 분리된 것을 볼 수 있다.