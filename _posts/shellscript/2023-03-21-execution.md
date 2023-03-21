---
layout: post
title: "쉘스크립트의 실행 방식"
tags: shellscript
---

쉘스크립트를 실행할 때는 현재 쉘에서 바로 실행하는 방법과 별도의 새로운 프로세스로 실행하는 방법이 있다.

먼저 새로운 프로세스로써 실행시키는 것은, 배쉬 프로그램을 실행시켜 스크립트를 읽어가게 하거나 스크립트를 실행 가능하게 만들어 직접 실행한다는 것이다.

일반적으로 우리가 스크립트를 실행하는 방식이라고 생각하면 된다.

즉, 아래처럼 쉘의 인자로 스크립트 파일 경로를 넘겨서 실행하거나,

```bash
bconfiden2ui-iMac :: blog/_posts/shellscript » vi test.sh
echo my PID : $$
# 특수 변수 $$ 에 자신의 PID를 담고 있다.

bconfiden2ui-iMac :: blog/_posts/shellscript » bash test.sh
my PID : 3642
# 새롭게 실행된 bash 프로세스의 PID
bconfiden2ui-iMac :: blog/_posts/shellscript » echo $$
3354
# 현재 터미널의 PID
```

스크립트에 실행 권한을 준 뒤에 실행한다.

```bash
bconfiden2ui-iMac :: blog/_posts/shellscript » chmod u+x test.sh
bconfiden2ui-iMac :: blog/_posts/shellscript » ./test.sh
my PID : 3722
# 또다른 새로운 프로세스
```

쉘은 환경변수들 중 PATH에 세팅된 경로들에서만 실행 파일을 찾기 때문에, 실행 시 반드시 ./ 을 붙임으로써 현재 디렉토리 아래에 있는 파일로 인식할 수 있도록 한다.

<br>

현재 쉘 프로세스에서 바로 실행하기 위해서는 source 나 . 을 이용한다.

```bash
bconfiden2ui-iMac :: blog/_posts/shellscript » source test.sh
my PID : 3354
bconfiden2ui-iMac :: blog/_posts/shellscript » . ./test.sh
my PID : 3354
# 둘 다 터미널의 PID와 동일한 값이 찍힘!
```

이런 명령어들은 .bashrc 등의 설정 파일을 수정해준 뒤, 적용시킬 때 사용한 명령어들로 익숙하다.

해당 파일이 sh 확장자를 가지지는 않았지만, 쉘에서 사용할 변수들이나 특정 디렉토리 아래의 다른 파일들을 적용하는 스크립트이기 때문에 

비로그인 쉘을 하나 실행시키면 해당 파일을 참조하여 읽어왔기 때문에, 수정 전 내용들이 기본적으로 적용되어 있다.

그러나 파일을 수정만 하고 source 등으로 현재 쉘에 적용시키지 않으면, 해당 파일은 디스크에 그냥 수정된 채로 남아있을 뿐이다.

따라서 수정된 파일 내용을 현재 터미널에 바로 적용시키기 싶으면, source 나 . 등을 사용하여 현재 쉘 프로세스에서 실행시켜 읽어가게 한다.

<br>

스크립트가 실제로 새로운 프로세스로 실행되는지, 현재 프로세스(터미널)에서 실행되는지 확인하기 위해서 프로세스를 종료하는 스크립트를 짜서 실행해보면 된다.

```bash
bconfiden2ui-iMac :: blog/_posts/shellscript » vi test.sh
exit
```

위 스크립트는 exit 이라는 명령어를 담고 있기 때문에, 프로세스를 종료시킨다.

먼저 bash 를 실행시켜 해당 스크립트를 읽어가게 하면,

```bash
bconfiden2ui-iMac :: blog/_posts/shellscript » bash test.sh
# bash 프로세스가 종료됨 !

bconfiden2ui-iMac :: blog/_posts/shellscript 127 » source test.sh
# 터미널이 종료될 것임
```

새로운 bash 프로세스가 생성되고 해당 프로세스를 exit 하기 때문에 아무 일도 일어나지 않는다.

그러나 해당 스크립트를 source 로 실행시키게 되면, 현재 쉘 프로세스에서 실행되며 exit을 통해 쉘이 종료되며 터미널이 꺼지게 된다.