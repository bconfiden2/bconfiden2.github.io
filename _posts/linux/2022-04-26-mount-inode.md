---
layout: post
title: "파일시스템이 특정 경로에 마운트될 때 발생하는 일"
tags: linux
---

파일시스템을 마운트하는 것은, 마운트 되고 있는 동안에 바인딩을 유지한다는 뜻이다.

이러한 바인딩은 기존에 존재하던 파일시스템의 특정 경로(mount point)와 새로운 파일시스템의 루트를 엮어주는데, 이 둘은 unmount 되기 전까지 연결된다.

새로운 파일시스템은 마운트 포인트에 해당하는 경로에 있던 파일, 디렉토리, 링크 등의 모든 데이터들을 덮어쓰기 때문에, 마운트 되고 있는 동안에는 기존 파일들에 대해서 접근할 수 없다.

리눅스/유닉스에서의 모든 것들은 파일의 형태로 관리된다.

디렉토리도, 디바이스들도 전부 파일로 취급되는데, 이 말은 사실 파일시스템에서 블록들과 그에 대한 메타데이터를 관리하는 아이노드로 이루어진다는 뜻이다.

아이노드에는 파일 접근 시간, 수정 시간, 링크 수, uid나 gid 등의 속성들을 가지고 있는데, 실제로 파일시스템을 조회하는 명령어인 ls 에서도 확인 가능한 속성들이다.

일반적으로 파일의 경우 아래와 같은 정보들을 담는 아이노드를 통해 디스크의 여러 블록들에 실제 데이터를 담는데, 디렉토리의 경우에도 이와 동일하게 아이노드와 블록으로 구성된다.

```c
struct stat {
    dev_t       st_dev;
    ino_t       st_ino;
    mode_t      st_mode;
    nlink_t     st_nlink;
    uid_t       st_uid;
    gid_t       st_gid;
    dev_t       st_rdev;
    off_t       st_size;
    blksize_t   st_blksize;
    blkcnt_t    st_blocks
    time_t      st_atime;
    time_t      st_mtime;
    time_t      st_ctime;
}
```

다만 디렉토리가 담는 데이터는 해당 경로 아래에 존재하는 다른 경로들에 대한 아이노드 넘버와 경로명 등이 된다.

마운트 포인트의 상위 디렉토리에 해당 경로에 대한 아이노드 넘버를 담고 있기 때문에 실제로 그 경로로써 사용자가 접근할 수 있는 것인데, 만약 이 경로를 새로운 파일시스템의 루트로 마운트할 경우 이 아이노드 넘버가 변경된다.

즉 어떠한 새로운 파일시스템을 특정 경로에다가 마운트한다는 뜻은, 해당 경로의 상위 디렉토리에서 관리하던 블록 정보의 아이노드 번호를 변경하여 다른 파일시스템으로 접근할 수 있게 만든다는 뜻이다.

<br>

아래와 같이 /dev/sda 라는 디스크가 존재하고, sda1 파티션이 마운트되지 않은 상황에 놓여있다.

```bash
bconfiden2@h01:~$ sudo fdisk -l
# ...
Disk /dev/sda: 1.84 TiB, 2000398934016 bytes, 3907029168 sectors
Disk model: WDC WD20SPZX-22U
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: dos
Disk identifier: 0x27d44f46

Device     Boot Start        End    Sectors  Size Id Type
/dev/sda1        2048 3907027438 3907025391  1.8T  7 HPFS/NTFS/exFAT
# ...
```
<br>

루트디렉토리 아래에는 HDD 라는 현재 파일시스템 안에서 생성되어있는 경로가 존재하며, 해당 경로 아래에는 다양한 디렉토리와 파일들이 들어있다.

아이노드 넘버는 ls -i 옵션으로 확인할 수 있는데, 아래와 같이 서로 다른 아이노드 번호들을 가지고 있다.

```bash
# /HDD 의 아이노드번호
bconfiden2@h01:~$ ls -ail / | grep HDD
13762561 drwxr-xr-x   3 root       root             4096 May 28 21:14 HDD

# /HDD 아래의 서브디렉토리나 파일들의 아이노드 번호
bconfiden2@h01:~$ ls -ail /HDD
total 12
13762561 drwxr-xr-x  3 root root 4096 May 28 21:14 .
       2 drwxr-xr-x 23 root root 4096 Feb 17 20:28 ..
13762563 -rw-r--r--  1 root root    0 May 28 21:14 bar
13762564 -rw-r--r--  1 root root    0 May 28 21:14 bconfiden2
13762562 drwxr-xr-x  2 root root 4096 May 28 21:14 foo
```
<br>

이런 상황에서 /HDD 를 마운트 지점으로 잡아 /dev/sda1 라는 새로운 파일시스템을 마운트시킨다.

mount의 경우 시스템콜 형식으로도 제공될 뿐만 아니라 리눅스의 명령어로도 제공되기 때문에, ```sudo mount device dir``` 형태로 실행시킬 수 있다.

어떤 명령어가 시스템콜인지, 명령어인지는 man 페이지 번호가 몇번몇번 존재하는지를 통해 확인해볼 수 있다.

```bash
bconfiden2@h01:/$ sudo mount /dev/sda1 /HDD
bconfiden2@h01:/$ df -h | grep /dev/sda1
/dev/sda1       1.9T  212G  1.7T  12% /HDD
```

<br>

기존의 /HDD 위치에 새로운 파일시스템이 마운트 되었기 때문에, 루트노드가 관리하던 /HDD의 아이노드번호 대신 새로운 번호로써 루트의 디렉토리에 쓰기가 발생하게 된다.

즉 루트디렉토리를 위한 블록에 관리되던 경로와 아이노드번호가 바뀐다는 뜻이다.

따라서 /HDD를 조회할 경우 하위 디렉토리에 있던 내용들도, /dev/sda1를 루트로 삼고 경로를 따라가 해당 파티션에 존재하던 데이터들로 바뀐다.

```
bconfiden2@h01:/$ ls -ail / | grep HDD
       5 drwxrwxrwx   1 root       root             4096 Feb 17 20:29 HDD
bconfiden2@h01:/$ ls -ail /HDD
total 48
     5 drwxrwxrwx  1 root root  4096 Feb 17 20:29  .
     2 drwxr-xr-x 23 root root  4096 Feb 17 20:28  ..
139975 drwxrwxrwx  1 root root  4096 Mar 25  2020  classic
 89206 drwxrwxrwx  1 root root  4096 Sep 12  2020  etc
 10046 drwxrwxrwx  1 root root  4096 Aug 10  2020  movies
140582 drwxrwxrwx  1 root root     0 Apr 11  2020  pictures
```

기존의 파일시스템(마운트 되기 전)에 존재하던 파일들(foo,bar,bconfiden2 등)이 기존의 디스크에서 지워진 상태는 아니며, 다만 파일시스템에서 조회가 불가능한 것일 뿐이다.

/dev/sda1 을 unmount 할 경우 해당 파일들이 다시 /HDD 경로를 통해 조회할 수 있다.