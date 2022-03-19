---
layout: post
title: "콘솔창 텍스트 색깔/속성 지정"
tags: shellscript
---

echo 명령어로 텍스트를 찍을 때, 강조 표시를 하거나 배경색을 다르게 하는 등 표시를 하고 싶을 때는 이스케이프 시퀀스를 사용할 수 있다.

이스케이프 시퀀스는 ```\033[속성1;속성2;...;속성3m 문자열 \033[0m```의 포맷을 갖는다.

그러나 echo 에서는 -e 옵션을 넣어주지 않으면 백슬래시를 문자 그대로 이해하기 때문에 이스케이프 처리가 되지 않으므로, -e 옵션과 반드시 같이 사용한다.

출력할 문자열 뒷부분에 나오는 ```\033[0m```은 지정한 속성과 색깔을 초기화하는 것이기 때문에 넣어주지 않아도 되지만, 뒤이어 나오는 다른 문자열들도 전부 변한다는 사실은 알고 있어야 한다.

속성에 해당하는 대표적인 값들은 아래와 같으며, 다른 속성값들에 대해 확인하고 싶을 경우에는 ```man console_codes```로 맨페이지에서 확인 가능하다.

- 0 : 일반 글씨체(디폴트)
- 1 : 굵게, 볼드체 
- 2 : 반투명 
- 3 : 기울임, 이탤릭체 
- 4 : 밑줄 
- 5 : 깜박거리는 효과
- 텍스트 색깔 지정
    - 30 : 텍스트 - 검정색 
    - 31 : 텍스트 - 빨간색 
    - 32 : 텍스트 - 초록색 
    - 33 : 텍스트 - 노란색 
    - 34 : 텍스트 - 파란색 
    - 35 : 텍스트 - 자홍색 
    - 36 : 텍스트 - 옥색(하늘색) 
    - 37 : 텍스트 - 하양색
- 배경 색깔 지정 
    - 40 : 배경 - 검정색
    - 41 : 배경 - 빨간색
    - 42 : 배경 - 초록색
    - 43 : 배경 - 노란색
    - 44 : 배경 - 파란색
    - 45 : 배경 - 자홍색
    - 46 : 배경 - 옥색(하늘색)
    - 47 : 배경 - 하양색

<br>

하나씩 예시로 살펴보자.

```bash
# 굵은 글씨체(1), 빨간색 텍스트(31), 초록색 배경(42)
echo -e "\033[1;31;42mHello, World\033[0m"
```

```bash
# 깜박거림(5), 노란색 텍스트(33)
echo -e "\033[5;33mHello, World\033[0m"
```

```bash
# 이탤릭체(3), 파란색 배경(44), 자홍색 텍스트(35)
echo -e "\033[3;44;35mHello, World\033[0m"
```

```bash
# 볼드체(1), 이탤릭체(3), 밑줄(4), 노란색 텍스트(33), 하얀색 배경(47)
echo -e "\033[1;3;4;33;47mHello, World\033[0m"
```

매번 이스케이프 시퀀스를 다 작성하기는 굉장히 번거롭기 때문에, 일반적으로는 변수에 미리 지정해놓은 뒤 사용한다.

```bash
BRed='\033[1;31m'
BBlue='\033[1;34m'
OFF='\033[0m'
echo -e "I ${BRed}love ${BBlue}you${OFF}!"
```

빨간 볼드체를 Bred, 파란 볼드체를 BBlue, 속성 초기화를 OFF 라는 변수에 넣어놓음으로써, 해당 변수를 가지고와서 편하게 효과를 넣어줄 수 있다.