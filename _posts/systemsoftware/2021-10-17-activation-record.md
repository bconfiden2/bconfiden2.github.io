---
layout: post
title: "Function call, Activation Record"
subtitle: ""
categories: cs
tags: systemsoftware
---

프로그램에서 함수를 호출할 때, 여러 값들에 대한 제어가 필요하다.

함수에서 반환해주는 값, 함수에 넘겨주는 매개변수들, 함수 안에서만 사용되는 지역변수들, 함수가 끝나고 다시 돌아올 주소 등 많은 값들에 대해 호출부와 피호출부에서 값에 접근할 수 있어야 한다.

이를 위해서 각 함수마다 Activation Record 를 구성하여서 스택에 올려주고, 함수가 종료되면 스택에서 해당 값들을 빼주는 방식으로 동작한다.

<br>

## Activation Record

메모리의 스택 영역에 올라가며, Stack Frame, Activation Frame 이라고도 부른다.

어떤 함수가 호출되는 순간에만 사용되는 값들로, 함수 호출마다 해당 함수의 activation record 가 스택에 올라간다.

Activation Record 에는 아래와 같은 여러가지 값들이 포함되어 있어서, 프로그램의 실행 흐름을 제어할 수 있도록 한다.

- return address : 함수가 종료된 뒤 돌아갈 주소값이다. 특정 위치에서 JMP 하여 함수에 해당하는 명령어들로 이동하였을텐데, 함수가 종료된 뒤에는 다시 원래 JMP 했던 곳으로 돌아가야 하기 때문이다.

- return value : 함수가 반환할 값이다.

- parameters : 함수가 사용할 매개변수들로, 호출한 쪽의 지역변수, 상수, 전역변수의 값들, 혹은 포인터 등의 주소값들을 함수에서 사용해야 하기 때문이다.

- local variables : 함수 안에서 정의되고 사용되는 지역변수들이다. 지역변수들은 해당 함수 안에서만 접근이 가능하다.

특정 함수의 activation record 에는 이런 값들을 SP(스택 포인터) 레지스터를 활용하여 스택 영역에 할당받고, B 레지스터를 통해서만 함수 내에서 접근하기 때문에 각각의 지역성이 보장된다.

<br>

## Execution Stack

함수가 계속 호출되면 스택영역에 각 함수들의 Activation Record 들이 쌓이게 되고, 그 중 스택의 top 에서 실행중인 함수를 active 하다고 볼 수 있다.

현재 활성화된(실행중인) 함수의 Activation Record 가 B 레지스터에 들어있기 때문에 % 를 사용하여 값들에 접근하고, 실행이 종료되면 자신이 사용하려고 할당받았던 지역변수, 매개변수, 반환값, 반환주소 등의 공간들을 스택에서 해제시킨다.

그러면 스택의 top 에는 직전에 호출되었던 함수가 위치하게 되며, 해당 함수의 Activation Record 들을 B 레지스터에 넣음으로써 함수의 호출과 종료가 이루어진다.

스택 영역에 activation record 들을 배치하는 것이 좋은 이유는, 컴파일(어셈블) 과정에서 주소가 한군데에 딱 지정되는 것이 아니라 실행되면서 스택에 동적으로 지정되기 때문에, 함수를 재귀적으로 호출할 때 발생하는 문제점들을 막을 수 있다.

<br>

## 함수 호출 시

1. 함수를 호출하는 부분에서 먼저 SP-- 를 한번 해서 반환값에 해당하는 공간을 만든다.

2. 만약에 매개변수들이 존재한다면, 각 매개변수에 해당하는 값들을 하나씩 A 레지스터에 넣고 PUSH A 를 통해 스택에 채워놓는다.

3. 매개변수들을 스택에 전부 올렸다면, 돌아올 주소를 RTN 에 설정한 뒤 스택에 푸시한 뒤 함수를 호출하여 JMP 한다.

4. 함수 안에서 명령어를 실행하기 전에 현재 설정돼있던 B 값을 스택에 푸시한 뒤, 해당 스택포인터의 주소를 B에 담는다(active).

5. 지역변수들의 수 만큼 SP-- 로 공간을 만든다.

6. 현재 레지스터값들을 보존하기 위해 PUSHALL 을 사용하여 스택에 전부 집어넣고 함수의 명령어들을 실행한다.

<br>

## 함수 종료 시

1. POPALL 을 사용하여 저장해뒀던 컨텍스트(모든 레지스터의 값들) 정보를 레지스터들에 다시 세팅해준다.

2. 스택포인터 위치를 B레지스터에 들어있는 값으로 옮기고, B레지스터에는 호출 이전에 활성화되었던 함수의 기준점을 넣어준다. B는 active 함수의 기준점을 가리키고 있기 때문에, 기준점 위쪽에 존재하던 지역변수들도 해제하는 효과를 갖는다(SP++).

3. 넣은 값들의 역순으로 뽑아내는 스택의 특성상, 다음 값은 *함수 호출시*의 3번에서 푸시했던 돌아갈 주소가 되므로, 해당 값을 RTN 에 넣고 점프한다.

4. 함수가 종료되고 호출했던 곳의 다음 명령어로 돌아왔지만, 아직 스택의 activation record 에는 매개변수와 반환값들이 해제되지 않았으므로, 매개변수 수 만큼 SP++ 를 시켜준다.

5. 마지막으로 남아있는 반환값을 POP 하여 A 레지스터에 넣고 필요에 맞게 쓰기까지가 함수의 시작부터 종료까지의 과정이다.