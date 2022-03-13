---
layout: post
title: "명령어를 실행하기 전에 쉘이 수행하는 다양한 확장들"
tags: shellscript linux
---

터미널에서 명령어를 입력하고 엔터를 눌러 실행할 때, 쉘이 해당 명령어 텍스트에 몇가지 프로세스를 적용한다.

예를 들어 가장 널리 알려진 와일드카드(*)를 사용하는 경우도 이런 프로세스들 중 하나인데, 이를 ```확장```이라고 부른다.

<br>

### 경로명 확장

echo는, 인자로 넘겨준 텍스트를 stdout 에 표시하는 쉘 빌트인 명령어이다.

그러나 아래에서는 * 이라는 텍스트를 넘겨줬음에도 * 을 출력하는 것이 아닌 뭔가 ls의 결과와 비슷한 텍스트를 출력하고 있다.
```bash
bconfiden2ui-iMac :: ~ » echo *
Applications Desktop Documents Downloads Library Movies Music Pictures Public

bconfiden2ui-iMac :: ~ » ls
Applications Documents    Library      Music        Public
Desktop      Downloads    Movies       Pictures
```

와일드카드로써의 * 은 어떤 글자든 상관 없다는 의미를 가지기 때문에, echo 라는 명령어에 인자로써 넘어가기 전에, 텍스트 확장이 일어나면서 인자값 자체가 바뀐 것이다.

```bash
# 대문자로 시작하는 모든 파일을 출력
echo [[:upper:]]*
# .txt 로 끝나는 모든 파일을 출력
echo *.txt
```

이처럼 다양한 방식으로 경로명 확장이 가능하다.

<br>

### 산술 확장

쉘에서는 단순한 계산기와 같은 산술 연산에 대한 확장도 지원하는데, ```$((expression))```과 같은 형태로 사용한다.

연산자는 사칙연산(+, -, *, /)와 모듈러(%), 거듭제곱(**) 등 총 6가지를 쓸 수 있으며, 각 연산자들은 파이썬에서와 동일하다.

산술식 안에서 띄어쓰기의 형태는 상관하지 않고, 여러 연산자들을 중첩하여 사용할 수도 있다.
```bash
bconfiden2ui-iMac :: ~ » echo 100 x 100 x 100 + 5 = $((100**3 + 5))
100 x 100 x 100 + 5 = 1000005
```

<br>

### 중괄호 확장

중괄호는 반복된 패턴을 나타낼 수 있게 하는, 약간 반복문과 비슷하게 동작하는 확장이다.

Preamble 이라고 부르는 앞부분과 Postscript 라고 하는 뒷부분을 통해 특정 범위나 패턴을 표현해서, 그 사이의 값들로 반복한다.

중괄호 안에서 빈칸은 허용되지 않으며, 중괄호 내에 또다른 중괄호 확장을 넣어 중첩시킬 수도 있다.

```bash
bconfiden2ui-iMac :: ~ » echo Hi{1,2,3,4,5}
Hi1 Hi2 Hi3 Hi4 Hi5

bconfiden2ui-iMac :: ~ » echo Hi{1..5}
Hi1 Hi2 Hi3 Hi4 Hi5

bconfiden2ui-iMac :: ~ » echo {A..Z}
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

bconfiden2ui-iMac :: ~ » echo {0{0,1},1{0,1}}
00 01 10 11
```

<br>

### 매개변수 확장

시스템에서 사용하는 환경변수라는 곳에 여러 값들이 저장되어 있는데, $ 를 사용하여 이런 변수들에 대한 확장이 가능하다.

```bash
bconfiden2ui-iMac :: ~ » echo $USER
bconfiden2

bconfiden2ui-iMac :: ~ » echo $HOME
/Users/bconfiden2

cd $HOME    # cd ~  와 동일
```

그래서 자바를 설치한 뒤 JAVA_HOME 이라는 환경변수를 설정해줘야, 어떤 프로그램을 구동하는 쉘스크립트에서 $JAVA_HOME 과 같이 매개변수 확장을 통해 해당 경로에 접근할 수 있게 되는 것이다.

환경변수들 뿐만 아니라, 다른 커맨드라인 명령어의 결과를 확장에 사용할 수도 있고, 이 때 넘겨주는 커맨드라인 명령에 내부적으로도 확장을 사용할 수도 있다.

예를 들어 ssh-add 를 하기 위해 ssh agent 프로그램을 실행시킬 때, ```eval "$(ssh-agent -s)"```와 같이 사용한다.

ssh-agent -s 만 터미널에 입력하면, 환경변수를 설정하거나 echo 를 찍는 등 쉘에서 실행 가능해보이는 명령어의 형태가 출력되는 것을 볼 수 있다.

그렇기 때문에 $(ssh-agent -s) 부분에서 확장이 일어나며 해당 명령어로 치환되고, eval 명령어의 인자로 들어가 실행되는 것이다.

<br>

### 인용 (확장 제어)

쉘이 텍스트 명령어를 확장시킬 때, 사용자가 원치 않는 확장에 대해서는 따옴표 등을 활용해 확장을 제어할 수 있다.

예를 들어 정말로 터미널에 $ 를 출력하고 싶어도, 아무런 표시가 없으면 쉘은 매개변수 확장으로써 인식한다.

특정 텍스트를 쌍따옴표 묶게 되면, 해당 범위 안에 있는 특수 기호들을 전부 단순 문자로만 인식한다.

즉, 중간중간 존재하는 공백, 경로명 확장, 중괄호 확장 등이 무시되고 텍스트 그 자체로써 인식하는데, 경로명에 띄어쓰기가 포함된 경우 쌍따옴표를 반드시 사용해야 한다.

```bash
# test 디렉토리와 directory 디렉토리를 각각 생성
mkdir test directory
# test directory 라는 디렉토리를 생성
mkdir "test directory"
```

그러나 쌍따옴표로 묶어도 ```$   \   ` ``` 의 3가지 문자들은 무시되지 않는다.

매개변수 확장, 산술 확장, 명령어 치환 등은 쌍따옴표 안에 들어가더라도 확장이 발생한다는 뜻인데, 이러한 문자들까지 제어하고 싶을 경우에는 그냥 하나의 따옴표로 묶으면 된다.

```bash
echo $USER $((1+2+3)) repeat{a,b,c} ~/test		# 변수명, 산술, 중괄호, 틸드 확장이 그대로 적용
echo "$USER $((1+2+3)) repeat{a,b,c} ~/test"		# 중괄호와 틸드 확장은 제어
echo '$USER $((1+2+3)) repeat{a,b,c} ~/test'		# 모든 확장이 제어(텍스트 그대로 출력)
```