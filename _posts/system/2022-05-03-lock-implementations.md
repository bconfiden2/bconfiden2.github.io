---
layout: post
title: "Spinning 기반 Lock 구현 방법들 - Test-And-Set, Fetch-And-Add"
tags: system
---

락을 평가하는 지표로는 아래와 같은 3가지가 있다.
1. Correctness
락이 올바르게 작동하는지에 대한 여부로, 크리티컬 섹션에서 하려고 하는 일이 여러 쓰레드들 간에 상호 배제적으로 동작하는지이다.
해당 섹션에 항상 하나의 쓰레드만이 진입하게끔 락이 구현되었고, 그러면서도 최소한 쓰레드 하나는 계속 진행이 되게 함으로써 데드락에 걸리지 않게 해야 한다.

2. Fairness.
쓰레드가 락을 얻지 못하면 풀릴 때 까지 기다려야 하는데, 쓰레드들이 이렇게 무작정 기다리는 시간이 균등해야한다.
즉, 자기가 크리티컬 섹션에 도착한 시간부터 락을 얻기까지, 락을 기다리는 시간이 여러 쓰레드들 간에 공평하게 이루어져야 한다.

3. Performance.
마지막으로, 아무리 경쟁조건을 해결하고 공평하게 나눠주더라도, 그로 인해 작업 속도가 너무 느려지면 안되기 때문에 성능 역시 중요하다.

이런 조건들이 있음을 인지하고, 다양한 락 구현 방법들에 대해 알아보자.

<br>

## Interrupt

쓰레드가 크리티컬 섹션의 코드를 실행중인 상황에서, 인터럽트가 걸려서 그 흐름이 끊기면서 문제가 발생하기 때문에, 애초에 크리티컬 섹션에 진입하기 전에 인터럽트를 꺼버려서 그런 일이 일어나지 않게 하는 방법이 있다.

크리티컬 섹션의 코드를 모두 실행하고 난 뒤에 인터럽트를 다시 켜줌으로써 다른 쓰레드들과 경쟁조건을 해결하는 것이다.

물론 이런 방법이 기본적으로 동작은 하지만, 인터럽트를 키고 끄는 것은 privileged 명령어들이라 유저프로그램에서는 구현이 안된다는 점에서 한계가 있다.

더욱 치명적인 것은, cpu가 여러개 존재하는 멀티프로세서 환경에서는 동작하지 않는 방법이라는 점이다.

특정 쓰레드가 cpu1에서 실행되는 상황에서, cpu1의 인터럽트는 끈다고 하더라도 cpu2의 인터럽트까지 꺼지는 것은 아니기 때문에 다른 쓰레드에서 접근하는 일이 발생하기 때문이다.

그래서 쓰레드가 여러 cpu에서 나뉘어 실행되고 있었다면, 단순히 인터럽트만 끈다고 해서 락이 제대로 동작하지 않으므로 Correctness 부터 만족시키지 못한다.

또한 인터럽트는 수많은 장치들이 자신의 상태 등을 알리는 수단으로써 활용하는 신호이기 때문에, 문제가 발생할 여지가 생긴다.

크리티컬 섹션이 길어지면 그만큼 인터럽트 꺼져있는 시간이 길어지기 때문이다.

<br>

## 단순한 LD, ST

어셈블리 명령어들 중에 기본적으로 메모리에서 값을 읽어오고, 레지스터값을 메모리에 쓰는 LD/ST 명령어만을 활용한 락 구현 방법이 있다.

우선 lock_t 라는 구조체 안에 현재 락이 걸려있는지 아닌지에 대한 상태값만이 존재하는 락을 만든다.

쓰레드가 크리티컬 섹션 진입 전에 락을 걸려고 할 경우에는, lock 을 호출함으로써 현재 락이 걸려있다면(LD) 무한 대기하다가, 락이 걸려있지 않으면 내가 락을 걸어버리는(ST) 방식이다.

락을 해제 시킬 때는 그냥 이 플래그를 0 으로 세팅해서 다른 쓰레드가 무한 대기하다가 락을 가져갈 수 있도록 한다.

```c
typedef struct __lock_t {
    int flag;
} lock_t;

void lock(lock_t* mutex) {
    while(mutex->flag == 1)
        ;
    mutex->flag = 1;
}

void unlock(lock_t* mutex) {
    mutex->flag = 0;
}
```

이렇게 구현할 경우, 크리티컬 섹션에서 발생하는 경쟁 조건 문제는 해결할 수 있다.

T1에서 락을 걸어놓으면 T2로 문맥교환이 발생하더라도, 락을 걸려고 하는 과정에서 T1이 다시 락을 풀때까지 T2는 무한 루프를 돌 수 밖에 없기 때문이다.

결국에는 다시 T1으로 돌아와서, 남은 명령어를 수행하고 락을 풀게 되면 그제서야 T2가 락을 걸고 자기 일을 수행하게 된다.

그러나 이런 구현 방식은, 유저 프로그램에서의 경쟁조건은 해결했지만, 락을 거는 지점(lock 함수)에서 경쟁 조건이 발생할 수 있다.

LD나 ST 등의 명령어가 아토믹하지 않기 때문에, while문을 빠져나와서 플래그 값을 세팅하기 직전에 인터럽트가 걸리면, 쓰레드 간에 락이 제대로 걸리지 않은 상태로 넘어가기 떄문이다.

<br>

## Test & Set

그래서 하드웨어적으로 지원되는 Test & Set 명령어를 사용한다.

이는 LD와 ST를 합한 명령어로써, 특정 메모리의 값을 레지스터로 가져옴과 동시에 레지스터에 있던 값은 해당 메모리 위치에 써버리는 명령어이다.

즉 메모리와 레지스터 사이에 값을 스왑하는 과정이 아토믹하게 진행된다고 볼 수 있다.

아래는 Test and Set 명령어가 하드웨어적으로 동작하는 방식을 c 형식으로 표현한 코드이다(소프트웨어적 동작 아님).

```c
int TestAndSet(int* old_ptr, int new) {
    int old = *old_ptr;
    *old_ptr = new;
    return old;
}
```

이런 아토믹한 명령어를 이용하면, 위의 LD/ST 과정에서 경쟁조건이 걸리던 한계점을 해결할 수 있게 된다.

기존에는 락의 상태를 while문에서 계속 테스트하다가, 조건이 충족되면 플래그 값을 세팅하는 과정이 서로 분리되어 있었는데, test&set을 사용하여 이를 한 덩어리로 만들어 버린다.

```c
typedef struct __lock_t {
    int flag;
} lock_t;

void lock(lock_t* lock) {
    while(TestAndSet(&lock->flag, 1) == 1)
        ;
}

void unlock(lock_t* mutex) {
    mutex->flag = 0;
}
```

기존에 락이 걸려 있지 않아서(0), 자기가 락을 걸 수 있는 경우에는 반환값이 0이기 때문에 while 문을 바로 빠져나온다.

그러나 원래 1(락이 걸려있음)이었는데, 거기다가 자기가 1로 세팅하려고 하는 경우에는 반환값 1을 받아와 루프를 못빠져나오고 계속 스핀상태에 놓임으로써, 다른 쓰레드가 락을 풀 때 까지 대기한다.

이렇게 현재 락의 상태와 플래그 값 갱신을 원클락에 해결하면서, LD/ST에서 발생하던 경쟁조건 문제가 해결되는 것이다.

Test & Set과 비슷한 계열(유사한 방식으로 동작)의 명령어로는 Compare & Swap 과 Load-Linked & Store-Conditional 등이 있다.

이러한 방식들은 쓰레드간 mutual exclusion 이나 deadlock 문제는 해결헀지만, 스케줄러는 락의 상태를 고려하지 않기 때문에 특정 쓰레드의 starvation 현상을 해결해주지는 못한다.

어떤 쓰레드가 자기의 사용시간을 다 쓰기 전에 계속 락을 걸어버리고 넘기면, 다른 쓰레드들은 자신이 할당받은 시간을 계속 스핀 상태에 놓여있어야 하기 때문이다.

<br>

## Fetch & Add

스핀 상태 때문에 Fairness를 너무 만족시키지 못하는 문제를 해결하기 위하여 Fetch And Add 방식이 등장하였다.

우선 명령어의 동작 방식을 c 스타일로 확인하면 아래와 같다.
```c
int FetchAndAdd(int* ptr) {
    int old = *ptr;
    *ptr = old + 1;
    return old;
}
```

이 명령어는 값을 읽어온 뒤, 해당 값에 1을 더해 다시 저장해놓는다.

마치 은행에서 번호표 발급 버튼을 누를때마다, 이번 번호표가 출력된 뒤에 기기 내부적으로는 다음 번호표에 해당하는 1 증가된 값이 세팅되는 것과 비슷한 개념이다.

fetch 할 경우 값이 하나씩 증가하기 때문에, 쓰레드들이 각자 자기 순서에 해당하는 번호랑 일치할 때 까지 기다리는 방식이다.

```c
typedef struct __lock_t {
    int ticket;
    int turn;
} lock_t;

void lock(lock_t* lock) {
    int myturn = FetchAndAdd(&lock->ticket);
    while(lock->turn != myturn)
        ;
}

void unlock(lock_t* lock) {
    FetchAndAdd(&lock->turn);
}
```

락 구조체를 조금 변경하여, 티켓 발생기와 현재 진행중인 순서에 대한 정보를 저장한다.

쓰레드가 락을 걸려고 할 때에는 fetch 함으로써 티켓을 하나 받아오고, 현재 turn 값이 내가 가진 티켓값과 같아질 때 까지 스핀 상태에 들어가는 것이다.

그리고 언락시에는 나의 서비스가 다 종료되었으니 turn 값을 하나 증가시킴으로써 다음 티켓을 가진 쓰레드가 락을 걸면서 루프를 빠젼와 진행할 수 있게 한다.

먼저 도착하여 대기하던 쓰레드부터 먼저 처리해주는 방식이기 때문에 공평하다고 볼 수 있고 Fairness 역시 만족시키며 starvation 현상을 해결한다.

그러나 자신의 턴을 기다리는 과정에서 스핀이 포함되기 때문에, 여전히 성능적으로 효율적이지는 못하다.