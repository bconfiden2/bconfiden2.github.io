---
layout: post
title: "프로세스별로 가상화된 주소 공간과 하드웨어 기반(MMU) 주소 변환"
tags: system
---

프로세스별로 갖는 가상화된 메모리는, 운영체제 단에서 서로 격리되면서 protection 을 만족시키는데, 이를 위해서 하드웨어적으로 MMU라는 장치를 둠으로써 내부적으로 주소 변환을 수행한다.

MMU는 프로세스에서 사용하는 가상 주소를 실제 물리 메모리의 주소로 변환해준다.

소스코드를 번역하면 기계어가 나오고, 그러한 실행파일 안에 해당 프로그램이 접근해서 사용할 여러 주소들이 들어있는데, 이들은 모두 가상메모리 주소라고 할 수 있다.

이 프로그램이 실행되어 메모리로 로딩되더라도 해당 주소값이 똑같이 올라오기 때문에 그렇다.

cpu는 기계적으로 메모리에 접근해서 값을 읽어오기 때문에, 이런 가상메모리 주소를 가져온다.

따라서 이를 실제 물리메모리의 주소로 변환하여서 cpu가 값을 문제없이 가져올 수 있게 해야 하는데, 중간에 MMU가 개입하여 변환해주어 프로그램의 메모리 참조를 실제 매모리 위치로 재지정하는 것이다.

이렇게 설계되어 있기 때문에, 프로그래머들이 프로그램을 짤 때 자신만의 메모리를 가지고 있다는 좋은 착각을 하게 해준다.

우리가 배열 등을 사용할 때, 특정 인덱스의 앞 뒤로 다른 프로세스의 메모리가 있지는 않을지 등, 다른 프로그램에 대한 고민을 할 필요 없게 만들어주기 때문이다.

<br>

고급 언어로 짜여진 ```x = x + 3``` 코드는 아래와 같은 어셈블리 형식으로(실제 x86 어셈블리 코드가 아닌 가상의 LMC 머신을 위한 코드) 변환될 것이다.
```
0: LDA 90
1: ADDA #3
2: STA 90
```

변수 X가 가상메모리에서 90번지에 담겨있는 상태이고, 위의 실행코드는 주소 0번부터 실행하는 상황이라고 가정한다.

우선 PC가 처음에 0번지를 가리키고 있기 때문에 cpu 는 해당 위치에서 실행코드를 fetch해오는데, 이 경우 LDA 90 이 된다.

해당 위치에는 X의 주소(90)로부터 값을 로드해오는 명령어가 있었기 때문에, 메모리의 X 주소로부터 값을 가져와서 A 레지스터에 넣는다.

다시 PC가 가리키고 있는, 실행코드를 담고있는 주소 1번지에서 명령어를 fetch해오고, A 레지스터에 3을 더해주고, 명령어를 2번지에서 가져오고, 90번지에다가 값을 다시 저장하는 등 메모리 참조가 계속해서 발생한다.

사실 이 과정에서 참조한 모든 주소들은 해당 프로그램만의 가상메모리이기 때문에, MMU가 내부적으로 실제 물리메모리 주소로 계속 변환해주고 있어서 가능하다는 것이다.

프로그램이 인식하는 가상메모리는 0번지부터 연속적으로 존재하지만, 실제 물리메모리 상에서는 0번지가 아닌 다른 어딘가에 위치해있다.

이렇게 프로그램을 실행해서 코드를 메모리에 로딩할 때, 가상 메모리의 자체적인 0번 주소를 기준으로 하지 않고 다른 위치를 기준으로 삼는 일련의 과정을 relocation 이라고 한다.

코드 안에 들어있는 가상 주소 영역들을 자체적으로 다 변환시킬 수도ㅜ 있겠지만, 이게 아니라 하드웨어적인 도움을 받아 동적으로 변환하면서 실행.

실행코드의 주소값들을 수정하지 않고 그대로 메모리에 올리는 대신, MMU에 의해 매번 동적으로 주소가 변환된다.

가상메모리의 주소들을 연속된 하나의 공간으로 가정하고, 가상메모리가 갖는 크기도 물리메모리보다 작으며, 각 프로세스들이 갖는 주소 공간의 크기도 같다고 가정해보자.

이런 경우는 굉장히 간단하게, 가상 메모리에 베이스 주소만 더해주면 된다.

예를 들어 0부터 999 까지 사용하는 가상메모리의 주소를, 실제 물리메모리에서는 5000~5999 까지 배치한다고 헀을 때, 베이스 레지스터에 5000 값을 세팅하면, 매번 베이스값만 더해줌으로써 변환이 일어나게 된다.

또한 바운드 레지스터에는 1000 을 세팅함으로써, 프로그램에서 999를 넘어가는 주소를 참조할 경우 예외를 발생시킨다.

<br>

이런 주소 변환을 위한 MMU의 하드웨어적인 요구사항들은 아래와 같다.

1. cpu의 듀얼 모드 지원 - 유저 프로그램에서 MMU의 레지스터값(base/bound)을 바꿔버리면 프로텍션의 개념 자체가 박살나버림

2. 베이스/바운드 레지스터 - MMU에서 이러한 레지스터를 사용할 수 있어야 함

3. translation - MMU가 이런 레지스터의 값들을 더하거나, 혹은 인덱스를 초과하는지 등 체크할 수 있어야 함

4. 베이스와 바운드 값에 대한 권한 - 커널(특권) 모드에서 이러한 레지스터 값들을 변경할 수 있어야 사용자 프로그램별로 세팅이 가능함

5. 예외 발생시키기 - 자신이 사용할 수 있는 범위를 넘어갈 경우, 인터럽트를 발생시킴으로써 OS가 해당 문제에 대해 처리할 수 있어야 함

<br>

하드웨어적 요건이 갖춰진다고 하더라도, 하드웨어만으로 가상화를 구현할 수는 없다.

정확한 변환이 일어나고, 발생한 문제에 대해 처리하기 위해서는 운영체제가 관여해야하는데, 이 때의 소프트웨어적인 이슈들은 아래와 같다.

1. 프로그램이 디스크에서 메모리로 로딩되는 시점에, 실제로 어디다가 올릴지 결정하는 reloaction 과정

2. 프로세스가 종료될 때, 메모리도 해제함으로써 다른 프로세스가 사용할 수 있도록 공간 확보 - 커널에서 메모리의 빈 공간을 리스트 형태로 관리

3. 문맥 교환시 변환정보를 같이 교체해줘야 서로 다른 프로세스가 문제 없이 자신의 메모리에 접근. 프로세스별로 베이스/바운드 값을 보존했다가 복원해주기

4. 예외가 발생했을 때(bad load - 자신에게 허락된 공간을 벗어날 경우) MMU가 발생시키는 인터럽트에 대한 처리

그러나 이런 단순한 가상화 기법은 앞서 언급한 여러 가정들을 전제로 하는데, 이런 가정은 사실 비현실적이기 때문에 다른 가상화 기법들이 많이 존재한다.