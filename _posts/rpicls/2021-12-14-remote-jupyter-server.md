---
layout: post
title: "[라즈베리파이] 홈 클러스터에서 원격 주피터 서버 열어놓기"
subtitle: ""
categories: system
tags: rpicls
---

우선은 간단하게 ```pip3 install jupyter```로 주피터 노트북을 설치해준다.

일반적으로는 주피터를 설치할 경우, 설치 과정에서 자동적으로 환경변수 PATH 에 등록해주지만, 만약 jupyter 를 찾을 수 없다고 나올 때는 ```export PATH=~/.local/bin:$PATH```처럼 직접 추가해준다.

물론 주피터 노트북이 설치된 경로에 맞게 바꿔주고, .bashrc 파일에 추가해주는 것이 좋다.


원격으로 서비스할 것이기 때문에, ```jupyter notebopk password```를 사용해 비밀번호를 반드시 설정해 놓아야 한다.

비밀번호를 세팅하지 않을 경우, 전세계적으로 무차별적인 포트스캐닝에 그냥 당해버린다. 포트번호를 바꿔놓아도 사람들이 자주 접속한다.


```jupyter notebook --generate-config```를 통해 주피터 서비스의 설정들을 몇가지 바꿔줘야 하는데, 이를 수행하면 .jupyter 경로 아래에 파일들이 생기므로 이 파일들을 아래처럼 바꿔주면 된다.

```bash
$ vi ~/.jupyter/jupyter_notebook_config.py

c.NotebookApp.ip = '0.0.0.0'    # 모든 아이피에서 접속 허용
c.NotebookApp.open_browser = False  # 브라우저 실행하지 않게
c.NotebookApp.port = 8888   # 다른 포트로 변경하는 것을 권장
```

```jupyter notebook```을 실행시키면, 지정해둔 포트로 주피터 노트북에 접근할 수 있다.

그러나 아직은 로컬 네트워크에 속한 컴퓨터들만이 접근 가능한데, 퍼블릭 아이피의 해당 포트로 요청을 보내봤자 이는 공유기에 요청이 가기 때문이다.

따라서 공유기 관리 페이지에 들어가, 주피터를 서빙하는 컴퓨터의 아이피와 포트번호를 포워딩 설정 해줘야 외부에서도 접근이 가능하다.

이 단계까지 오게 되면 내부망에서도 외부망에서도 서비스 중인 노트북에 들어갈 수 있지만, 컴퓨터가 재부팅될 경우 매번 다시 켜주기 번거롭기 때문에 이를 systemctl 에 등록하여 자동으로 시작하게 한다.

```$ sudo vi /etc/systemd/system/jupyter.service```를 통해 새로운 서비스 파일을 만들어주고, 아래와 같은 형식으로 서비스를 설정한다.

```
[Unit]
Description=Jupyter server

[Service]
Type=test
PIDFile=/run/jupyter.pid
User=bconfiden2 # 사용자명
ExecStart=/home/bconfiden2/.local/bin/jupyter-notebook  # 주피터노트북 실행경로(which 로 확인 가능)
WorkingDirectory=/home/bconfiden2

[Install]
WantedBy=multi-user.target
```

아래처럼 systemctl 에 등록해준 뒤 서비스를 실행시켜주고, 상태를 확인해보면 잘 서비스 중임을 확인할 수 있다.

이는 컴퓨터를 껐다 켜도 자동으로 재실행되므로 tmux 로 매번 켜놓을 필요가 없다!

```
$ sudo systemctl enable jupyter.service
$ sudo systemctl start jupyter
$ sduo systemctl status jupyter

● jupyter.service - Jupyter Server
     Loaded: loaded (/etc/systemd/system/jupyter.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2021-12-20 19:01:53 KST; 20min ago
   Main PID: 764 (jupyter-noteboo)
      Tasks: 1 (limit: 9332)
     Memory: 85.6M
     CGroup: /system.slice/jupyter.service
             └─764 /usr/bin/python3 /home/bconfiden2/.local/bin/jupyter-notebook

12월 20 19:01:53 DESKTOP systemd[1]: Started Jupyter Server.
12월 20 19:01:56 DESKTOP jupyter-notebook[764]: [I 19:01:56.055 NotebookApp] Serving notebooks from local directory: /home/bconfiden2
12월 20 19:01:56 DESKTOP jupyter-notebook[764]: [I 19:01:56.055 NotebookApp] Jupyter Notebook 6.4.6 is running at:
12월 20 19:01:56 DESKTOP jupyter-notebook[764]: [I 19:01:56.055 NotebookApp] http://DESKTOP:8899/
12월 20 19:01:56 DESKTOP jupyter-notebook[764]: [I 19:01:56.055 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirma
```