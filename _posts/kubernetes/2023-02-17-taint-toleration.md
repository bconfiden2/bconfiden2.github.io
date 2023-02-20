---
layout: post
title: "테인트(Taints)와 톨러레이션(Tolerations) 기본 개념"
tags: k8s
---

테인트는 노드가 특정 파드 셋을 제외시키거나 스케줄링 되지 않도록 설정할 수 있는 제약 같은 것으로, 노드에 적용된다.

톨러레이션은 테인트가 걸려있는 노드에, 해당 테인트를 무시하고 파드가 배치될 수 있도록 파드에 부여한다.

즉, 테인트가 설정된 노드에는 기본적으로는 파드들이 스케줄링 되지 않으며, 테인트가 걸린 노드에 파드를 스케줄링 하려면 해당 파드에 톨러레이션을 설정해줘야 하는 것이다.

이렇게 톨러레이션이 설정된 파드들만이 해당 노드에서 실행이 가능하다.

일반적으로 어떤 노드에 대해서 어떤 파드들을 담당할지에 대한 역할 같은 것을 부여할 때 사용한다.

<br>

유데미에서 CKA 강의로 유명한 뭄샤드 씨는, 노드와 파드를 각각 사람과 해충으로, 테인트와 톨러레이션을 각각 해충 차단 스프레이와 해충의 면역력으로 비유한다.

기본적으로 어떤 사람이 자신에게 해충 차단 스프레이를 하나도 뿌리지 않는다면, 해충들은 좋다구나 하고 사람에게 들러붙는다.

이것을 파드가 스케줄링 되는 것으로 보면 된다.

그러나 만약 사람(노드)이 어떤 특성을 갖는 해충들을 쫓아내는 해충 차단 스프레이(테인트)를 몸에 뿌려놓으면, 그 해충(파드)은 몸에 들러붙을 수 없다.

이 경우 해당 특성에 면역력을 갖는 해충들은 들러붙을 수 있는데, 이것이 톨러레이션인 것이다.

<br>

노드에 특정한 key=value:effect 형태의 테인트를 걸고 이러한 테인트를 통과하는 톨러레이션이 부여된 파드는, 그 노드에 배치될 수 있다.

파드에 톨러레이션이 설정됨으로써 스케줄러는 이와 일치하는 테인트가 있는 노드에 해당 파드를 스케줄링 할 수 있다는 말인데, 주의할 점은 이것은 스케줄링을 허용한다는 뜻이지, 반드시 해당 노드에만 파드가 스케줄링 된다는 뜻이 아니다.

스케줄러의 판단에 따라 테인트가 없는(테인트가 없어도 충분히 스케줄링이 가능하기 때문에) 노드에도 배치가 될 수 있는 것이다.

쿠버네티스 클러스터를 구축하면 기본적으로 모든 사용자 파드들은 컨트롤 플레인에 스케줄링 되지 않는 이유도 사실 테인트 때문이다.

kubeadm으로 설치하는 경우, 컨트롤 플레인 노드에는 테인트가 설정되기 때문에 일반적인 파드들이 애초에 배치되지 않는다.

<br>

테인트는 키-값 형태로 부여하며, 이 뒤에 테인트의 effect를 지정할 수 있다.

테인트의 이펙트에는 NoSchedule, PreferNoSchedule, NoExecute 3가지를 설정할 수 있다.

NoSchedule은 디폴트 값으로, 파드를 스케줄링하지 않는다. 그러나 기존에 실행되던 파드들에 대해서는 따로 건드리지 않는다.

NoExecute는 파드를 스케줄링하지 않음과 동시에, 기존에 실행되고 있던 파드들 역시 축출(evict)해서 제거한다.

PreferNoSchedule은 파드를 스케줄링하지 않으려고 노력(?)한다. 사실 어떤 효과인지 잘 모르겠다.

<br>

노드에 테인트가 걸려있는지는, describe에서 Taint 부분을 확인한다.
```
controlplane ~ ➜  kubectl describe node node01 | grep Taints
Taints:             <none>
```
<br>

kubectl taint 명령어로 노드에 직접 테인트를 걸어준다.
```
controlplane ~ ➜  kubectl taint node node01 mykey=myvalue:NoSchedule
node/node01 tainted

controlplane ~ ➜  kubectl describe node node01 | grep Taint
Taints:             mykey=myvalue:NoSchedule
```
<br>

컨트롤플레인에는 기본적으로 스케줄되지 않고, 노드1번에도 테인트를 걸어놨기 때문에, 아무런 톨러레이션이 없는 파드를 생성하면 무한정 Pending 상태에 놓이게 된다.
```
controlplane ~ ✖ k run test --image=nginx
pod/test created

controlplane ~ ➜  k get po
NAME       READY   STATUS    RESTARTS   AGE
test       0/1     Pending   0          92s
```
<br>

노드 1번에 파드를 스케줄링하기 위해서는, 파드에 톨러레이션이 추가되어야 한다.

아래 yaml 파일처럼 해당 테인트를 충족시키기 위한 톨러레이션 항목들을 넣어주고 파드를 생성하면, 노드01에 정상적으로 스케줄링되는 것을 확인할 수 있다.

```
controlplane ~ ➜  kubectl run test --image=nginx --dry-run=client -o yaml > test.yaml
```
```
controlplane ~ ➜  vi test.yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: test
  name: test
spec:
  containers:
  - image: nginx
    name: test
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
  tolerations:
  - key: mykey
    operator: Equal
    value: myvalue
    effect: NoSchedule
status: {}
```
```
controlplane ~ ➜  kubectl apply -f test.yaml 
pod/test created

controlplane ~ ➜  k get pods -o wide
NAME       READY   STATUS    RESTARTS   AGE    IP           NODE     NOMINATED NODE   READINESS GATES
test       1/1     Running   0          52s    10.244.1.3   node01   <none>           <none>
```
<br>

파드에 톨러레이션을 넣는 방법에는 여러 경우가 있는데, spec 부분에 아래 예시처럼 지정하는 경우는 모두 테인트와 일치한다고 본다.
```
tolerations:
- key: "mykey"
  operator: "Equal"
  value: "myvalue"
  effect: "NoSchedule"
```
```
tolerations:
- key: "mykey"
  operator: "Exists"
  effect: "NoSchedule"
```
operator의 기본값은 Equal이기 때문에, 생략하는 경우 키와 값이 테인트와 일치해야만 한다.

그러나 Eqaul 말고 Exists를 값으로 받을 수도 있는데, 이 경우 아래쪽 예시처럼 value 부분을 지정하지 않는다.

만약 effect 부분이 생략되는 경우에는 모든 이펙트와 매칭된다.

<br>

기존에 있던 테인트를 지우고 싶은 경우, kubectl taint 명령어 맨 뒤에 - 만 추가로 붙여준다.
```
controlplane ~ ➜ kubectl describe node controlplane | grep Taints
Taints:             node-role.kubernetes.io/control-plane:NoSchedule

controlplane ~ ➜  kubectl taint node controlplane node-role.kubernetes.io/control-plane:NoSchedule-
node/controlplane untainted
```
```
controlplane ~ ➜  kubectl describe node node01 | grep Taints
Taints:             mykey=myvalue:NoSchedule

controlplane ~ ➜  kubectl taint node node01 mykey=myvalue:NoSchedule-
node/node01 untainted
```
<br>