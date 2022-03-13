---
layout: post
title: "smartctl, 하드디스크 SMART 모니터링 도구"
subtitle: ""
categories: devops
tags: linux
---

많은 부품들 중 가장 고장나기 쉬운 것이 디스크인데, 서버들이 RAID 를 구성해서 백업을 하는 이유도 이 때문이다.

데비안 기반의 리눅스 배포판에서는 하드디스크 상태를 모니터링하는 SMART 기능을 활용하는 도구를, ```apt-get install smartmontools```로 설치할 수 있다.

SMART 란 **S**elft **M**onitoring, **A**nalysis, **R**eporting **T**echnology 의 줄임말이다.

따라서 SMART 기능이 없는 디스크는 패키지 안에 있는 smartctl 프로그램을 사용할 수 없지만, 최근 디스크 제조업체들은 반드시 SMART 를 지원한다.

아래는 smartctl 을 실행할 때의 옵션들이며, ```sudo smartctl [옵션] [장치명]```처럼 사용한다.

| 옵션 | 내용 |
| --- | --- |
| --scan | 장착된 디스크들 검사하여 리스트업 |
| -i | 장치의 identity |
| -H | 장치의 SMART health |
| -c | 장치의 SMART capability |
| -A | 장치의 제조사별 attritubte 들과 그 값 |
| -a | 특정 장치에 대한 모든 SMART 정보 제공, i, H, c, A 옵션을 한번에 보여줌 |

<br>

대표적인 attribute 들은 아래와 같으며, 이보다 더 많은 속성들이 있다.

| 속성 | 내용 |
| --- | --- |
| Current_Pending_Sector | 불안정 섹터 |
| Offline_Uncorrectable | 배드 섹터 |
| Power_On_Hours | 하드에 전원이 들어온 시간 |
| Power_Cycle_Count | 전원 ON/OFF 횟수 |
| Power-Off_Retract_Count | 헤드가 플래터에서 벗어난 횟수 |
| Raw_Read_Error_Rate | 물리적 충격으로 인해 디스크로부터 데이터를 정상적으로 읽지 못한 비율 |
| Reallocated_Sector_Ct | 특정 섹터에 에러가 생겨 다른 섹터로 재할당된 횟수 |
| Reallocated_Event_Count | 스페어 섹터로부터 데이터를 읽은 횟수 |
| Seek_Error_Rate | 탐색 오류 비율 |
| Spin_Retry_Count | 최대 rpm 회전에 도달하기 위해 플래터가 회전을 시도하는 횟수 |
| Spin_Up_Time | 플래터가 최대 rpm 까지 회전하는데 걸리는 시간
| Start_Stop_Count | 플래터가 회전하고 정지한 횟수 |
| Temperature_Celsius | 디스크 온도 |
| UDMA_CRC_Error_Count | 디스크 인터페이스를 통해 데이터를 전송하는 과정에서 발생한 CRC 횟수 |

아래는 -A 옵션으로, sda 디스크의 속성값들을 확인해본 결과이다.

```
$ sudo smartctl -A /dev/sda
=== START OF READ SMART DATA SECTION ===
SMART Attributes Data Structure revision number: 16
Vendor Specific SMART Attributes with Thresholds:
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  1 Raw_Read_Error_Rate     0x002f   100   100   051    Pre-fail  Always       -       0
  2 Throughput_Performance  0x0026   252   252   000    Old_age   Always       -       0
  3 Spin_Up_Time            0x0023   094   093   025    Pre-fail  Always       -       1929
  4 Start_Stop_Count        0x0032   098   098   000    Old_age   Always       -       2895
  5 Reallocated_Sector_Ct   0x0033   252   252   010    Pre-fail  Always       -       0
  7 Seek_Error_Rate         0x002e   252   252   051    Old_age   Always       -       0
  8 Seek_Time_Performance   0x0024   252   252   015    Old_age   Offline      -       0
  9 Power_On_Hours          0x0032   100   100   000    Old_age   Always       -       511
 10 Spin_Retry_Count        0x0032   252   252   051    Old_age   Always       -       0
 11 Calibration_Retry_Count 0x0032   100   100   000    Old_age   Always       -       14
 12 Power_Cycle_Count       0x0032   099   099   000    Old_age   Always       -       1022
191 G-Sense_Error_Rate      0x0022   100   100   000    Old_age   Always       -       3784
192 Power-Off_Retract_Count 0x0022   100   100   000    Old_age   Always       -       58
194 Temperature_Celsius     0x0002   064   064   000    Old_age   Always       -       29 (Min/Max 12/44)
195 Hardware_ECC_Recovered  0x003a   100   100   000    Old_age   Always       -       0
196 Reallocated_Event_Count 0x0032   252   252   000    Old_age   Always       -       0
197 Current_Pending_Sector  0x0032   252   252   000    Old_age   Always       -       0
198 Offline_Uncorrectable   0x0030   252   252   000    Old_age   Offline      -       0
199 UDMA_CRC_Error_Count    0x0036   100   100   000    Old_age   Always       -       158
200 Multi_Zone_Error_Rate   0x002a   100   100   000    Old_age   Always       -       1513
223 Load_Retry_Count        0x0032   100   100   000    Old_age   Always       -       14
225 Load_Cycle_Count        0x0032   099   099   000    Old_age   Always       -       15282
```

<br>

간단하게 상태를 체크하기 위해서는 아래처럼 특정 디스크에 -H 옵션을 줄 수 있다.

```
$ sudo smartctl -H [장치명]
smartctl 7.1 2019-12-30 r5022 [x86_64-linux-5.11.0-43-generic] (local build)
Copyright (C) 2002-19, Bruce Allen, Christian Franke, www.smartmontools.org

=== START OF READ SMART DATA SECTION ===
SMART overall-health self-assessment test result: PASSED
```

마지막에 PASSED 라고 뜨더라도 디스크 온도 등에 대한 주의 메시지를 같이 반환할 수도 있다.

이 경우 먼저 서버컴퓨터 자체의 온도를 검사해보는 것도 좋은데, lm-sensors 패키지가 cpu, 보드 등의 온도를 확인할 수 있는 서비스를 제공한다.

아래처럼 패키지를 설치한 뒤, sensors-detect 프로그램을 한번 수행하여 하드웨어들을 쭉 훑어주는데, 이때 yes 를 매번 입력할 필요 없이 엔터만 쳐도 된다.

```
$ sudo apt-get install lm-sensors
$ sudo sensors-detect
$ sensors
acpitz-acpi-0
Adapter: ACPI interface
temp1:        +27.8°C  (crit = +105.0°C)
temp2:        +29.8°C  (crit = +105.0°C)

coretemp-isa-0000
Adapter: ISA adapter
Package id 0:  +30.0°C  (high = +80.0°C, crit = +100.0°C)
Core 0:        +28.0°C  (high = +80.0°C, crit = +100.0°C)
Core 1:        +28.0°C  (high = +80.0°C, crit = +100.0°C)
```

detect 가 완료되면 sensors 명령으로 온도를 확인할 수 있다.