---
layout: post
title: "소스코드로 쿠버네티스 직접 빌드하기"
tags: k8s
---

쿠버네티스 공식 레포에 기여할 때 프리뷰 형식으로 확인을 하거나, 컴포넌트 기능을 변경하여 사용하고 싶은 경우 쿠버네티스 클러스터의 핵심 파드들을 직접 빌드해야 한다.

[여기](https://github.com/kubernetes/community/blob/master/contributors/devel/development.md#building-kubernetes-on-a-local-osshell-environment)를 참조하면, 시스템은 8GB 이상의 메모리와 50GB 이상의 디스크 여유 공간을 필요로 하며, gcc와 make를 활용하기 때문에 만약 없을 경우 `apt-get install build-essential`을 통해 설치해놓는다.

우선 쿠버네티스 레포에 있는 소스코드들을 받아온다.

```bash
bconfiden2@h03:~$ git clone https://github.com/kubernetes/kubernetes k8s-src
Cloning into 'k8s-src'...
remote: Enumerating objects: 1369681, done.
remote: Counting objects: 100% (224/224), done.
remote: Compressing objects: 100% (157/157), done.
remote: Total 1369681 (delta 88), reused 85 (delta 65), pack-reused 1369457
Receiving objects: 100% (1369681/1369681), 875.81 MiB | 2.79 MiB/s, done.
Resolving deltas: 100% (988566/988566), done.
Updating files: 100% (23176/23176), done.

bconfiden2@h03:~$ cd k8s-src
bconfiden2@h03:~/k8s-src$ ls
api           cluster             docs    LICENSE   OWNERS          README.md          test
build         cmd                 go.mod  LICENSES  OWNERS_ALIASES  SECURITY_CONTACTS  third_party
CHANGELOG     code-of-conduct.md  go.sum  logo      pkg             staging            vendor
CHANGELOG.md  CONTRIBUTING.md     hack    Makefile  plugin          SUPPORT.md
```

소스코드 뿐만 아니라 깃 정보들도 전부 가져오기 때문에 시간이 오래 걸리는데, shallow나 partial clone을 활용할 수도 있다.

이후에는 사용자 의도에 맞게 코드의 일부를 변경했다고 가정하며, 지금은 간단하게 예를 들어 kubectl help 시 출력되는 문자열을 수정한다.

kubectl의 version.go 파일의 145번째 라인의 Client Version 사이에 Customized를 넣어줬다.

```bash
bconfiden2@h03:~/k8s-src$ vi staging/src/k8s.io/kubectl/pkg/cmd/version/version.go

# Line 145
fmt.Fprintf(o.Out, "Client Customized Version: %s\n", versionInfo.ClientVersion.GitVe    rsion)
```

빌드 자체는 컨테이너 환경을 사용하기 때문에 굉장히 간단한데, 먼저 각종 패키지들을 설치해준다.

```bash
bconfiden2@h03:~/k8s-src$ sudo apt-get install -y socat conntrack
```

[도커를 설치]()하는 과정에서 containerd와 ctr 역시 같이 설치되며, 이후에는 make만 수행해주면 끝!

```bash
bconfiden2@h03:~/k8s-src$ make quick-release
+++ [1017 11:38:32] Verifying Prerequisites....
+++ [1017 11:38:33] Building Docker image kube-build:build-a54a9432d7-5-v1.25.0-go1.19.2-bullseye.0
+++ [1017 11:51:27] Creating data container kube-build-data-a54a9432d7-5-v1.25.0-go1.19.2-bullseye.0
+++ [1017 11:51:48] Syncing sources to container
+++ [1017 11:51:59] Running build command...
+++ [1017 11:52:00] Building go targets for linux/amd64
    k8s.io/kubernetes/cmd/kube-proxy (static)
    k8s.io/kubernetes/cmd/kube-apiserver (static)
    k8s.io/kubernetes/cmd/kube-controller-manager (static)
# ...
# ...
# ...
+++ [1017 12:04:40] Docker builds done
+++ [1017 12:04:40] Building tarball: server linux-amd64
+++ [1017 12:05:31] Building tarball: final
+++ [1017 12:05:33] Starting tarball: test linux-amd64
+++ [1017 12:05:33] Waiting on test tarballs
+++ [1017 12:06:22] Building tarball: test portable
```

시간이 약 30분 정도로 오래 걸렸다.

컨테이너에서 빌드한 결과는 호스트OS의 ```_output/release-stage``` 아래에 저장된다.

```bash
# 컨트롤 플레인과 관련된 실행파일들
bconfiden2@h03:~/k8s-src$ ls _output/release-stage/server/linux-amd64/kubernetes/server/bin
apiextensions-apiserver    kube-controller-manager.docker_tag  kube-proxy.docker_tag
kubeadm                    kube-controller-manager.tar         kube-proxy.tar
kube-aggregator            kubectl                             kube-scheduler
kube-apiserver             kubectl-convert                     kube-scheduler.docker_tag
kube-apiserver.docker_tag  kubelet                             kube-scheduler.tar
kube-apiserver.tar         kube-log-runner                     mounter
kube-controller-manager    kube-proxy

# 노드와 관련된 실행파일들
bconfiden2@h03:~/k8s-src$ ls _output/release-stage/node/linux-amd64/kubernetes/node/bin
kubeadm  kubectl  kubectl-convert  kubelet  kube-log-runner  kube-proxy
```

빌드된 실행파일들을 `/usr/bin`에 옮겨 사용한다.

```bash
cd _output/release-stage/server/linux-amd64/kubernetes/server/bin/
sudo cp kubeadm kubectl kubelet /usr/bin/

sudo mkdir -p /etc/kubernetes/manifests
sudo mkdir -p /etc/systemd/system/kubelet.service.d
sudo wget https://raw.githubusercontent.com/kubernetes/release/master/cmd/kubepkg/templates/latest/deb/kubeadm/10-kubeadm.conf -P /etc/systemd/system/kubelet.service.d
sudo wget https://raw.githubusercontent.com/kubernetes/release/master/cmd/kubepkg/templates/latest/deb/kubelet/lib/systemd/system/kubelet.service -P /etc/systemd/system
```

컨테이너 런타임을 containerd 로 설정해준 뒤,

```bash
bconfiden2@h03:~$ sudo vi /etc/containerd/config.toml 
#disabled_plugin=["cri"]  # 해당 부분 주석처리하기

bconfiden2@h03:~$ sudo systemctl restart containerd.service
```
 
containerd를 제어하기 위한 crictl 을 설치한다.

```bash
VERSION="v1.25.0"
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
sudo tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin
rm -f crictl-$VERSION-linux-amd64.tar.gz
```
```bash
# 파일 생성 후 아래 내용 추가
bconfiden2@h03:~$ sudo vi /etc/crictl.yaml
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock

# docker images 처럼 컨테이너 이미지들 확인
bconfiden2@h03:~$ sudo crictl images
IMAGE               TAG                 IMAGE ID            SIZE
```

앞서 빌드되었던 컨테이너 이미지 파일들을 ctr을 사용하여 이미지를 등록해준다.

다만 빌드 시점에 따라 이미지 이름이 매번 달라지기 때문에, `kube-proxy-amd64:버전버전버전` 처럼 뒤에 붙는 버전은 달라질 수 있음을 주의해야 한다.

```bash
# 이미지 등록
sudo ctr -n k8s.io image import kube-proxy.tar
# 이미지 태그 변경해주기
sudo ctr -n k8s.io image tag registry.k8s.io/kube-proxy-amd64:v1.26.0-alpha.2.127_48608cfe60ed3a-dirty registry.k8s.io/kube-proxy:v1.26.0-alpha.2.127 registry.k8s.io/kube-proxy:v1.26.0-alpha.2.127

sudo ctr -n k8s.io image import kube-scheduler.tar
sudo ctr -n k8s.io image tag registry.k8s.io/kube-scheduler-amd64:v1.26.0-alpha.2.127_48608cfe60ed3a-dirty registry.k8s.io/kube-scheduler:v1.26.0-alpha.2.127 registry.k8s.io/kube-proxy:v1.26.0-alpha.2.127

sudo ctr -n k8s.io image import kube-apiserver.tar
sudo ctr -n k8s.io image tag registry.k8s.io/kube-apiserver-amd64:v1.26.0-alpha.2.127_48608cfe60ed3a-dirty registry.k8s.io/kube-apiserver:v1.26.0-alpha.2.127
registry.k8s.io/kube-apiserver:v1.26.0-alpha.2.127

sudo ctr -n k8s.io image import kube-controller-manager.tar
sudo ctr -n k8s.io image tag registry.k8s.io/kube-controller-manager-amd64:v1.26.0-alpha.2.127_48608cfe60ed3a-dirty registry.k8s.io/kube-controller-manager:v1.26.0-alpha.2.127
```
```bash
bconfiden2@h03:~/k8s-src/_output/release-stage/server/linux-amd64/kubernetes/server/bin$ sudo crictl images
IMAGE                                           TAG                                        IMAGE ID            SIZE
registry.k8s.io/kube-apiserver                  v1.26.0-alpha.2.127                        16f6e307b253d       129MB
registry.k8s.io/kube-controller-manager         v1.26.0-alpha.2.127                        0af0bc404f90c       116MB
registry.k8s.io/kube-proxy                      v1.26.0-alpha.2.127                        08eef1e14c091       64.2MB
registry.k8s.io/kube-scheduler                  v1.26.0-alpha.2.127                        712e41e1b09b3       52.9MB
```

최종적으로 등록한 kube-system 관련 이미지들을 사용하여 kubeadm으로 클러스터를 초기화한다.

kubeadm init 에다가, 빌드했던 쿠버네티스 버전을 명시해주면 그 이후로는 평소에 보던 kubeadm이랑 비슷한 메시지가 출력된다.

```bash
bconfiden2@h03:~/k8s-src/_output/release-stage/server/linux-amd64/kubernetes/server/bin$ sudo kubeadm init --kubernetes-version v1.26.0-alpha.2.127
[init] Using Kubernetes version: v1.26.0-alpha.2.127
[preflight] Running pre-flight checks
[preflight] Pulling images required for setting up a Kubernetes cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection

# ...

Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 10.30.113.22:6443 --token j7k18u.vgn00dhwx4l56cd0 \
	--discovery-token-ca-cert-hash sha256:09c4c70e9521fe15e1e0eb21de693df66e152eb41fd1195663d8ac7918e408e6
```

수정해줬던 kubectl version 출력문도 변경되었다!

```bash
bconfiden2@h03:~$ kubectl version --short
Flag --short has been deprecated, and will be removed in the future. The --short output will become the default.
Client Customized Version: v1.26.0-alpha.2.127+48608cfe60ed3a-dirty
Kustomize Version: v4.5.7
Server Version: v1.26.0-alpha.2.127+48608cfe60ed3a-dirty
```