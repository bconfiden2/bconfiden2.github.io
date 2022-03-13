---
layout: post
title: "네트워크 문제 발생 시 리눅스에서 원인 추적하기"
tags: linux
---

여러가지 문제들이 서버의 네트워크 상태에 영향을 미쳐 정상적으로 인터넷과 연결이 되지 않을 수 있다.

리눅스에서 제공되는 다양한 네트워크 문제 해결 도구들을 활용하여 시스템 쪽에서의 근본적 원인들을 하나씩 확인 가능하다.

<br>

## 네트워크 인터페이스 카드 연결 상태

가장 기본적으로는 네트워크 연결이 활성화 되어 있는지부터 확인해야 한다.

ifconfig 명령으로는 시스템에서 인식하고 있는 네트워크 인터페이스들을 확인할 수 있는데, 이들 중 확인해보고 싶은 장치명을 가져다가 ethtool 로 검사할 수 있다.

```bash
# 유선랜카드
$ sudo ethtool enx00e04c60d746
Settings for enx00e04c60d746:
	Supported ports: [ TP MII ]
	Supported link modes:   10baseT/Half 10baseT/Full 
	                        100baseT/Half 100baseT/Full 
	Supported pause frame use: No
	Supports auto-negotiation: Yes
	Supported FEC modes: Not reported
	Advertised link modes:  10baseT/Half 10baseT/Full 
	                        100baseT/Half 100baseT/Full 
	Advertised pause frame use: Symmetric Receive-only
	Advertised auto-negotiation: Yes
	Advertised FEC modes: Not reported
	Speed: 10Mb/s
	Duplex: Half
	Port: MII
	PHYAD: 32
	Transceiver: internal
	Auto-negotiation: on
	Supports Wake-on: pumbg
	Wake-on: g
	Current message level: 0x00007fff (32767)
			       drv probe link timer ifdown ifup rx_err tx_err tx_queued intr tx_done rx_status pktdata hw wol
	Link detected: no
# 무선랜카드
$ sudo ethtool wlp2s0
Settings for wlp2s0:
	Link detected: yes
```

각 결과마다 마지막 줄에 Link detected 가 no, yes 로 뜨는데, yes 로 되어 있을 경우 네트워크에 연결되어 있다는 뜻이다.

연결이 되어있다고 할지라도 해당 인터페이스의 설정에 대해서도 검사를 해줘야 하는데, 이를 위해 ifconfig 로 정보를 가져올 수 있다.

```bash
$ ifconfig wlp2s0
wlp2s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.219.101  netmask 255.255.255.0  broadcast 192.168.219.255
        inet6 fe80::5a26:7813:f219:22cc  prefixlen 64  scopeid 0x20<link>
        ether 14:4f:8a:b2:0a:8e  txqueuelen 1000  (Ethernet)
        RX packets 17143  bytes 19218818 (19.2 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 9048  bytes 1682110 (1.6 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

두번째 줄에 inet 다음으로 호스트의 아이피가 나오고, netmask와 broadcast 정보들을 토대로 어떤 네트워크에 속해있는지 파악할 수 있다.

현재는 노트북이 집 공유기에 연결되어있는 상태고, DHCP 서버(공유기)가 할당해준 프라이빗 아이피가 문제 없이 홈네트워크에서 동작 중이다.

만약 네트워크 인터페이스에 대한 설정이 호스트에 대한 설정값과 맞지 않을 경우에는 DHCP 서버 측을 확인해야 한다.

<br>

## 게이트웨이와의 통신 상태

인터페이스가 정상적으로 활성화 돼있다면, 다음으로는 디폴트 게이트웨이에 대해서 검사해볼 필요가 있다.

패킷을 로컬 네트워크가 아닌 인터넷 상으로 보낼 때는 디폴트 게이트웨이로 설정된 호스트를 거쳐 가기 때문에, 게이트웨이에 문제가 생겨서 접근이 안될 수도 있다.

```route -n``` 혹은 ```netstat -rn```이 라우팅 테이블 정보를 확인하는 명령어이다.

두 명령어 모두 -n 옵션이 없을 경우에는 아이피 주소를 호스트명으로 바꿔서 보여주는데, 문제 해결을 위해서는 잠재적인 DNS 문제를 배제하는 것이 좋기 때문에 -n 옵션을 넣어준다.

```bash
$ netstat -rn
Kernel IP routing table
Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
0.0.0.0         192.168.219.1   0.0.0.0         UG        0 0          0 wlp2s0
169.254.0.0     0.0.0.0         255.255.0.0     U         0 0          0 wlp2s0
172.17.0.0      0.0.0.0         255.255.0.0     U         0 0          0 docker0
192.168.219.0   0.0.0.0         255.255.255.0   U         0 0          0 wlp2s0
```

패킷의 도착지 아이피가 로컬 네트워크들에 해당하지 않을 경우 Destination 이 0.0.0.0 으로 결정되어, 이에 해당하는 게이트웨이로 패킷을 송신하기 때문에 인터넷을 위한 디폴트 게이트웨이가 된다.

디폴트 게이트웨이가 확인되면 ping 등의 명령어로 통신 가능한지 확인해본다.

만약 게이트웨이와 통신이 되지 않는 상태일 경우, 게이트웨이의 ICMP 패킷 수신 설정 등을 확인해보는 등 해당 호스트 측으로 문제가 넘어간다.

<br>

## DNS 이름 해결이 정상적으로 동작하는지

만약 목적지 호스트를 옥텟으로 이루어진 아이피 형태가 아닌 도메인명으로 지정할 경우에는, DNS 기능이 동작하고 있는지 확인해야 한다.

nslookup을 활용하면 특정 도메인을 아이피 주소로 받아올 수 있다.

```bash
$ nslookup google.com
Server:		127.0.0.53
Address:	127.0.0.53#53

Non-authoritative answer:
Name:	google.com
Address: 142.250.66.142
Name:	google.com
Address: 2404:6800:4005:814::200e
```

DNS에 문제가 없을 경우, 위처럼 google.com 이라는 도메인이 142.250.66.142 라는 아이피를 갖고 있음을 보여준다.

이때 사용된 DNS 주소가 127.0.0.53 으로 되어있는데, 이는 ```/etc/resolv.conf```에 nameserver 로 설정된 값이다.

그러나 실질적으로 이는 ```/etc/systemd/resolved.conf``` 에 설정된 DNS 서버에 요청한다는 의미이고, DHCP 서버로부터 동적 할당을 받아왔을 경우 DHCP 서버에 설정된 DNS 정보를 가져온다.

만약 netplan 등을 활용해 고정 아이피를 설정해준 경우 역시 nameservers 항목에서 수동으로 설정해줘야 한다.

nslookup 결과로 정보를 가져오지 못하는 경우에는 네임서버의 상태를 의심해볼 수 있다.

다른 DNS 서버를 추가해본다거나, 기존에 설정되어있던 DNS 서버에 직접적으로 핑을 날려보는 등의 테스트가 가능하다.

<br>

## 원격 호스트에 찾아갈 수 있는지

앞선 사항들에 문제가 없을 경우에는, 게이트웨이나 네임서버에 핑을 날리듯 최종 목적지에 핑을 날림으로써 연결 상태를 확인할 수 있다.

원격 호스트에서 응답이 없을 경우에는 우선적으로 해당 원격지와 같은 네트워크에 속해있는 다른 원격 호스트에 핑을 날려볼 수 있는데, 이를 통해 어느 지점에서 문제가 발생하는지 파악할 수 있다.

라우팅 과정에서 어느 단계까지 패킷이 송신 가능한지 테스트하기 위한 툴이 traceroute 이다.

```bash
$ traceroute google.com
traceroute to google.com (142.250.66.110), 30 hops max, 60 byte packets
 1  _gateway (192.168.219.1)  3.944 ms  3.839 ms  5.740 ms
 2  * * *
 3  10.21.121.165 (10.21.121.165)  15.005 ms 10.21.121.161 (10.21.121.161)  16.433 ms 10.21.121.165 (10.21.121.165)  16.387 ms
 4  10.18.162.9 (10.18.162.9)  19.104 ms 10.18.162.1 (10.18.162.1)  21.982 ms 10.18.162.9 (10.18.162.9)  22.013 ms
 5  1.213.141.13 (1.213.141.13)  31.159 ms 1.208.141.13 (1.208.141.13)  23.565 ms 1.213.3.89 (1.213.3.89)  25.053 ms
 6  1.208.178.169 (1.208.178.169)  26.880 ms  3.635 ms 1.208.179.177 (1.208.179.177)  5.339 ms
 7  61.35.243.137 (61.35.243.137)  5.132 ms  5.166 ms  7.128 ms
 8  1.208.149.1 (1.208.149.1)  8.936 ms 1.213.114.133 (1.213.114.133)  8.899 ms 1.208.105.97 (1.208.105.97)  10.495 ms
 9  203.252.13.22 (203.252.13.22)  55.690 ms 1.208.145.38 (1.208.145.38)  55.724 ms 1.208.175.170 (1.208.175.170)  51.318 ms
10  1.208.148.206 (1.208.148.206)  51.351 ms 1.208.106.210 (1.208.106.210)  52.033 ms 1.208.148.206 (1.208.148.206)  59.739 ms
11  74.125.118.154 (74.125.118.154)  50.682 ms 72.14.215.29 (72.14.215.29)  59.075 ms 74.125.118.154 (74.125.118.154)  52.777 ms
12  * * *
13  108.170.241.33 (108.170.241.33)  96.935 ms 216.239.47.82 (216.239.47.82)  44.677 ms 108.170.241.33 (108.170.241.33)  44.563 ms
14  66.249.95.129 (66.249.95.129)  43.879 ms 108.170.241.45 (108.170.241.45)  51.103 ms  46.100 ms
15  hkg12s28-in-f14.1e100.net (142.250.66.110)  53.994 ms  52.753 ms  42.195 ms
```

원격 호스트까지 몇 홉을 거쳐 통신이 되는지, 통신을 지연시키는 구간이 있는지 등을 확인 가능하다.
 
결과 중 경로가 * * * 처럼 출력되는 경우 해당 호스트(라우터)의 정책상 특정 udp 패킷을 거부할 수 있으므로, 대신 tcptraceroute 패키지를 설치하여 똑같이 사용하면 된다.

만약 목적지까지 패킷들을 라우팅하는건 문제가 없지만, 해당 서버의 서비스에 접근하지는 못한다면(웹서비스 등) 마지막으로는 포트가 열려 있는지 점검한다.

포트를 테스트하기 위해서는 ```nmap```을 사용하는데, nmap 은 진짜로 막혀있는 포트와 방화벽이 걸러낸 포트를 구별해주지만 사실상 웬만한 서버들은 방화벽으로 차단하기 때문에 실제로 다운된 포트와의 구별이 큰 의미를 갖지는 않는다.

```bash
$ nmap -p 443 naver.com
Starting Nmap 7.80 ( https://nmap.org ) at 2022-01-26 17:24 KST
Nmap scan report for naver.com (223.130.200.107)
Host is up (0.0061s latency).
Other addresses for naver.com (not scanned): 223.130.195.95 223.130.200.104 223.130.195.200

PORT    STATE SERVICE
443/tcp open  https

Nmap done: 1 IP address (1 host up) scanned in 0.06 seconds

$ nmap -p 22 naver.com
Starting Nmap 7.80 ( https://nmap.org ) at 2022-01-26 17:30 KST
Nmap scan report for naver.com (223.130.195.200)
Host is up (0.0057s latency).
Other addresses for naver.com (not scanned): 223.130.200.104 223.130.200.107 223.130.195.95

PORT   STATE    SERVICE
22/tcp filtered ssh

Nmap done: 1 IP address (1 host up) scanned in 0.28 seconds
```

일반적으로 포트가 열려있으면 위의 실행처럼 open 으로 뜨지만, 방화벽에 의해 필터링 될 경우에는 STATE 부분에 filtered 를 볼 수 있다.