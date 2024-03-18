---
layout: post
title: "쉘스크립트에서 예외나 에러 처리하기"
tags: shellscript
---

쉘스크립트에서의 예외처리는 다른 프로그래밍 언어들과는 조금 다르다.

일반적으로 사용되는 `try-catch` 등의 구문이 제공되지 않기 때문에, 다른 방법들을 사용해야 한다.

## 종료 상태 확인하기

대부분의 유닉스 계열 명령어들은 명령어가 성공적으로 실행되면 종료값 0을 반환한다.

만약 0이 아닌 다른 종료값을 반환하는 경우에는, 종료값에 따른 종료 상태를 확인할 수도 있다.

```bash
#!/bin/bash

function check_cmd_failed() {
    # 종료값이 0 이 아닐 경우 실행
    if [ "$?" -ne 0 ]; then
        echo "명령어 실패"
        # 종료값 1 반환
        exit 1
    fi
}

add 5 7
check_cmd_failed
```
```shell
bconfiden2@h01:~/blog/_posts/shellscript$ bash test.sh 
test.sh: line 9: add: command not found
명령어 실패
```

## set 명령어 사용

`set -e` 옵션을 사용하면 쉘스크립트 처리 중 에러를 만나면 즉시 종료되게 할 수 있다.

만약 해당 옵션이 함수 안에서만 적용되게끔 설정하고 싶다면, 함수가 종료되기 직전 `set +e`를 통해 설정을 다시 바꿔준다.

```bash
#!/bin/bash

set -e

# hi 는 출력되지만, hihi 는 출력되지 않는다
echo hi
add 5 7
echo hihi
```
```shell
bconfiden2@h01:~/blog/_posts/shellscript$ bash test.sh 
hi
test.sh: line 6: add: command not found
```

## trap 명령어 사용

쉘스크립트가 받는 신호에 대해 핸들러 함수를 정의하여 실행되게 할 수 있다.

스크립트가 갑자기 종료되는 경우에도 마무리 또는 정리 작업을 수행한 뒤 종료시키기 위함이다.

```bash
#!/bin/bash

function cleanup() {
    echo "마무리 작업하기!!"
}

trap cleanup EXIT

echo hi
# EXIT 신호를 받으면 cleanup 함수 실행 뒤 종료
exit 0
echo hihi
```
```
bconfiden2@h01:~/blog/_posts/shellscript$ bash test.sh 
hi
마무리 작업하기!!
```

## '||' 연산자를 통한 에러 처리

OR 연산자는 앞의 명령어가 실패했을 때 그 뒤의 명령을 실행한다.

반대로, &&(AND) 연산자의 경우에는 앞의 명령이 성공적으로 실행되어야만 뒤의 명령도 실행한다.

이는 둘 중 하나라도 성공하거나(OR) 둘 다 성공해야만 하는(AND), 즉 다른 프로그래밍 언어에서 조건을 검사하는 로직과 동일하다.

```bash
#!/bin/bash

add 5 7 | echo "add 명령어 실패!!"
```
```shell
bconfiden2@h01:~/blog/_posts/shellscript$ bash test.sh 
add 명령어 실패!!
test.sh: line 3: add: command not found
```

<br>

간혹 `set -e` 를 선언하지 않았음에도 불구하고, 에러 발생 시점에 스크립트가 종료되는 경우도 있다.

만약 해당 쉘스크립트가 다른 스크립트에 의해 호출된 경우, 호출하는 스크립트에 설정된 쉘 옵션을 상속받기 때문에 그럴 수 있다.

쉘 옵션을 확인하기 위해서는 `set -o`를 실행할 수 있다.

이 중 `errexit` 항목이 on 으로 되어있는 경우 `set -e`가 설정되었다고 보면 된다.