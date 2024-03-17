---
layout: post
title: "쉘에서 kubectl 자동완성 사용하기"
tags: k8s
---

```kubectl completion bash``` 명령으로 배쉬 쉘에서 kubectl 자동 완성 스크립트를 생성할 수 있다.

해당 스크립트를 적용시키면 현재 쉘 세션에만 적용되기 때문에, 모든 세션에 적용시키기 위해서는 사용자 계정의 bashrc에 추가할 수 있다.

```
echo 'source <(kubectl completion bash)' >>~/.bashrc
```

시스템 전체에 적용하기 위해서는 bash-completion이 읽어들이는 스크립트 경로인 ```/etc/bash_completion.d``` 아래에 파일을 생성할 수도 있다.

```
kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null
```

<br>

kubectl에 대해 k 로 alias를 붙여 사용하는 경우도 흔한데, 이 경우에는 아래와 같이 확장할 수 있다.

```
echo 'alias k=kubectl' >>~/.bashrc
echo 'complete -o default -F __start_kubectl k' >>~/.bashrc
```

이후 ```source .bashrc```, ```exec bash``` 또는 쉘을 새로 실행시키면 자동 완성이 적용된다.