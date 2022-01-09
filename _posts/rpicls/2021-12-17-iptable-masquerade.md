---
layout: post
title: "[홈클러스터] MASQUERADE 설정으로 메인노드 인터넷 가져다쓰기"
subtitle: ""
categories: devops
tags: rpicls
---

현재 라즈베리파이 클러스터들은 공유기에 직접적으로 연결되는 것이 아니라, 스위치를 통해 다른 콘솔 역할을 맡은 컴퓨터랑만 네트워크가 연결되어 있다.

물론 무선랜카드들이 달려 있지만, 밖에 가져갈 경우 매번 와이파이 설정을 해주고 싶지 않아서 콘솔 컴퓨터의 무선랜카드를 거쳐 인터넷을 사용하려고 한다.

스위치로 연결되어있는 메인 컴퓨터가 nat instance 역할을 한다고 보면 된다.

노트북에 내장된 무선랜카드가 공유기로부터 아이피를 할당받아 인터넷을 사용할 수 있기 때문에 라즈베리파이들은 유선 인터페이스와 무선 인터페이스를 거쳐 인터넷을 사용할 수 있다.

우선 해당 컴퓨터가 패킷을 포워딩 할 수 있게 ```/proc/sys/net/ipv4/ip_forward``` 값을 1로 설정해줘야 한다.

```echo 1 > /proc/sys/net/ipv4/ip_forward```처럼 직접 바꿀 수 있지만, 재부팅시 초기화되기 때문에 설정파일에서 값을 바꿔놓는 것이 좋다.

```
$ sudo vi /etc/sysctl.conf

net.ipv4.ip_forward=1
```

위처럼 값을 1로 설정한 뒤, ```sysctl -p```로 적용시켜준다.

다음으로는 아래처럼 iptables에서 규칙을 추가해줘야 한다.

```
$ sudo iptables -A FORWARD -o [PRIVATE]] -j ACCEPT
$ sudo iptables -A FORWARD -o [PUBLIC] -j ACCEPT
$ sudo iptables -t nat -A POSTROUTING -o [PUBLIC] -j MASQUERADE
```

위의 두줄은 인터페이스들에 모든 패킷이 통과 가능하게 하는 것이고, 마지막줄은 외부 인터넷과 연결되는 인터페이스에 MASQUERADE 설정을 해주어 내부망에 속한 컴퓨터들이 외부와 연결될 수 있게 해준다.

iptables 에는 현재 규칙들을 저장하는 ```iptables-save``` 명령도 있지만, 서버를 껐다 킬 경우 초기화 되기 때문에 매번 이렇게 설정을 해줘야 한다.

이를 간단히 해결하기 위해서는 iptables-persistent 라는 패키지가 있는데, ```sudo apt-get install iptables-persistent netfilter-persistent```처럼 설치할 수 있다.

iptables 를 저장한 뒤, ```netfilter-persistent save```와 ```netfilter-persistent start```를 수행해주면 설정한 규칙이 재부팅시에 적용된다.