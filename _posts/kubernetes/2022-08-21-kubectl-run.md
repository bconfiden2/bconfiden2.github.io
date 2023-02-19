---
layout: post
title: "Imperatives - kubectl run"
tags: k8s
---

kubectl run은 사용자가 터미널에서 직접 파드를 생성할 수 있게 해주는 명령어이다.

일반적인 사용 방법은 ```kubectl run 파드이름 --image=이미지명 [옵션1] [옵션2] ...```와 같다.

<br>

## 자주 사용하는 옵션들

| 이름 | 기본값 | 설명 |
| :-: | :-: | :-- |
| image | 없음 | 컨테이너 이미지를 지정하며, 반드시 들어가야 하는 필수 옵션이다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx` |
| annotations | 없음 | 파드에 어노테이션을 추가한다. 어노테이션을 여러개 설정하는 경우 동일한 옵션을 여러번 넣어준다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --annotations="annot1=test1" --annotations="annot2=test2"` |
| attach | false | true로 설정하는 경우, 파드가 실행된 이후에 `kubectl attach ...` 명령을 내리는 것과 동일하게 작동한다. attach에서도 사용하는 -i(--stdin) 또는 -t(--tty) 옵션을 run에서도 지원하기 때문에, 같이 사용할 수 있다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --attach=true --stdin --tty` |
| dry-run | none | 반드시 "none"(기본값), "server", "client" 셋 중 하나의 값을 갖는다. client일 경우, 해당 run 명령어를 실행하지 않고 어떻게 실행되는지에 대한 결과만 출력하며, 일반적으로 -o 옵션과 같이 사용된다. server일 경우, 실제로 api서버와 통신해서 생성이 가능한지까지 확인하지만, 자원을 실제로 사용하여 띄우지는 않는다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --dry-run=client -o yaml` |
| env | 없음 | 컨테이너에 세팅할 환경 변수 목록을 지정한다. 여러개 설정하는 경우 동일합 옵션을 여러번 넣어준다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --env="MYENV=test1" --env"FOO=bar"` |
| restart | Always | 파드가 종료되는 경우 재시작할지 말지에 대한 정책으로, "Always"(기본값), "OnFailure", "Never" 의 값을 갖는다. Always는 컨테이너가 종료되면 항상 자동으로 재시작되며, OnFailure은 컨테이너가 비정상적으로 종료될 시에만 재시작하고, Never은 재시작하지 않는다. OnFailure 같은 경우 특정 태스크를 수행하도록 설계된 컨테이너일 경우 사용하면 유용하다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --restart=OnFailure"` |
| port | 없음 | 컨테이너가 열어둘 포트번호를 지정한다. kubectl expose와는 다르게 포트번호 여러개를 넣어주는게 잘 안되므로, 필요할 경우 yaml파일로 생성하던지 expose 명령어를 쓴다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --port=30303` |
| expose | false | true로 설정하는 경우, 파드를 실행하면서 ClusterIP 서비스를 같이 생성하며, --port 옵션과 반드시 같이 사용되어야 한다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --expose=true --port=30303` |
| labels | 없음 | 파드에 적용될 레이블을 쉼표로 구분하여 넘겨준다. 만약 옵션을 여러개 준 경우, 맨 마지막 옵션에 해당하는 레이블만 적용된다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --labels="app=test1,env=test2"` |
| output | 없음 | 출력 포맷을 지정한다. json, yaml, name, go-template, go-template-file, template, templatefile, jsonpath, jsonpath-as-json, jsonpath-file 등의 값을 가질 수 있다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx -o json` |
| command | false | true로 설정하고 명령어와 인자들이 주어질 경우, 컨테이너에서는 이미지에 세팅된 기본 CMD 대신 입력된 명령어를 실행한다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --command=true -- [cmd] [arg1] [arg2] ...` |
| privileged | false | true로 설정하는 경우, 컨테이너를 privileged 모드로 실행한다. 이는 호스트 컴퓨터 커널의 기능 및 장치들에 접근할 수 있는 모드이다. |
| ------------------------ | --------------- | `kubectl run test --image=nginx --privileged` |



<br>

이 외에 몇가지 옵션들이 더 있는데, 이는 공식 문서에서 제공해주는 [kubectl run 치트시트](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#run)를 확인하자.