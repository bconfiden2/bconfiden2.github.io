---
layout: post
title: "쿠버네티스 클러스터 설치하기"
tags: k8s
---

홈클러스터를 기준으로, 컨트롤 플레인 역할의 컴퓨터 1대와 노드 역할을 하는 컴퓨터 2대로 쿠버네티스를 구성한다.

<br>

## 기본 세팅

아래의 내용들은 컨트롤 플레인과 모든 워커 노드들 모두에서 동일하게 진행한다.

클러스터의 각 머신에는 모두 컨테이너 런타임이 설치되어있다고 가정한다.

<br>

먼저 쿠버네티스에서는 기본적으로 스왑 공간을 비활성화시키는 것을 권장한다.
```
sudo swapoff -a
```

시스템 재부팅 시 애초에 스왑 공간을 마운트하지 않기 위해서, /etc/fstab 파일에서 스왑파일과 관련된 부분을 주석 처리 해준다.

파일을 열어서 직접 변경해도 되지만, sed 를 사용하여 명령어로 처리가 가능하다.

아래 명령어는 /swap 앞에 # 을 넣어주기 때문에, 기존에 주석처리가 되어있었더라도 상관없다.
```
sudo sed -i '/swap/s/^/#/' /etc/fstab
```
<br>

iptable 설정을 몇가지 바꿔주고, sysctl에 해당 프로퍼티 값을 갱신한다.
```bash
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

sudo modprobe overlay
sudo modprobe br_netfilter
sudo sysctl --system
```
<br>

우분투를 사용하고 있기 때문에, apt를 통해 kubeadm, kubelet, kubectl 패키지들을 설치한다.

관련된 패키지들은 쿠버네티스에서 관리하고있는 저장소를 추가해줘야 그쪽으로부터 받을 수 있기 때문에, gpg 키를 추가하여 apt 저장소를 갱신해준 뒤 설치한다.
```
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
```

설치해뒀던 패키지가 자동으로 업데이트되면 클러스터를 사용하다가 호환이 되지 않을 수 있기 때문에, hold 를 통해 버전을 고정해준다.
```
sudo apt-mark hold kubelet kubeadm kubectl
```

kubelet 서비스는 설치 후 자동으로 올라와서 시작되지만(아마), 확실히 하기 위해 systemctl로 직접 띄워준다.
```
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```
<br>

- 한번에 정리하기

apt-get install 같은 경우는 정상적으로 패키지들을 설치하더라도 종료 코드로 0(정상) 말고 다른 걸 찍기도 한다.

그렇기 때문에 스크립트가 해당 위치에서 중단될 때가 많은데, 쉘스크립트로써 이를 만드려면 종료 조건에 관계 없이 실행하도록 짤 수 있겠지만 일단은 명령어 뭉치를 다시 복사해가서 쓰도록 하자.

apt-get install을 기준으로 총 3개 묶음으로 나눠놨으니 순차적으로 복사해가서 실행하면 된다.
```bash
sudo swapoff -a
sudo sed -i '/swap/s/^/#/' /etc/fstab
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
sudo sysctl --system
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

sudo apt-mark hold kubelet kubeadm kubectl
sudo systemctl daemon-reload
sudo systemctl restart kubelet

```
<br>

## 컨트롤 플레인 설정

아래의 내용은 마스터 노드에서만 진행하고, 워커 노드에서는 진행하지 않는다.

컨트롤 플레인 역할을 할 마스터 노드에서는 kubeadm을 사용하여 쿠버네티스 클러스터를 초기화한다.
```bash
bconfiden2@h01:~$ sudo kubeadm init
[init] Using Kubernetes version: v1.26.1
[preflight] Running pre-flight checks
[preflight] Pulling images required for setting up a Kubernetes cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection
[preflight] You can also perform this action in beforehand using 'kubeadm config images pull'
[certs] Using certificateDir folder "/etc/kubernetes/pki"
[certs] Generating "ca" certificate and key
#...
#...
Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 222.111.164.42:6443 --token 74xi2q.60oy3vj9b46rb20h \
	--discovery-token-ca-cert-hash sha256:0f980e18b8a9e687f7d82d60025d661626f198b6070172bc42e5f908e8323acc
```
마지막 부분을 잘 읽어보면, kubeadm join을 사용하여 워커 노드들을 클러스터에 넣어줄 수 있다고 한다.

해당 토큰과 해시값을 워커 노드들 설정할 때 이용할 것이기 때문에 기억해놓고 있어야 한다.

<br>

kubeadm init에서 출력한 메시지 내용들 중 마지막에서 조금만 위쪽으로 올라가보면, 초기화된 쿠버네티스 클러스터에 접근할 수 있는 설정 파일의 위치를 알려준다.

`/etc/kubernetes/admin.conf`인데, 루트 사용자로 로그인 한 상태라면 KUBECONFIG 환경 변수에 해당 파일 위치를 넣어준다.

만약 일반 유저라면 아래의 명령어들을 그대로 따라해서 홈디렉토리에 .kube 디렉토리를 만들고 그 아래에 해당 설정파일을 위치시키면 된다.
```bash
bconfiden2@h01:~$ mkdir -p $HOME/.kube
bconfiden2@h01:~$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
bconfiden2@h01:~$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

kubectl로 현재 클러스터의 노드 상황을 확인해보면, 컨트롤 플레인 하나가 등록되어있다.
```bash
bconfiden2@h01:~$ kubectl get nodes
NAME      STATUS     ROLES           AGE    VERSION
h01       NotReady   control-plane   4m8s   v1.26.1
```
<br>

## 노드 설정

아래의 내용은 모든 워커 노드들에 동일하게 적용된다.

위에 등장했던 토큰과 해시값을 이용하여 클러스터에 노드를 조인시킨다.
```bash
bconfiden2@h02:~$ sudo kubeadm join 222.111.164.42:6443 --token 74xi2q.60oy3vj9b46rb20h --discovery-token-ca-cert-hash sha256:0f980e18b8a9e687f7d82d60025d661626f198b6070172bc42e5f908e8323acc
[preflight] Running pre-flight checks
[preflight] Reading configuration from the cluster...
#...
#...
This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.
```

```bash
bconfiden2@h01:~$ kubectl get nodes
NAME      STATUS     ROLES           AGE     VERSION
h01       NotReady   control-plane   18m     v1.26.1
h02       Ready      <none>          109s   v1.26.1
h03       Ready      <none>          103s    v1.26.1
```
<br>

## CNI 네트워크 설정

클러스터 내부적으로 사용할 CNI(Container Network Interface)를 붙여줘야 하는데, 지금은 흔히 사용되는 weave net을 설치한다.

weave 말고 calico, flannel 등도 있으며, CNI 설치는 kubectl을 사용하여 컨트롤 플레인과 워커 노드들에 파드 형태로 띄운다.

컨트롤 플레인에서 수행한다.
```bash
bconfiden2@h01:~$ kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml
serviceaccount/weave-net created
clusterrole.rbac.authorization.k8s.io/weave-net created
clusterrolebinding.rbac.authorization.k8s.io/weave-net created
role.rbac.authorization.k8s.io/weave-net created
rolebinding.rbac.authorization.k8s.io/weave-net created
daemonset.apps/weave-net created
```
```bash
bconfiden2@h01:~$ kubectl get pods -n kube-system | grep weave-net
weave-net-cx8h2                   2/2     Running             0          3m14s
weave-net-j7gg5                   2/2     Running             0          3m14s
weave-net-l662k                   2/2     Running             0          3m14s
```