---
layout: post
title: "LDAP 클라이언트 트러블슈팅 - cuold not search LDAP server - Server is unavailable"
tags: linux
---

서버들을 재부팅할 일이 있어서 노드들을 전부 껐다 켰더니, 기존에 LDAP 서버에 추가해놨던 사용자들이 인식되지 않는 문제가 발생했다.

로그를 확인한 결과, LDAP 클라이언트들이 서버를 찾지 못해서 응답 받지 못하는 상황이었고, 사용자 정보를 받아오지 못하는 상황에 로컬 파일에도 존재하지 않아서 발생하는 문제였다.

로그는 아래처럼 뜬다.

```bash
bconfiden2@h01:~$ sudo systemctl status nscd
# ...
2월 28 12:53:48 h01 nscd[1113]: nss_ldap: could not connect to any LDAP server as cn=admin,dc=bconfiden2 - Can't contact LDAP server
 2월 28 12:53:48 h01 nscd[1113]: nss_ldap: failed to bind to LDAP server ldapi:///192.168.100.141: Can't contact LDAP server
 2월 28 12:53:48 h01 nscd[1113]: nss_ldap: reconnecting to LDAP server (sleeping 1 seconds)...
 2월 28 12:53:49 h01 nscd[1113]: nss_ldap: could not connect to any LDAP server as cn=admin,dc=bconfiden2 - Can't contact LDAP server
 2월 28 12:53:49 h01 nscd[1113]: nss_ldap: failed to bind to LDAP server ldapi:///192.168.100.141: Can't contact LDAP server
 2월 28 12:53:49 h01 nscd[1113]: nss_ldap: could not search LDAP server - Server is unavailable
```

우선 ldapi:///192.168.100.141 의 경우에는, LDAP 클라이언트와 관련된 패키지를 설치하는 도중에 지정해줬던 초기 설정값이다.

해당 호스트에 TCP 세션 대신 IPC를 활용하는 방식이라고 되어있는데, 이러한 설정값들은 ```/etc/ldap.conf```에서 관리된다.

```bash
bconfiden2@h01:~$ sudo vi /etc/ldap.conf
# ...
#uri ldapi:///192.168.100.141
# ldapi 대신 ldap 로 세팅
uri ldap://192.168.100.141
# 혹은 그냥 호스트만 지정해도 좋음
host 192.168.100.141
```
```bash
sudo service nscd restart
```

수정하고 서비스를 재시작해주면 ldap 서버를 정상적으로 인식한다.