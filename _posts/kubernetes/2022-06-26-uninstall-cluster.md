---
layout: post
title: "쿠버네티스 클러스터 지우기"
tags: k8s
---

먼저 클러스터에서 각 노드들을 떼어낸다.

사실 아래 명령어는 진행하지 않아도 무방하지만, 좀 더 속시원하게 처리하고 싶다면 직접 분리를 해주고 초기화를 해주는 것이 마음이 편하다.
```
kubectl drain [노드명] --delete-local-data --force --ignore-daemonsets
kubectl delete node [노드명]
```
<br>

아래의 내용은 컨트롤 플레인을 포함한 모든 노드에 동일하게 적용된다.

kubeadm을 사용하여 만들었던 클러스터는 kubeadm으로 리셋하여 관련된 파일들을 초기화 시켜준다.

이 지점부터 아래의 모든 명령어들은 클러스터를 구성하고 있는 컨트롤 플레인 및 모든 노드들에 동일하게 적용된다.
```
sudo kubeadm reset --force
```
<br>

쿠버네티스와 관련된 패키지들을 깔끔하게 지워준다.

만약 kubelet 등에 대한 자동 업데이트를 막아놨었다면(held) --allow-change-held-packages 옵션을 붙여서 처리한다.
```
sudo apt-get purge -y kubeadm kubectl kubelet kubernetes-cni --allow-change-held-packages
```
```
sudo apt-get autoremove -y
```
<br>

설치 과정에서 바꿔줬던 세팅값들을 초기화해준다.
```bash
sudo vi /etc/fstab
# 주석처리해뒀던 스왑파일 해제하기

# 스왑 공간을 바로 다시 사용해야하는 경우 직접 swapon 처리, 그 외엔 시스템 재부팅 시 알아서 다시 켜짐
sudo swapon [스왑파일]
```
```
sudo swapon -a
sudo rm /etc/modules-load.d/k8s.conf /etc/sysctl.d/k8s.conf
sudo sysctl --system
sudo modprobe overlay -r
sudo modprobe br_netfilter -r
sudo rm /etc/apt/sources.list.d/kubernetes.list*
```

kubeadm reset 과정에서 발생했던 메시지를 잘 살펴보면, reset process does not clean~ 이라고 하며 특정 디렉토리들을 언급한다.

해당 파일들은 자동으로 초기화되지 않기 때문에, 필요할 경우 사용자가 수동으로 처리해줘야 한다.

흔적을 남기고 싶지 않은 경우 아래 파일들을 전부 지워준다.
```
sudo rm -rf ~/.kube
sudo rm -rf /opt/cni
sudo rm -rf /etc/kubernetes /etc/systemd/system/etcd*
sudo rm -rf /var/lib/etcd /var/lib/dockershim /var/lib/kubelet/ /var/run/kubernetes
```
<br>

마지막에 /var/lib/kubelet 을 지우는 과정에서 아래와 같은 에러가 뜰 때가 있다.

```bash
bconfiden2@h01:~$ sudo rm -rf /var/lib/etcd /var/lib/dockershim /var/lib/kubelet/ /var/run/kubernetes
rm: cannot remove '/var/lib/kubelet/pods/e090b2c6-6eeb-42b9-b777-db85923fcd1e/volumes/kubernetes.io~projected/kube-api-access-d97q7': Device or resource busy
rm: cannot remove '/var/lib/kubelet/pods/d830703d-efcb-476c-a50b-e5ce67765d7c/volumes/kubernetes.io~projected/kube-api-access-4mlpj': Device or resource busy
rm: cannot remove '/var/lib/kubelet/pods/d8f6b258-e6b9-435d-8a97-882fbff576f6/volumes/kubernetes.io~projected/kube-api-access-mpb8c': Device or resource busy
```

앞에서 뭔가 지우지 않았거나 하는 경우, kubelet이 정상적으로 종료되지 않으면서 마운트해서 사용중이던 파일들이 해제가 되지 않은 것이다.

아래처럼 하나씩 수동으로 마운트를 풀어주면 문제 없이 지워진다.

```bash
bconfiden2@h01:~$ sudo umount /var/lib/kubelet/pods/e090b2c6-6eeb-42b9-b777-db85923fcd1e/volumes/kubernetes.io~projected/kube-api-access-d97q7
bconfiden2@h01:~$ sudo umount /var/lib/kubelet/pods/d830703d-efcb-476c-a50b-e5ce67765d7c/volumes/kubernetes.io~projected/kube-api-access-4mlpj
bconfiden2@h01:~$ sudo umount /var/lib/kubelet/pods/d8f6b258-e6b9-435d-8a97-882fbff576f6/volumes/kubernetes.io~projected/kube-api-access-mpb8c
```