---
layout: post
title: "변수 사용과 다양한 문자열 처리 방법들"
tags: shellscript
---

쉘스크립트에서 변수는 `변수명=값`의 형태로 사용하며, 할당 연산자 앞뒤로 공백을 허용하지 않는다.

일반적으로 변수 이름은 대문자로 이루어지는 편이지만, 소문자도 상관은 없다.

또한 변수에 들어가는 값들은 모두 문자열이기 떄문에, 따옴표나 쌍따옴표를 붙여야지만 문자열로 인식하는 것은 아니다.

따옴표나 쌍따옴표의 경우는 쉘에서 수행하는 확장의 범위를 제어하는 용도로 사용되기 때문에, 아래 예시처럼 name과 NAME1, NAME2는 동일한 값을 갖는다.

```bash
#!/bin/bash

name=bconfiden2
NAME1="bconfiden2"
NAME2="$name"
NAME3='$name'

echo $name $NAME1 $NAME2 $NAME3
```
```shell
bconfiden2ui-iMac :: blog/_posts/shellscript » bash test.sh
bconfiden2 bconfiden2 bconfiden2 $name
```

<br>

위의 예시에 나와있듯이, 선언된 변수의 값을 가져다 사용하려고 할 때는 변수 앞에 $를 붙여준다.

그러나 my_name 이라는 변수를 사용하고 싶지만, 변수를 참조하려는 위치 뒤에 _ 가 붙어있을 경우 변수명이 어디까지인지 구분하지 못하는 문제가 생길 수 있다.

```bash
#!/bin/bash

my_name=bconfiden2

echo $my_name_live_in_Seoul
echo ${my_name}_live_in_Seoul
```

위의 echo 명령은, my_name_live_in_Seoul 이라는 존재하지 않는 변수를 참조하기 때문에 공백이 출력되며, 의도한 대로 변수를 사용하기 위해서는 아래 명령어처럼 `${변수명}`를 사용하는 것을 권장한다.

<br>

변수를 사용할 때 다양한 방식으로 문자열을 처리할 수 있다.

```bash
#!/bin/bash

NAME=bconfiden2_KSH

# 변수값의 길이 반환
echo len: ${#NAME}

# 변수값을 특정 오프셋 이후부터 반환
# 오프셋은 0부터 시작
echo offset from 3: ${NAME:3}
echo offset from 1 to 1+6 : ${NAME:1:6}

# ${변수명:+value}
# 변수에 값이 존재하면 value를 반환
echo NAME: ${NAME+fakename}

# ${변수명:-value}
# 변수가 없거나 null 이면 value를 반환
AGE=""
echo AGE: ${AGE:-27}

# ${변수명:?value}
# 변수에 값이 존재하면 변수명 반환
# 없거나 null이면 value 출력하면서 에러 발생
echo ${NAME:?error}
echo ${HEIGHT:?error}
```
```shell
bconfiden2ui-iMac :: blog/_posts/shellscript » bash test.sh
len: 14
offset from 3: nfiden2_KSH
offset from 1 to 1+6 : confid
NAME: fakename                  # ${NAME+fakename}
AGE: 27                         # ${AGE:-27}
bconfiden2_KSH                  # ${NAME:?error}
test.sh: line 24: HEIGHT: error # ${HEIGHT:?error}
```

<br>

부분 문자열을 제거할 수도 있다.

| :-: | :-: |
| ${변수명#패턴} | 맨 **앞**부터 검사를 시작하여, 패턴과 매칭되는 가장 짧은 문자열을 **지운다**. |
| ${변수명##패턴} | 맨 **앞**부터 검사를 시작하여, 패턴과 매칭되는 가장 긴 문자열을 **지운다**. |
| ${변수명%패턴} | 맨 **뒤**부터 검사를 시작하여, 패턴과 매칭되는 가장 짧은 문자열을 **지운다**. |
| ${변수명%%패턴} | 맨 **뒤**부터 검사를 시작하여, 패턴과 매칭되는 가장 긴 문자열을 **지운다**. |

```bash
#!/bin/bash

STR1=ab_cd_ef_gh
STR2=helloworldhelloworld

# 맨 앞부터 시작하여, *_ 와 가장 짧게 매칭되는 문자열인 ab_ 를 지운다.
echo ${STR1#*_}
# 맨 앞부터 시작하여, h와 l 사이 한 문자가 있는 형태인 hel 을 지운다.
echo ${STR2#h?l}

# 맨 앞부터 시작하여, *_ 와 가장 길게 매칭되는 문자열인 ab_cd_ef_ 를 지운다.
echo ${STR1##*_}
# 맨 앞부터 시작하여, h로 시작하여 l로 끝나는 가장 긴 문자열인 helloworldhelloworl 을 지운다.
echo ${STR2##h*l}

# 맨 뒤부터 시작하여, f로 시작하며 가장 짧게 매칭되는 문자열인 f_gh 를 지운다.
echo ${STR1%f*}
# 맨 뒤부터 시작하여, w로 시작하여 d로 끝나는 가장 짧은 문자열인 world 를 지운다.
echo ${STR2%w*d}

# 맨 뒤부터 시작하여, f로 시작하며 가장 길게 매칭되는 문자열인 f_gh 를 지운다.
echo ${STR1%%f*}
# 맨 뒤부터 시작하여, w로 시작하여 d로 끝나는 가장 길게 매칭되는 worldhelloworld 를 지운다.
echo ${STR2%%w*d}
```
```shell
bconfiden2ui-iMac :: blog/_posts/shellscript » bash test.sh
cd_ef_gh
loworldhelloworld
gh
d
ab_cd_e
helloworldhello
ab_cd_e
hello
```

다만 변수의 중간부터 매칭되는 문자열에 대해서는 지우지 못한다는 점을 주의한다.