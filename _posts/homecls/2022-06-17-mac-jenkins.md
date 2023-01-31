---
layout: post
title: "M1 Mac 에 젠킨스 설치하고 퍼블릭 IP로 접근 가능하게 열어놓기"
tags: homecls
---

젠킨스 설치는 [공식문서](https://www.jenkins.io/doc/book/installing/)에 정리가 잘 되어 있어서, 아주 쉽게 설치가 가능하다.

기존에 리눅스(우분투 20.04)에서 깔 때도 apt 저장소 추가하여 바로 설치가 가능했던 것 처럼, 맥에서도 brew 라는 패키지 관리 툴을 사용한 설치를 지원한다.

brew에서는 젠킨스 LTS 버전과 Weekly 버전을 모두 지원하는데, 우선은 안정적인 LTS를 설치하여 사용할 생각이다.

아래처럼 jenkins-lts 패키지를 설치해주고, 설치가 완료되면 brew services 를 이용하여 서비스를 시작한다.

```bash
# 젠킨스 설치
bconfiden2ui-iMac :: ~ 1 » brew install jenkins-lts
==> Auto-updated Homebrew!
Updated 1 tap (homebrew/core).
# ...
# 설치로그...
# ...
Hide these hints with HOMEBREW_NO_ENV_HINTS (see `man brew`).

# 젠킨스 시작
bconfiden2ui-iMac :: ~ » brew services start jenkins-lts
==> Successfully started `jenkins-lts` (label: homebrew.mxcl.jenkins-lts)
```

<br>

디폴트로 로컬호스트의 8080 포트로 열리기 때문에, 먼저 해당 웹UI로 접속하여 기본 설정들을 변경해줄 수 있다.

아래와 같은 화면이 뜨는데, 언급하고 있는 경로에 가서 초기 관리자 비밀번호를 확인하여 입력해준다.

```bash
bconfiden2ui-iMac :: ~ » cat ~/.jenkins/secrets/initialAdminPassword
7fcbd4cd979f49ba906a8cce0dfdf699
```

<img src="https://user-images.githubusercontent.com/58922834/215726713-1265684b-f0b9-457f-ad89-c754f739a833.png">

<br>

비밀번호를 입력하고 다음 버튼을 누르면, 초기에 설치할 플러그인들을 선택할 수 있게 해준다.

패키지들을 직접 선택하여 불필요한 플러그인을 제외시킬수도 있지만, 처음에는 그냥 무지성으로 추천해주는 플러그인들을 설치하는 것도 나쁘지 않다.

<img src="https://user-images.githubusercontent.com/58922834/215726860-495797f3-2187-4b71-8277-b5c90fc3b3ef.png">

열심히 플러그인들을 설치하고 있다.

<img src="https://user-images.githubusercontent.com/58922834/215726915-cf69444a-a8bb-4078-a410-7335ee050af8.png">

<br>

설치가 완료되면 사용할 계정을 하나 추가해준 뒤,

<img src="https://user-images.githubusercontent.com/58922834/215726811-190df611-9cb2-4690-9bb9-343238f54f7f.png">

<br>

젠킨스의 접속 URL 을 세팅해준다.

기본적으로 ```http://localhost:8080```을 띄워주는데, 뒤에서 변경할 예정이기 때문에 우선은 그냥 저장 버튼을 눌러 초기 세팅을 마친다.

<img src="https://user-images.githubusercontent.com/58922834/215726967-fa9d6ed2-66e4-4950-913e-d04f4534fd3c.png">

<br>

젠킨스 웹UI에 들어올 수 있는데, 왼쪽에 있는 젠킨스 관리 탭에 들어가 시스템 설정 페이지로 들어간다.

<img src="https://user-images.githubusercontent.com/58922834/215727026-703a73fd-ac7e-440c-bc1c-afd5bbf371da.png">

시스템 설정에서 아주 조금만 내리다 보면 아래와 같이 앞서 설정하려고 했던 젠킨스의 URL을 설정할 수 있는 칸이 보이는데, 만약 공인아이피를 통하여 외부에서 젠킨스에 접근하고 싶을 경우 해당 부분을 바꿔줘야 한다.

<img src="https://user-images.githubusercontent.com/58922834/215727057-7117bb54-5e1f-4c8b-882e-962c4a7dce99.png">

나의 경우에는 bconfiden2.site 라는 도메인을 가지고 있기 때문에, 아이맥의 퍼블릭 아이피로 연결시킨 도메인명을 넣어주었다.

<br>

우분투에서 설치했던 경우, 이 항목을 바꿔주고 젠킨스를 재시작하면 해당 아이피로 접속이 가능했다.

하지만 맥에서는 추가적으로 몇가지 설정파일에서 값을 변경해줘야 한다.

이러한 파일들은 ```/opt/homebrew/Cellar/jenkins-lts/2.332.3``` 아래에 존재하는데, 구글링하면서 찾아봤던 결과 시스템마다 조금씩 달라질 수 있는 것 같다.

아무튼 자기 시스템에서 패키지가 설치되는 위치에 맞게 찾아가보면, homebrew.jenkins-lts.service 라는 파일과 homebrew.mxcl.jenkins-lts.plist 라는 두개의 파일이 존재한다.

이 파일을 통해 젠킨스의 httpListenAddress 설정값을 세팅해줄 수 있는데, 기본적으로 127.0.0.1 로 지정되어있기 때문에, 로컬호스트에서밖에 웹에 접근할 수 없었던 것이다.

따라서 해당 프로퍼티를 모든 소스에서 접근할 수 있도록 0.0.0.0 으로 변경해주고 젠킨스를 재시작하면, 외부에서도 접근이 가능하게 된다.

```bash
bconfiden2ui-iMac :: Cellar/jenkins-lts/2.332.3 » vi homebrew.jenkins-lts.service
# jenkins-lts.service 수정
[Unit]
Description=Homebrew generated unit for jenkins-lts

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
# --httpListenAddress를 0.0.0.0 으로
ExecStart=/opt/homebrew/opt/openjdk@11/bin/java -Dmail.smtp.starttls.enable=true -jar /opt/homebrew/opt/jenkins-lts/libexec/jenkins.war --httpListenAddress=0.0.0.0 --httpPort=8080

# mxcl.jenkins-lts.plist 수정
bconfiden2ui-iMac :: Cellar/jenkins-lts/2.332.3 » vi homebrew.mxcl.jenkins-lts.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>homebrew.mxcl.jenkins-lts</string>
	<key>ProgramArguments</key>
	<array>
		<string>/opt/homebrew/opt/openjdk@11/bin/java</string>
		<string>-Dmail.smtp.starttls.enable=true</string>
		<string>-jar</string>
		<string>/opt/homebrew/opt/jenkins-lts/libexec/jenkins.war</string>
        # --httpListenAddress를 0.0.0.0 으로
		<string>--httpListenAddress=0.0.0.0</string>
		<string>--httpPort=8080</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>

# 젠킨스 재시작
bconfiden2ui-iMac :: Cellar/jenkins-lts/2.332.3 » brew services restart jenkins-lts
Stopping `jenkins-lts`... (might take a while)
==> Successfully stopped `jenkins-lts` (label: homebrew.mxcl.jenkins-lts)
==> Successfully started `jenkins-lts` (label: homebrew.mxcl.jenkins-lts)
```

내가 젠킨스에 보내는 패킷을 보려는 사람이 있을까 싶긴 하지만... 그래도 http 로 열어놓고있기 때문에 자주 사용하는 비밀번호 유출에 유의하자!