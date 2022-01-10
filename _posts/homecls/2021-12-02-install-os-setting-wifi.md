---
layout: post
title: "[홈클러스터] 라즈베리파이 - 운영체제 설치 및 와이파이 세팅"
subtitle: ""
categories: devops
tags: homecls
---

## 준비물

- micro sd 카드 (16GB 이상 권장)

- sd 카드 리더기

- [sd 카드 포맷](https://www.sdcard.org/downloads/formatter/sd-memory-card-formatter-for-windows-download/)

- 이미지파일 flash 툴
    - [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
    - [balenaEtcher](https://www.balena.io/etcher/)
    - [imgFlasher](https://www.upswift.io/imgflasher)

- 디스크 이미지 파일(.img)

<br>

## 순서

1. 마이크로sd카드를 리더기에 넣은 뒤 컴퓨터에 꽂아준다.

2. sd카드를 먼저 포맷해주는데, 위의 sd card formatter 를 사용해도 되고, 아니면 파일시스템에서 직접 우클릭을 하며 포맷을 눌러줘도 된다.(윈도우 기준)

3. 디스크 이미지 파일을 sd카드에 올려줘야 하는데, 이 때 이미지파일 flash 도구들 중 하나를 사용한다.
    - Raspberry Pi Imager 는 라즈베리파이에서 공식적으로 제공해주는 프로그램인데, 조금 불안정한 감이 없지 않다.
    - 그래서인지 많은 사람들이 balenaEtcher 를 사용하는데, 이상하게 잘 될때도 있고 validation 부분에서 자꾸 sd카드 마운트를 해제시키면서 에러를 뱉는 경우도 몇 번 있었다.
    - imgFlasher 는 그래도 아직까지 문제 없이 동작하기 때문에 imgFlasher 가 개인적으로 마음에 든다.

4. 셋 중 뭐가 됐든 프로그램을 실행시키면, os 이미지 파일과 장치를 선택하는 창이 나오는데, 미리 디스크 이미지 파일을 받아놓아야 한다.

5. [라즈베리파이 소프트웨어 페이지](https://www.raspberrypi.com/software/operating-systems/)에서 다양한 이미지 파일을 받아온다.

6. 프로그램이 sd카드에 운영체제를 다 올릴때까지 기다렸다가, 완료되면 라즈베리파이에 꽂아서 전원을 넣어주면 된다.

<br>

## Wifi 세팅

라즈베리파이에 기본적으로 와이파이 모듈을 탑재해줬기 때문에, 무선인터넷에 연결이 가능하다.

근데 아무리 와이파이를 잡으려고 해도, AP not found 같은 메시지를 띄우며 신호를 잡지 못한다.

이는 라즈베리파이 설정에서 와이파이 국가를 한국이 아니라 미국으로 잡아줘야 된다.

```sudo raspi-config```를 사용하여 다른 기본적인 세팅들에 대해서도 설정할 수 있는 창을 띄워준다.(약간 ncurses 라이브러리 같은 느낌의 윈도우랄까)

설정창에서 Localisation Options - WLAN Country 를 US 혹은 UK 로 잡아주면 된다.

이후에는 상단 배너에서 와이파이를 직접 잡아주면 된다.

만약 GUI 지원이 되지 않는 운영체제(우분투 서버 같은)로 들어왔다면 무선인터넷은 ```/etc/wpa_supplicant/wpa_supplicant.conf``` 파일에서 설정해줄 수 있다.

```bash
$ sudo vi /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="WIFI_NAME"
    psk="WIFI_PASSWORD"
}
```

이때 psk 부분에는 와이파이 비밀번호를 평문 그대로 저장하는데, 보안상 찝찝할 경우에는 ```wpa_passphrase [WIFI_NAME] [WIFI_PASSWORD]``` 명령어를 사용해 임의의 psk 를 생성할 수 있다.

```bash
$ wpa_passphrase WIFI_NAME WIFI_PASSWORD
network={
	ssid="WIFI_NAME"
	#psk="WIFI_PASSWORD"
	psk=46d9ce1543e5997199f818b25b75afc512afb57ec7e42140853e4f7a99a76d19
}
```

시간대 역시 기본적으로는 표준시간대 그대로 세팅되어있기 때문에, CLI 상에서 명령어로 설정해줘야 한다면 ```timedatectl``` 을 활용하자!