---
layout: post
title: "바이너리로 containerd 설치하기"
tags: k8s
---

[Getting started with containerd](https://github.com/containerd/containerd/blob/main/docs/getting-started.md) 페이지를 참고하여 진행한다.

<br>

먼저 containerd 바이너리를 다운받고 압축을 푼어준다
```
bconfiden2@h02:~$ sudo tar Cxzvf /usr/local containerd-1.7.13-linux-amd64.tar.gz 
bin/
bin/containerd-shim-runc-v2
bin/ctr
bin/containerd-shim
bin/containerd-shim-runc-v1
bin/containerd
bin/containerd-stress
```

containerd를 systemd의 서비스로 띄울 것이기 때문에, containerd.service 유닛 파일 명세를 복사하여 ```/etc/systemd/system/``` 아래에 작성한다.

아래 내용은 위의 링크에서도 확인할 수 있다.
```
# Copyright The containerd Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
```

systemd 대몬들을 불러들이고 containerd를 시작해준다.
```
sudo systemctl daemon-reload
sudo systemctl enable --now containerd
```

<br>

runc 와 CNI 플러그인도 필요하다.

링크에서 runc 바이너리를 받아서 ```/usr/local/sbin/runc``` 위치에 설치한다.
```
bconfiden2@h02:~$ sudo install -m 755 runc.amd64 /usr/local/sbin/runc
```

CNI 플러그인도 링크를 참고한다.
```
bconfiden2@h02:~$ sudo tar Cxzvf /opt/cni/bin/ cni-plugins-linux-amd64-v1.4.0.tgz
./
./loopback
./bandwidth
./ptp
./vlan
./host-device
./tuning
./vrf
./sbr
./tap
./dhcp
./static
./firewall
./macvlan
./dummy
./bridge
./ipvlan
./portmap
./host-local
```

<br>

containerd는 ```/etc/containerd/config.toml```에 위치한 설정파일을 사용하는데,

자동으로 생성해주지 않기 때문에 아래 명령어를 통하여 디폴트 설정파일을 만들어준다.

```
sudo bash -c 'containerd config default > /etc/containerd/config.toml'
```

/etc/containerd/config.toml의 systemd cgroup 드라이버를 runc 에서 사용하려면, 아래와 같이 SystemdCgroup의 값을 false에서 true로 바꿔준다.
```
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  ...
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true
```

<br>

crictl을 통해 정상적으로 작동하는지 확인해본다.

```
bconfiden2@h02:~$ crictl ps -a
WARN[0000] runtime connect using default endpoints: [unix:///var/run/dockershim.sock unix:///run/containerd/containerd.sock unix:///run/crio/crio.sock unix:///var/run/cri-dockerd.sock]. As the default settings are now deprecated, you should set the endpoint instead. 
WARN[0000] image connect using default endpoints: [unix:///var/run/dockershim.sock unix:///run/containerd/containerd.sock unix:///run/crio/crio.sock unix:///var/run/cri-dockerd.sock]. As the default settings are now deprecated, you should set the endpoint instead. 
E0229 00:30:44.168427   17956 remote_runtime.go:390] "ListContainers with filter from runtime service failed" err="rpc error: code = Unavailable desc = connection error: desc = \"transport: Error while dialing dial unix /var/run/dockershim.sock: connect: no such file or directory\"" filter="&ContainerFilter{Id:,State:nil,PodSandboxId:,LabelSelector:map[string]string{},}"
FATA[0000] listing containers: rpc error: code = Unavailable desc = connection error: desc = "transport: Error while dialing dial unix /var/run/dockershim.sock: connect: no such file or directory"
```

crictl의 런타임 엔드포인트를 지정해주지 않아서 에러가 뜨는 것을 확인할 수 있다.

아래와 같이 crictl의 설정을 세팅해준다.

```
sudo crictl config --set runtime-endpoint=unix:///run/containerd/containerd.sock
```
```
bconfiden2@h02:~$ sudo crictl config --set runtime-endpoint=unix:///run/containerd/containerd.sock
bconfiden2@h02:~$ sudo crictl config --get runtime-endpoint
unix:///run/containerd/containerd.sock

bconfiden2@h02:~$ sudo crictl ps -a
CONTAINER           IMAGE               CREATED             STATE               NAME                ATTEMPT             POD ID              POD
```