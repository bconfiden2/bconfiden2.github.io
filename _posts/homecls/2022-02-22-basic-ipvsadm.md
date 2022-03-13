---
layout: post
title: "리눅스 ipvsadm 을 활용한 웹서버 로드밸런싱 LVM 클러스터 구축"
tags: homecls
---

리눅스 커널에 존재하는 로드밸런싱을 위한 가상 서버 모듈인 ipvsadm 을 활용하여 웹서버 로드밸런싱을 구현할 수 있다.

데스크톱이 LVS 서버 역할을 맡고, 라즈베리파이 클러스터의 각 노드들에 웹서버를 설치한다.

이 때 LVS 서버의 가상 호스트를 192.168.100.200 로 설정하여, 해당 주소로 요청을 보냈을 때 지정해놓은 웹서버들에 돌려가며 라우팅해준다.

세팅은 아래와 같다.

| 역할 | 주소 | 호스트명 | 장비 | 운영체제 |
| :-: | :-: | :-: | :-: | :-: |
| LVS 서버 | 192.168.100.142 | h02 | 일반 데스크톱 | Ubuntu Desktop 20.04 |
| 웹서버 1 | 192.168.100.101 | w01 | 라즈베리파이 | Ubuntu Server 20.04 |
| 웹서버 2 | 192.168.100.102 | w02 | 라즈베리파이 | Ubuntu Server 20.04 |
| 웹서버 3 | 192.168.100.103 | w03 | 라즈베리파이 | Ubuntu Server 20.04 |
| 웹서버 4 | 192.168.100.104 | w04 | 라즈베리파이 | Ubuntu Server 20.04 |

<br>

## LVS 서버

우선 가상호스트 아이피를 네트워크 인터페이스에 추가해준다.

```bash
bconfiden2@h02:~$ sudo ifconfig enp3s0:0 192.168.100.200 netmask 255.255.255.0 up
bconfiden2@h02:~$ ifconfig
# ...
enp3s0:0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.100.200  netmask 255.255.255.0  broadcast 192.168.100.255
        ether 00:01:2e:5a:c9:75  txqueuelen 1000  (Ethernet)
```

ipvsadm 패키지는 ```sudo apt-get install ipvsadm```으로 설치할 수 있다.

설치한 뒤에는 우선 서비스를 하나 등록해줘야 하는데, 포맷은 ```ipvsadm -A -t [가상호스트:포트] -s [규칙]```이 된다.

이 때 규칙은 라우팅 시 서버를 스케줄링하는 방식으로, 대표적인 라운드로빈의 경우는 rr 이라고 넣으면 된다.

그외에도 라운드로빈에 가중치를 부여한 wrr, 가장 적은 요청을 처리 중인 서버에게 넘기는 lc, 해시함수를 활용한 sh 등 다른 방식들이 많이 있다.

현재 세팅 기준으로 라운드로빈 방식으로 서비스를 등록하려면 ```sudo ipvsadm -A -t 192.168.100.200:80 -s rr```과 같이 하면 된다.

등록 후에는 아래처럼 ipvsadm의 상태를 확인할 수 있다.

```bash
bconfiden2@h02:~$ sudo ipvsadm -ln
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  192.168.100.200:80 rr
```

가상호스트를 등록해놨으면, 해당 호스트가 부하를 분산시킬 실제 웹서버들을 등록해줘야 하며, 사용 방식은 ```ipvsadm -a -t [가상호스트:포트] -r [실제서버:포트] [방식]```이다.

마지막에 들어가는 옵션(방식) 중 -m은 masquerade로, 자체적으로 주소를 변환하는 nat 방식을 의미하며, -g 는 다이렉트 라우팅을, -i 는 터널링을 의미한다.

만약 가상호스트 서비스를 등록할 때 규칙에 가중치와 관련된 것을 설정했으면, 여기서 -w 옵션에 숫자를 주어서 서버마다 가중치를 설정할 수도 있다.

웹서버 4개를 등록한 뒤 다시한번 ipvsadm 상태를 확인해보면, 아래처럼 뜬다.

```bash
$ bconfiden2@h02:~$ sudo ipvsadm -a -t 192.168.100.200:80 -r 192.168.100.101:80 -g
$ bconfiden2@h02:~$ sudo ipvsadm -a -t 192.168.100.200:80 -r 192.168.100.102:80 -g
$ bconfiden2@h02:~$ sudo ipvsadm -a -t 192.168.100.200:80 -r 192.168.100.103:80 -g
$ bconfiden2@h02:~$ sudo ipvsadm -a -t 192.168.100.200:80 -r 192.168.100.104:80 -g
bconfiden2@h02:~$ sudo ipvsadm -ln
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  192.168.100.200:80 rr
  -> 192.168.100.101:80           Route   1      0          0         
  -> 192.168.100.102:80           Route   1      0          0
  -> 192.168.100.103:80           Route   1      0          0
  -> 192.168.100.104:80           Route   1      0          0
```

LVS 서버에서 추가적으로, 들어오는 패킷을 다른쪽으로 포워딩시켜줄 수 있게 하는 커널 파라미터를 세팅해줘야 한다.

Masquerade 설정으로 메인노드 인터넷을 설정할 때와 마찬가지로, LVS 서버의 ```net.ipv4.ip_forward``` 값을 1로 세팅해서, 웹서버로 패킷들을 포워딩 가능하게 해준다.

간단하게 ```echo 1 > /proc/sys/net/ipv4/ip_forward```로 세팅하면 끝.

<br>

## 웹서버

기본적으로 아파치 웹서버가 설치되어있고, 켜져있는 상태라고 가정하고 진행한다.

웹서버에도 LVS 서버와 마찬가지로 동일한 가상 호스트를 추가해줘야 한다.

```bash
bconfiden2@h02:~$ sudo ifconfig eth0:0 192.168.100.200 netmask 255.255.255.0 up
bconfiden2@h02:~$ ifconfig
# ...
eth0:0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.100.200  netmask 255.255.255.0  broadcast 192.168.100.255
        ether 00:01:2e:5a:c9:75  txqueuelen 1000  (Ethernet)
```

뿐만 아니라, ARP 프로토콜에 대한 응답을 꺼줘야 하는데, 가상호스트로 접속 시 ARP 요청을 통해 특정 노드의 맥주소가 이미 캐싱되어있었을 경우, 로드밸런싱이 되지 않고 해당 호스트로만 바로 넘어가기 때문이다.

해당 설정파일은 /etc/sysctl.conf 이며, 아래와 같은 내용들을 추가해준 뒤, sysctl -p 로 변경사항을 적용시켜준다.

```bash
bconfiden2@w01:~$ sudo vi /etc/sysctl.conf
...
net.ipv4.conf.lo.arp_ignore = 1
net.ipv4.conf.lo.arp_announce = 2
net.ipv4.conf.all.arp_ignore = 1
net.ipv4.conf.all.arp_announce = 2
net.ipv4.conf.default.arp_ignore = 1
net.ipv4.conf.default.arp_announce = 2
```
```bash
bconfiden2@w01:~$ sudo sysctl -p
```

다른 모든 웹서버들에 설정을 동일하게 진행해준다.

각 노드의 인덱스 페이지를 구분할 수 있게 다르게 바꿔준 뒤, 가상호스트 192.168.100.200 으로 몇 번 접속해보면, 다른 노드들로 라우팅되면서 각 인덱스 페이지들이 뜨는 것을 확인할 수 있다.