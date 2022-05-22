---
layout: post
title: "조건을 만족할때 까지 대기할 수 있는 Condition Variable 큐"
tags: system
---

두개의 쓰레드(메인, 메인에서 생성한 쓰레드)가 있다고 했을 때, 생성된 쓰레드가 완료된 후에 메인이 나머지 일을 하고 싶은 상황이라고 하자.

이 때 만들어진 쓰레드 t1이 일을 수행하다가 끝났을때 어떻게 메인쓰레드에게 알려줄 수 있을지, 그리고 메인쓰레드는 기다리는동안 뭘 하고있을지에 대한 고민이 필요하다.

메인쓰레드가 그 사이에 sleep 상태로 넘어가거나, spin 상태에 놓여 계속 대기하고 있을 수 있기 때문이다.

이러한 내용을 멀티프로세스 환경에서는 fork로 만든 자식 프로세스의 pid에 wait()을 호출하여, 자식이 종료될때까지 대기할 수 있다.

물론 자식프로세스가 wait 하기 전에 먼저 스케줄링 된다면, 자식 프로세스가 다 수행한 뒤 자신의 exit status를 언제든 넘겨줄 수 있는 상태로 넘어갈 것이다.

그러면 다시 부모프로세스의 나머지 실행흐름대로 따라가다가, 자식을 기다리려고 wait을 호출하더라도 Block 되지 않고 바로 나머지 코드들을 실행하고 종료하게 된다.

어찌됐든 프로세스 레벨에서는, exit()과 wait()에 의해서 다른 실행흐름의 상태를 기다릴 수 있다.

그렇다면 멀티쓰레드 환경에서는 이를 어떻게 적용할 수 있을까?
<br>

## Spin based

간단한 방법으로는, 앞서 언급했듯이 메인쓰레드가 스핀 상태에 들어가는 방식이 있다.

모든 쓰레드가 공유할 수 있는 전역변수를 하나 선언함으로써, 자식 쓰레드는 해당 변수(상태값)를 변경함으로써 완료됐다고 표시한다.

그리고 메인쓰레드는 자식쓰레드를 만들어둔 뒤 계속해서 while 루프를 돌며 해당 변수를 점검하고, 자식쓰레드가 변경하는 시점에 빠져나오는 스핀 상태에 들어간다.

```c
volatile int done = 0;

void* child(void* arg)
{
    done = 1;
    return NULL;
}

int main(int argc, char* argv[])
{
    pthread_t c;
    pthread_create(&c, NULL, child, NULL);
    while(done == 0)
        ;
    return 0;
}
```

이 경우 실행 흐름을 제어한다는 목적은 달성할 수 있겠지만, 스핀 상태에서 불필요한 cpu 낭비가 일어나면서 비효율적인 코드가 된다.
<br>

## Condition Variable based

Condition Variable은 쓰레드가 여러개 있는 상황에서, 쓰레드 사이에 신호를 주고받는 방법이 필요한 경우에 사용한다.

이름 때문에 혼동하기 쉬운데, Condition Variable은 조건에 관련된 변수 같은 것이 아닌 그저 쓰레드들이 대기하는 큐라고 생각하면 된다.

즉, 다른 쓰레드가 특정한 조건을 만족시키기를 기다리는 과정에서 CV라는 대기열에 들어가서 기다린다고 볼 수 있다.

```c
int done = 0;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t c = PTHREAD_COND_INITIALIZER;

void thr_exit()
{
    pthread_mutex_lock(&m);
    done = 1;
    pthread_cond_signal(&c);
    pthread_mutex_unlock(&m);
}

void* child(void* arg)
{
    thr_exit();
    return NULL;
}

void thr_join()
{
    pthread_mutex_lock(&m);
    while(done == 0)
    {
        pthread_cond_wait(&c, &m);
    }
    pthread_mutex_unlock(&m);
}

int main(int argc, char* argv[])
{
    pthread_t c;
    pthread_create(&c, NULL, child, NULL);
    thr_join();
    return 0;
}
```

기본적으로 pthread_cond_t 를 제공해주기 때문에, 이를 전역변수로 선언하고 PTHREAD_COND_INITIALIZE 로 초기화하여 사용할 수 있다.

구조체 안에는 내부적으로 큐를 하나 관리하며, pthread_cond_wait() 메써드를 호출하여 쓰레드들이 이 큐에 들어간다.

CV는 조건이 만족되기를 기다리는 곳이기 때문에, 조건이 만족될 경우 큐에 잠들어있는 대기자들을 깨워줘야 하는데, 이는 pthread_cond_signal() 메써드를 제공해준다.

시그널은 CV의 큐에서 sleep 상태의 원소(쓰레드) 하나를 뽑은 뒤, 스케줄러가 사용하는 ready queue에 옮겨줌으로써 해당 쓰레드를 ready 상태로 변경시켜 스케줄링 될 수 있도록 한다.

어떤 쓰레드가 자기가 필요한 조건이 만족되지 않으면 wait을 호출하여 CV에서 기다리다가, 누군가가 만족시킨 뒤 시그널을 통해 레디큐로 보내주면, 다시 일을 할 수 있는 상태로 스케줄링을 대기하게 되는 것이다.

이렇게 wait을 호출할 때 락도 같이 넘겨주고 있는데, 이는 크리티컬 섹션 안에서 락을 잠그고 CV에 sleep 상태로 들어가게 되면 아무도 자신이 원하는 조건을 충족시켜주지 못하는 상황이 발생할 수 있기 때문이다.

즉 락을 걸어놓고 실행을 하다가 CV에 들어가는 시점에 락을 풀어줌으로써, 다른 쓰레드가 문제 없이 각자의 코드를 실행할 수 있게 해주고, 조건이 만족되어 깨어나는 시점에 다시 락을 걸어 점유할 수 있도록 락의 주소를 같이 넘겨주는 것이다.

CV에 들어가면 슬립 상태로 변하기 때문에, 다른 쓰레드가 cpu를 점유할 수 있어서 낭비 역시 줄어든다.

정리하자면, Condition Variable은 쓰레드들이 줄을 서서 자신을 깨워주기를 기다리는 곳이며, 줄에 서는 방법은 wait()로, 다른 쓰레드를 깨우는 방법은 signal()을 사용한다.

이 때 조건에 대해서는 별도의 공유할 수 있는 상태 변수를 통해 체크하고, 줄을 서는 시점과 깨우는 시점이 서로 얽히지 않게 락으로 감싸서 동기화를 잘 시켜야 한다.