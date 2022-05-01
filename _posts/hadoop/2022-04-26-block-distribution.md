---
layout: post
title: "HDFS에 올라가있는 특정 파일의 블록 분포 상태 확인하기"
tags: hadoop
---

맵리듀스 프로그램을 돌리던 중, 수많은 맵 태스크들이 특정 노드에만 스케줄링되는 킹받는 현상이 관찰되었다.

보자마자 뭔가 블록이 고르게 분포되지 않았을 것 같다는 생각이 들어, 이를 확인할 수 있는 방법을 찾아보았다.

<br>

### hdfs fsck

기본적으로 하둡에서는 ```hdfs fsck``` 커맨드를 제공해준다.

```
사용법 : hdfs fsck <path> [-move | -delete | -openforwrite] [-files [-blcoks [-locations | -racks]]
<path> : 확인할 hdfs 경로 / 파일
-move : 문제가 있는 파일을 /lost+found 로 이동
-delete : 문제가 있는 파일 제거
-openforwrite : write 를 위해 열려진 파일들 출력
-files : 체크한 파일 출력
-blocks : 블록 리포트 출력
-locations : 각 블록들이 위치한 노드를 출력
-racks : 데이터노드가 위치한 랙(네트워크 토폴로지)
```

사실 이 커맨드는 hdfs를 점검하는 명령어로, 누락된 블록이나 레플리카 등의 오류들을 확인하는 명령어이다.

다른 파일시스템들에서의 fsck와는 조금 다르게 하둡에서는 에러를 감지만 하고 따로 수정하지는 않으며, 일반적으로 이러한 복구 등은 네임노드가 자동적으로 수행한다.

fsck 가 보여주는 결과에는 상태, 전체 크기, 해당 경로 아래에 있는 파일들의 개수 등등이 있지만, 그 중에는 각 파일을 구성하는 블록들에 대한 정보도 보여준다.

```bash
bconfiden2@h01:~$ hdfs fsck filename -files -blocks -locations
Connecting to namenode via http://h01:9870/fsck?ugi=bconfiden2&files=1&blocks=1&locations=1&path=%2Fuser%2Fbconfiden2%2Ffilename
FSCK started by bconfiden2 (auth:SIMPLE) from /192.168.0.110 for path /user/bconfiden2/filename at Tue Apr 26 13:59:18 KST 2022

/user/bconfiden2/filename 1941880934 bytes, replicated: replication=2, 15 block(s):  OK
0. BP-1911947081-127.0.1.1-1648005823591:blk_1073743874_3050 len=134217728 Live_repl=2  [DatanodeInfoWithStorage[192.168.0.114:9866,DS-60cc27c4-cae5-42ff-8165-42c31db62d42,DISK], DatanodeInfoWithStorage[192.168.0.110:9866,DS-1291d38b-2544-47e5-8d80-dfc9e002fb59,DISK]]
1. BP-1911947081-127.0.1.1-1648005823591:blk_1073743875_3051 len=134217728 Live_repl=2  [DatanodeInfoWithStorage[192.168.0.112:9866,DS-d8dfa3df-8832-4714-8e29-2379f0707d30,DISK], DatanodeInfoWithStorage[192.168.0.110:9866,DS-1a5fa502-ffe9-4dbc-8809-bd0237188b1d,DISK]]
2. BP-1911947081-127.0.1.1-1648005823591:blk_1073743876_3052 len=134217728 Live_repl=2  [DatanodeInfoWithStorage[192.168.0.111:9866,DS-8f86541d-33c1-4f63-99fd-909c346318a0,DISK], DatanodeInfoWithStorage[192.168.0.110:9866,DS-3f0024d9-0011-4ab4-98cb-e81023a4df47,DISK]]
3. BP-1911947081-127.0.1.1-1648005823591:blk_1073743877_3053 len=134217728 Live_repl=2  [DatanodeInfoWithStorage[192.168.0.110:9866,DS-abcfb278-ab58-41dd-a496-244b9089612c,DISK], DatanodeInfoWithStorage[192.168.0.111:9866,DS-9e5e6e74-1509-4dea-b52f-ae7f541c39b3,DISK]]
4. BP-1911947081-127.0.1.1-1648005823591:blk_1073743878_3054 len=134217728 Live_repl=2  [DatanodeInfoWithStorage[192.168.0.114:9866,DS-720ade49-cafe-4fa7-9d31-cdde2e7de39c,DISK], DatanodeInfoWithStorage[192.168.0.110:9866,DS-1291d38b-2544-47e5-8d80-dfc9e002fb59,DISK]]
5. BP-1911947081-127.0.1.1-1648005823591:blk_1073743879_3055 len=134217728 Live_repl=2  [DatanodeInfoWithStorage[192.168.0.111:9866,DS-4ed35e37-9b5a-48ea-a392-589dbc093519,DISK], DatanodeInfoWithStorage[192.168.0.110:9866,DS-1a5fa502-ffe9-4dbc-8809-bd0237188b1d,DISK]]
# ...
```

fsck 명령어에 -files, -blocks, -locations 옵션을 넣어줌으로써 위와 같은 실행 결과를 볼 수 있다.

이 결과를 표준출력으로 찍어주며, 데이터노드의 위치는 DatanodeInfoWithStorage 뒤에 나와있다.

이 표준출력을 만들어둔 파이썬 스크립트에 표준입력으로 넘겨줌으로써, 각 데이터노드별로 블록이 몇개씩 있는지 간단하게 확인할 수 있다.

<br>

### python script

아래 코드는 범용적으로 쓰지는 못하고, 현재 클러스터 상황에 맞게 어느정도 하드코딩 한 스크립트이다.

클러스터를 구성하는 노드들이 총 5개이며 각각의 주소가 192.168.0 네트워크 안에 있다는 점과, 레플리카가 2로 설정되어있다는 점 등에서 그렇다.

그럴 일은 없겠지만 hdfs 실행파일을 조금 바꿔 fsck가 출력하는 리포트의 메시지를 조금 바꿨을 경우에도 제대로 인식하지 못한다.

```python
import sys, subprocess

nodes = {f"192.168.0.11{i}":0 for i in range(5)}

# 확인하고 싶은 hdfs 파일 경로를 인자값으로 넣어서 실행
if len(sys.argv) <= 1:
    print("Usage: python3 block-report.py [filepath]", file=sys.stderr)
    exit()
filepath = sys.argv[1]

# hdfs fsck 수행한 결과를 가져와서
fsck = subprocess.Popen(['hdfs', 'fsck', filepath, '-files' ,'-blocks', '-locations'],\
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout, stderr = fsck.communicate()
for line in stdout.decode("utf-8").split('\n'):
    if len(line) == 0: continue
    # DatanodeInfoWithStorage 뒤에 나오는 데이터노드 위치 확인
    if '0' <= line[0] <= '9':
        block = line.split('DatanodeInfoWithStorage[')
        nodes[block[1].split(':')[0]] += 1
        nodes[block[2].split(':')[0]] += 1

for node, num in nodes.items():
    print(f"{node} : {num}")
```

아래처럼 실행해본 결과, 해당 파일이 특정 노드에 치우쳐져 있는, 굉장히 불균형하게 퍼져있는 것을 확인할 수 있었다.

약 10GB 정도 되는 파일이고, 블록 사이즈가 128MB 이기 때문에 총 86개 블록인데, 하나의 노드에만 몰리고 나머지 노드들에 레플리카들만이 분산되어 저장된 것으로 보인다.

```bash
bconfiden2@h01:~$ python3 block-report.py deep1b
192.168.0.110 : 86
192.168.0.111 : 20
192.168.0.112 : 26
192.168.0.113 : 19
192.168.0.114 : 21
```