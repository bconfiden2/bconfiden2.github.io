---
layout: post
title:  "[쉘스크립트] if, 조건문 사용하기"
subtitle:  ""
categories: study
tags: shellscript
---

모든 프로그래밍 문법에서 기본 중의 기본이라고 할 수 있는 조건식에 대해서 알아보자.

우선 쉘스크립트에서 조건문의 형식은 아래와 같은데, 다른 언어들보다 조건문이 굉장히 까탈스럽다.
```bash
if [ expression ]; then
    statements
elif [ expression ]; then
    statements
else
    statements
fi
```

if(elif) 뒤에 반드시 한칸을 띄운 뒤 [ 를, [ 뒤에도 한 칸을 띄우고 조건식을, 조건식 뒤에도 한 칸을 띄운 뒤 ] 를 쳐야 한다.

띄어쓰기를 틀릴 경우 시스템에서 파싱을 할 때 제대로 읽지 못해 에러가 나므로 잘 맞춰야 한다.

<br>

### 산술 비교

이 때 **expression** 부분에 들어갈 조건식에는 다양한 조건들을 걸 수 있다.

먼저 두 변수나 숫자의 값을 비교하는 연산자들이 있다.
```
[ num1 -eq num2 ] : num1 == num2
[ num1 -ne num2 ] : num1 != num2
[ num1 -lt num2 ] : num1 < num2
[ num1 -le num2 ] : num1 <= num2
[ num1 -gt num2 ] : num1 > num2
[ num1 -ge num2 ] : num1 >= num2
```

예를 들어 아래처럼 활용할 수 있다.
```bash
tmp=1
if [ $tmp -eq 1 ]; then
    echo tmp is 1
fi

if [ 1 -lt 3 ]; then
    echo 1 is lower than 3
fi

# output
# tmp is 1
# tmp is lower than 3
```

<br>

### 문자열 비교

아래는 문자열을 비교하는 연산자들이다.
```
[ str1 = str2 ] : 두 문자열이 같다
[ str1 != str2 ] : 두 문자열이 다르다
[ str ] : 문자열이 NULL 이 아닌 경우 True
```

아래처럼 사용할 수 있다.
```bash
lang=kor
if [ $lang = kor ]; then
    echo Korean
fi

lang=eng
if [ $lang != kor ]; then
    echo Not Korean
fi
```

<br>

### 파일 조건

단순히 두 값을 비교하는 것 말고도, 시스템에 존재하는 파일이나 디렉토리 등을 처리하는 조건들도 존재한다.

예를 들어 *~/.profile* 시작파일에서도 *$HOME/.bashrc* 가 존재하면 해당 파일을 읽는 조건문이 존재한다.

이 때 사용 가능한 조건들은 아래와 같다.
```
[ -d file ] : file이 디렉토리면 True
[ -f file ] : file이 파일이면 True
[ -L file ] : file이 심볼릭링크이면 True
[ -e file ] : file이 존재하면 True
[ file1 -nt file2 ] : file1 이 file2 보다 최신 파일이면 True
[ file1 -ot file2 ] : file1 이 file2 보다 오래된 파일이면 True
[ file1 -ef file2 ] : 둘이 같은 파일이면 True
[ -O file ] : 사용자가 file 의 소유자이면 True
[ -G file ] : 사용자 그룹이 file 의 그룹이면 True
```