---
layout: post
title: "nvidia-smi 트러블 슈팅 - Failed to initialize NVML: Driver/library version mismatch"
tags: linux
---

며칠 전까지만 해도 아무런 문제 없이 GPU를 사용하고 있었는데, 갑자기 아래와 같은 에러 메시지를 뱉으면서 문제가 발생한다.

```bash
bconfiden2@h01:~$ nvidia-smi
Failed to initialize NVML: Driver/library version mismatch

bconfiden2@h01:~$ dmesg | grep NVRM
[2140090.470492] NVRM: API mismatch: the client has the version 470.129.06, but
                 NVRM: this kernel module has the version 470.103.01.  Please
                 NVRM: make sure that this kernel module and all NVIDIA driver
                 NVRM: components have the same version.
```

dmesg 로 메시지를 확인해본 결과, 클라이언트와 커널이 사용하는 버전이 맞지 않아서 발생한 것이라고 한다.

따로 드라이버나 모듈을 설치하지도 않았는데 왜 며칠 전까지만 해도 잘 맞던 버전이 갑자기 맞지 않는다고 할까?

원인은 바로 업데이트를 자동으로 수행하는 unattended-upgrade 가 nvidia 드라이버들을 설치해버렸고, 해당 모듈들을 커널에 로드했기 때문이다. 

이러한 로그는 ```/var/log/unattended-upgrades/unattended-upgrade.log``` 에서 확인할 수 있다.

```bash
bconfiden2@h01:~$ sudo cat /var/log/unattended-upgrades/unattended-upgrade.log
# ...
# ...
2022-05-19 06:58:13,382 INFO Packages that will be upgraded: apport apport-gtk libnvidia-cfg1-470 libnvidia-common-460 libnvidia-common-470 libnvidia-compute-460 libnvidia-compute-470 libnvidia-compute-470:i386 libnvidia-decode-460 libnvidia-decode-470 libnvidia-decode-470:i386 libnvidia-encode-460 libnvidia-encode-470 libnvidia-encode-470:i386 libnvidia-extra-470 libnvidia-fbc1-460 libnvidia-fbc1-470 libnvidia-gl-460 libnvidia-gl-470 libnvidia-gl-470:i386 libnvidia-ifr1-460 libnvidia-ifr1-470 nvidia-compute-utils-460 nvidia-compute-utils-470 nvidia-dkms-460 nvidia-dkms-470 nvidia-driver-460 nvidia-driver-470 nvidia-kernel-common-460 nvidia-kernel-common-470 nvidia-kernel-source-460 nvidia-kernel-source-470 nvidia-utils-460 nvidia-utils-470 python3-apport python3-problem-report xserver-xorg-video-nvidia-460 xserver-xorg-video-nvidia-470
2022-05-19 06:58:13,382 INFO Writing dpkg log to /var/log/unattended-upgrades/unattended-upgrades-dpkg.log
2022-05-19 07:02:26,766 INFO All upgrades installed
```

꼭두새벽부터 자기 혼자 nvidia 모듈들을 업데이트해놨다.. 어이없어

<br>

아무튼 버전 업데이트가 완료되어버린 모듈들을 다시 클라이언트와 맞춰주면 되는데, 커널에 로드된 모듈을 unload 했다가 다시 클라이언트 버전에 맞게 로드하면 된다.

커널 모듈의 의존성을 확인하여 하나씩 아래처럼 rmmod 시키려고 하는데, 어디선가 사용중인 모듈이라 그럴 수 없다는 메시지가 또 뜬다.

```bash
bconfiden2@h01:~$ lsmod | grep nvidia
nvidia_uvm           1036288  0
nvidia_drm             61440  3
nvidia_modeset       1200128  5 nvidia_drm
nvidia              35319808  184 nvidia_uvm,nvidia_modeset
drm_kms_helper        253952  1 nvidia_drm
drm                   557056  7 drm_kms_helper,nvidia,nvidia_drm

bconfiden2@h01:~$ rmmod nvidia_drm
rmmod: ERROR: Module nvidia_drm is in use
```

따라서 해당 모듈을 사용중인 프로세스를 lsof 로 확인하여 강제로 종료시키고 다시 unload 를 수행한다.

```bash
bconfiden2@h01:~$ sudo lsof /dev/nvidia*
COMMAND    PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
Xorg      1383 root  mem    CHR   195,0           506 /dev/nvidia0
Xorg      1383 root  mem    CHR 195,255           505 /dev/nvidiactl
Xorg      1383 root   12u   CHR 195,255      0t0  505 /dev/nvidiactl
Xorg      1383 root   16u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   17u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   18u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   19u   CHR 195,254      0t0  509 /dev/nvidia-modeset
Xorg      1383 root   23u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   24u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   27u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   28u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   29u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   30u   CHR 195,255      0t0  505 /dev/nvidiactl
Xorg      1383 root   31u   CHR 195,254      0t0  509 /dev/nvidia-modeset
Xorg      1383 root   32u   CHR   195,0      0t0  506 /dev/nvidia0
Xorg      1383 root   33u   CHR   195,0      0t0  506 /dev/nvidia0
gnome-she 1545  gdm  mem    CHR 195,255           505 /dev/nvidiactl
gnome-she 1545  gdm  mem    CHR   195,0           506 /dev/nvidia0
gnome-she 1545  gdm   12u   CHR 195,255      0t0  505 /dev/nvidiactl
gnome-she 1545  gdm   13u   CHR 195,254      0t0  509 /dev/nvidia-modeset
gnome-she 1545  gdm   14u   CHR   195,0      0t0  506 /dev/nvidia0
gnome-she 1545  gdm   15u   CHR   195,0      0t0  506 /dev/nvidia0
gnome-she 1545  gdm   18u   CHR 195,254      0t0  509 /dev/nvidia-modeset
gnome-she 1545  gdm   20u   CHR   195,0      0t0  506 /dev/nvidia0
gnome-she 1545  gdm   21u   CHR   195,0      0t0  506 /dev/nvidia0
gnome-she 1545  gdm   22u   CHR   195,0      0t0  506 /dev/nvidia0
gnome-she 1545  gdm   23u   CHR   195,0      0t0  506 /dev/nvidia0
gnome-she 1545  gdm   24u   CHR   195,0      0t0  506 /dev/nvidia0

bconfiden2@h01:~$ sudo kill -9 1545
```

gnome-shell 을 종료시킨 뒤 다시 아래처럼 하나씩 unload 해준다.

```bash
bconfiden2@h01:~$ sudo rmmod nvidia_drm
bconfiden2@h01:~$ rmmod nvidia_modeset
bconfiden2@h01:~$ rmmod nvidia_uvm
bconfiden2@h01:~$ sudo rmmod nvidia
```

이후에 다시 nvidia-smi 를 실행시키면 클라이언트의 버전에 맞게 커널에 모듈이 로드되면서 정상적으로 작동되는 것을 확인할 수 있다.

<br>

추후에 또다시 unattended-upgrade 가 nvidia 드라이버들을 업데이트하는 짓을 방지하기 위해, 해당 패키지들은 업데이트하지 말라고 제외시킬 수 있다.

apt-mark hold 를 사용함으로써 지정한 패키지들에 대해서 자동이나 수동 업그레이드를 막아버린다.

현재 시스템에 nvidia 470 버전이 설치되어있기 때문에 아래와 같은 수많은 470 버전 패키지들을 지정해준다.

```bash
bconfiden2@h01:~$ sudo apt-mark hold nvidia-compute-utils-470 nvidia-dkms-470 nvidia-driver-470 nvidia-kernel-common-470 nvidia-kernel-source-470 nvidia-utils-470 nvidia-modprobe nvidia-prime nvidia-settings
nvidia-compute-utils-470 set on hold.
nvidia-dkms-470 set on hold.
nvidia-driver-470 set on hold.
nvidia-kernel-common-470 set on hold.
nvidia-kernel-source-470 set on hold.
nvidia-utils-470 set on hold.
nvidia-modprobe set on hold.
nvidia-prime set on hold.
nvidia-settings set on hold.
```

```bash
bconfiden2@h01:~$ sudo dpkg --get-selections | grep hold
nvidia-compute-utils-470			hold
nvidia-dkms-470					hold
nvidia-driver-470				hold
nvidia-kernel-common-470			hold
nvidia-kernel-source-470			hold
nvidia-modprobe					hold
nvidia-prime					hold
nvidia-settings					hold
nvidia-utils-470				hold
```