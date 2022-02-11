---
layout: post
title: "[하둡] 하둡 클러스터를 위한 커널 파라미터와 파일시스템 최적화 방법"
categories: bigdata
tags: hadoop
---

하둡을 설치할 때는 하둡의 특성에 맞는 운영체제의 튜닝이 필요한데, 그들 중 커널 파라미터와 파일시스템에 대한 최적화 방법들이 몇가지가 있다.

<br>

### vm.swappiness

우선 커널의 여러 파라미터들 중 디스크 스왑과 관련된 vm.swappiness 파라미터는, 메모리에 있는 데이터들을 디스크로 얼마나 자주 스왑할지에 대한 정보이다.

swappiness 값의 범위는 0 ~ 100 으로, 0일 경우에는 디스크에 스왑하지 않겠다는 의미가 된며, 값이 높으면 높을수록 메모리에 여유 공간이 있다고 할지라도 메모리의 데이터를 디스크에 스왑한다.

하둡 대몬에서 발생하는 데이터들을 디스크로 스왑하게 될 경우에는 문제가 발생할 수도 있을 뿐만 아니라 디스크 I/O 도 그만큼 높아진다.

일반적으로 많은 리눅스 배포판들에서 vm.swappiness 의 디폴트 값은 60 정도가 되는데, 이 값들에 대해서는 아래처럼 확인할 수 있다.

```bash
bconfiden2@DESKTOP:~$ sysctl vm.swappiness
vm.swappiness = 60
bconfiden2@DESKTOP:~$ cat /proc/sys/vm/swappiness
60
```

해당 파라미터값을 변경하는데는 다른것들과 비슷하게 재부팅시 초기화되는 방법과 설정파일을 수정하여 영구적으로 변경하는 방법이 있는데, 우선 즉시 변경하는 방식으로는 위에서 확인한 명령어와 비슷하게 설정 가능하다.

혹은 /etc/sysctl.conf 파일에서 속성값을 명시하여 부팅 시에 읽어들이게 할 수 있다.

파일을 수정한 뒤에 재부팅 없이 바로 시스템에 적용시키고 싶을 경우에는 sysctl.conf 파일을 수동으로 다시 읽어들이게끔 명령 내려줘야 한다.

```bash
bconfiden2@DESKTOP:~$ sudo sysctl vm.swappiness=20
vm.swappiness = 20

bconfiden2@DESKTOP:~$ sudo vi /etc/sysctl.conf
vm.swappiness=20
bconfiden2@DESKTOP:~$ sudo sysctl -p
```

swappiness 를 0 혹은 1로 설정하여 과도한 디스크 I/O 나 장애 발생에 대비할 수 있다.

<br>

### LVM

하둡은 기본적으로 디스크I/O가 많이 발생하며, 데이터노드는 파일시스템에 블록들을 저장하기 때문에 파일시스템들에 대한 설정이 하둡의 성능에 영향을 준다.

우선 데이터노드로 사용할 디스크들에 대해서는 LVM을 사용하면 안된다.

파일시스템과 실제 물리 디바이스 사이에 LVM과 같은 추가적인 계층이 하나 더 포함돼있을 경우 I/O 성능은 더 떨어지기 때문이다.

뿐만 아니라 LVM 특성상 여러 디바이스들을 하나의 디바이스처럼 구성하기 때문에, 여러 디스크들 중 하나라도 장애가 발생시 다른 디스크들도 사용하지 못하게 된다.

<br>

### Reserved block

ext 기반의 파일시스템에서는 루트 사용자를 위한 블럭을 일정 부분 확보해놓는다.

디스크가 가득 차는 등의 상황에서는 일반적으로 작업 수행이 어렵기 때문에 루트로 접속하여 처리할 수 있게 해놓는 것인데, 이러한 예비 블럭에 해당하는 공간을 축소시킴으로써 더 효율적으로 사용이 가능하다.

이러한 예비 블록의 크기는 일반적으로 약 5퍼센트 정도이며, 아래와 같이 확인할 수 있다.

```bash
bconfiden2@DESKTOP:~$ sudo tune2fs -l [장치명] | grep -i "Block count"
Block count:              62383360
Reserved block count:     3119168

bconfiden2@DESKTOP:~$ sudo tune2fs -m1 [장치명]
tune2fs 1.45.5 (07-Jan-2020)
Setting reserved blocks percentage to 3% (1871500 blocks)
```

예약 공간의 비율을 설정하는 명령어도 tune2fs 에서 제공하며, -m 옵션 뒤에 비율 값을 넣어줌으로써 해당 퍼센테이지만큼의 블록들만 예약하게끔 설정 가능하다.

혹은 -r 옵션으로 전체 블록들 중의 비율이 아닌, 블록 크기의 절대값으로도 지정할 수 있다.

<br>

### noatime mount

일반적으로 파일시스템을 마운트하면, 디폴트로 파일이나 디렉토리의 접근 시간(atime)을 관리하는 기능이 포함된다.

접근 시간에 대한 정보는 최근에 변경되었거나 읽어간 파일에 대해 쉽게 알아볼 수 있게 해주지만, 하둡이나 hdfs 에서는 이러한 접근 시간에 대한 정보는 굳이 알 필요가 없다.

```man -s 2 stat```의 stat 구조체를 확인해보면 timespec 타입의 st_atimespec 값을 확인할 수 있는데, 파일을 읽게 되면 파일의 메타데이터중 st_atimespec 을 변경하는 것이다.

이렇게 파일을 읽을 때 마다 메타데이터가 변경되어 디스크에 I/O를 발생시켜 전체 시스템적인 성능을 떨어뜨리게 되는데, 파일에 액세스가 발생하더라도 이를 추적하지 않는다면 I/O 성능이 향상된다.

파일의 접근 시간을 추적하지 않는 기능을 noatime 이라고 하며, 이는 디스크를 마운트할 때 설정해줄 수 있다.

마운트할 때 -o noatime 옵션을 추가하면 되지만, 대부분 수동으로 하기보다는 /etc/fstab 을 통해 자동적으로 마운트되게끔 설정하기 때문에, /etc/fstab 파일에 아래처럼 옵션을 넣어서 마운트시켜주면 된다.

```bash
bconfiden2@DESKTOP:~$ sudo vi /etc/fstab
#[디바이스명]    [마운트지점]    [파일시스템]    defaults,noatime,nodiratime    [백업]  [검사]
/dev/sda1     /data1        ext4         defaults,noatime,nodiratime    0      0
```
