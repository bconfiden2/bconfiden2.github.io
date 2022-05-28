---
layout: post
title: "badblocks - man page & practices"
tags: linux
---

특정 디바이스의 배드블록들을 검사하는 명령어

## Synopsis

```badblocks [-svwnfBX] [-b block_size] [-c blocks_at_once] [-d read_delay_factor] [-e max_bad_blocks]```

```[-i input_file] [-o output_file] [-p num_passes] [-t test_pattern] device [last_block] [first_block]```

## Description

badblocks는 특정 디바이스(디스크 파티션)에 존재하는 배드블록들을 찾기 위해 사용된다.

이 때 디바이스는 /dev/sda1 과 같은 장치 파일을 의미하며, first block과 last block을 넣어줌으로써 디스크의 특정한 구간들의 블록만 검사할 수도 있다.

first block은 옵션이며, last block은 명시하지 않을 경우 기본적으로 해당 디바이스의 마지막 블록을 사용하기 때문에 사실상 옵션과도 비슷한 느낌이다.

만약 badblocks 의 결과를 가지고 e2fsck나 mke2fs에 넘겨줄 경우, 블록 사이즈를 정확하게 명시하는 것이 중요하다.

블록의 수가 파일시스템이 사용하는 블록 사이즈의 크기에 굉장히 의존적이기 때문이다.

그렇기 때문에 badblocks 명령어를 직접적으로 사용하기보다는, e2fsck 나 mke2fs 같은 프로그램의 -c 옵션을 같이 사용하는 것이 좋다.

## Options

- ```-b [block size]```<br>
블록의 사이즈를 바이트 단위로 명세하며, 디폴트값은 1024 이다.

- ```-c [num blocks]```<br>
한번에 검사하는 블록의 수로, 디폴트값은 64 이다.

- ```-d [delay factor]```<br>
이 옵션과 함께 양의 정수가 주어질 경우, 이는 read가 수행되는데 걸린 시간에 대한 비율이 되며, read를 수행하는데 아무런 에러가 발생하지 않았을 경우 배드블록이 sleep 하게끔 한다. 예를 들어 값이 100일 경우에는 각 read가 이전에 read할 때 걸렸던 시간의 100퍼센트만큼 지연된다는 뜻이다.

- ```-e [max count]```<br>
테스트를 종료하기까지의 최대 배드블록의 수를 지정하며, 디폴트는 0으로 블록의 수에 상관없이 지정한 구간을 검사한다.

- ```-n```<br>
non-destructive read-write 모드로 검사를 수행한다. 디폴트는(read only).

- ```-w```<br>
non-destructive write 모드로 검사를 수행한다.

- ```-p [num passes]```<br>
디스크 스캔을 num passes 만큼 반복하며, 디폴트 값은 0이다.

- ```-v```<br>
read 에러, write 에러, data corruption 등에 대한 정보들을 표준에러로 출력한다.

- ```-s```<br>
디스크를 검사해나가면서 발견한 배드블록들의 수와, 진행 상황을 퍼센티지로 출력해준다. 만약 -p 나 -w 같은 옵션이 주어졌다면 동일한 디스크에 대해 여러번 검사할 수 있음을 주의해야 한다.

- ```o [output file]```<br>
배드블록들의 리스트를 명시된 파일로 저장한다. 이 옵션이 없을 경우에는 표준출력으로 내보내며, 출력 포맷은 e2fsck나 mke2fs의 -l 옵션에 사용할 수 있도록 맞춰져있다.

- ```i [input file]```<br>
기존의 배드블록 리스트들에 대한 파일을 입력으로 줄 경우, 해당 블록들을 검사하지 않고 넘어간다. 파일명이 아닌 - 를 넣을 경우 배드블록 리스트를 표준입력으로부터 받아온다.


## Example

```bash
# -s 옵션으로 진행상황과 현재까지 발견된 배드블록 수 출력
bconfiden2@h01:~$ sudo badblocks -s /dev/nvme0n1p2
Checking for bad blocks (read-only test):   6.60% done, 0:47 elapsed. (0/0/0 errors)
```

```bash
# 검사 3회 반복, -v 로 정보 출력
bconfiden2@h01:~$ sudo badblocks -v -c 32 -p 3 /dev/nvme0n1p1
Checking blocks 0 to 524287
Checking for bad blocks (read-only test): done                                                 
Pass completed, 0 bad blocks found. (0/0/0 errors)
Checking blocks 0 to 524287
Checking for bad blocks (read-only test): done                                                 
Pass completed, 0 bad blocks found. (0/0/0 errors)
Checking blocks 0 to 524287
Checking for bad blocks (read-only test): done                                                 
Pass completed, 0 bad blocks found. (0/0/0 errors)
```

```bash
# /dev/sda 장치의 3000 부터 4000 까지 블록들을 총 2번 검사
bconfiden2@h01:~$ sudo badblocks -v -p 2 /dev/sda 4000 3000
Checking blocks 3000 to 4000
Checking for bad blocks (read-only test): done                                                 
Pass completed, 0 bad blocks found. (0/0/0 errors)
Checking blocks 3000 to 4000
Checking for bad blocks (read-only test): done                                                 
Pass completed, 0 bad blocks found. (0/0/0 errors)
```

```bash
# 검사 결과 나온 배드블록들을 bb-out 이라는 파일로 저장, 배드블록이 없어서 아무것도 뜨지 않음..
bconfiden2@h01:~$ sudo badblocks -o bb-out /dev/nvme0n1p1
bconfiden2@h01:~$ cat bb-out
```