---
layout: post
title: "도커 이미지를 파일로 저장한 뒤 원격지 서버로 복사하기"
tags: docker
---

인터넷 연결이 되지 않는(보안이 철저한) 서버에다가 도커 이미지를 올려서 실행시켜야 하는 경우가 있다.

아무리 도커파일을 만들어서 이미지를 빌드한다고 하더라도, 베이스 이미지가 없거나, 빌드 과정에서 패키지를 설치할 때 인터넷이 필요할 일이 많다.

이럴 때는 로컬 환경에서 빌드한 뒤, 원격지 서버로 파일을 복사하는 과정이 필요하다.

우선 현재 빌드되어있는 이미지를 파일로 저장하는 명령어는 아래와 같다.

```bash
bconfiden2@h01:~$ docker images
REPOSITORY              TAG         IMAGE ID       CREATED         SIZE
ubuntu                  20.04       54c9d81cbb44   2 months ago    72.8MB
nvidia/cuda             11.0-base   2ec708416bb8   20 months ago   122MB
centos/systemd          latest      05d3c1e2d0c1   3 years ago     202MB
```
```bash
bconfiden2@h01:~$ docker save -o filename ubuntu:20.04
bconfiden2@h01:~$ ll | grep filename
-rw-------  1 root       root         75163136 Apr 23 09:01 filename
```

```docker save``` 명령어로 도커 이미지를 파일로 저장하면, -o 옵션에 넣어준 파일명으로 이미지가 저장되며, 크기는 도커 이미지의 사이즈와 동일함을 확인할 수 있다.

현재는 도커를 루트 권한으로 실행시키고 있기 때문에, 해당 파일의 소유자와 그룹이 둘 다 루트로 설정된 것이다.

이렇게 이미지를 파일로 저장했으면, 단순히 이 파일을 원격지에 알아서 잘 옮겨주면 된다.

USB 를 활용하든지, 같은 네트워크에 속해있다면 네트워크를 통해 복사를 할 수도 있겠다.

복사해가는 과정에서는 파일의 크기가 작으면 작을수록 더 좋으므로 파일을 압축하여 전송하는 것도 좋다.

```bash
bconfiden2@h01:~$ ls -alh | grep filename
-rw-------  1 root       root        72M Apr 23 09:01 filename
bconfiden2@h01:~$ gzip -v9 filename
filename:	 63.4% -- replaced with filename.gz
bconfiden2@h01:~$ ls -alh | grep filename
-rw-------  1 root       root        27M Apr 23 09:01 filename.gz
```

gzip의 압축률을 최대로(-9) 주거나 애초에 압축률이 높은 xz 등을 활용하면, 위에서 볼 수 있듯이 더 작은 파일로 복사가 가능하다.

원격지로 압축된 파일을 복사한 뒤에는, 아래처럼 압축을 풀어준 뒤 ```docker load```를 사용하여 로드해주면 끝난다.

```bash
bconfiden2@h02:~$ gzip -d filename.gz
bconfiden2@h02:~$ ls -alh | grep filename
-rw-------  1 root       root        72M Apr 23 09:01 filename
```
```bash
bconfiden2@h02:~$ docker load -i filename
Loaded image: ubuntu:20.04
```

우분투 이미지를 구성하는 레이어들이 기존에 남아있어서 그런지 원래 없는지는 잘 모르겠지만, 이미지를 로드할 때는 아래처럼 포함된 레이어들이 하나씩 로드되는 과정을 볼 수도 있다.

```bash
bconfiden2@h02:~$ docker load -i test
36ffdceb4c77: Loading layer [==================================================>]  75.15MB/75.15MB
97203822015f: Loading layer [==================================================>]  2.048kB/2.048kB
215cf81b7ba8: Loading layer [==================================================>]  97.26MB/97.26MB
a42f7d89ced4: Loading layer [==================================================>]  197.6kB/197.6kB
cc0e2ab85d95: Loading layer [==================================================>]   2.56kB/2.56kB
f3b2a2c4382a: Loading layer [==================================================>]   2.56kB/2.56kB
c3829955e380: Loading layer [==================================================>]   5.12kB/5.12kB
Loaded image: tmp:1.0
```