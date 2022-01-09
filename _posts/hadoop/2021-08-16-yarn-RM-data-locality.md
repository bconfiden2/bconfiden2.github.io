---
layout: post
title: "[YARN] 리소스매니저가 데이터의 지역성을 지키는 방식"
subtitle: ""
categories: bigdata
tags: hadoop
---

YARN ResourceManager 의 디폴트 스케줄러는 Capacity Scheduler인데, 이 스케줄러가 어떻게 data locality를 지키면서 스케줄링을 하는지 궁금해졌다.

CapacityScheduler는 ```Delay Scheduling``` 방식을 통해 태스크들의 locality 를 지키는데, ```node-local -> rack-local -> off-switch``` 로 3단계의 locality constraint 가 있다.

스케줄러는 현재 수준에서의 locality 가 충족되지 않아서 miss 된 opportunity 의 숫자를 세고, 이 카운트가 특정 threshold에 도달할때까지 기다렸다가 다음 수준의 locality로 넘어간다.

간단히 말해서, ```데이터가 존재하는 노드```에 스케줄링을 걸었다가 일정 횟수 이상 미스가 날 경우, 조금이라도 더 데이터에 빠르게 접근할 수 있는 ```동일한 랙의 노드```들에게 스케줄링하고, 그것도 미스가 계속 날 경우 ```다른 랙(off-switch)의 노드```에게 스케줄링 한다는 것이다.

이 때의 threshold 들은 ```etc/hadoop/capacity-scheduler.xml``` 파일에서 아래 프로퍼티로 설정할 수 있다.

---

- **yarn.scheduler.capacity.node-locality-delay** : 스케줄러가 로컬 컨테이너에서 스케줄을 시도했지만 놓친 스케줄링 횟수이다. 전형적으로 클러스터에 있는 노드의 수로 설정되어야 하며, 디폴트 값은 일반적으로 하나의 랙에 들어가는 노드 수인 40개 이다. 만약 -1 로 설정할 경우 

- **yarn.scheduler.capacity.rack-locality-additional-delay** : 위의 node-locality-delay 를 넘어선 추가적인 미스 스케줄링 횟수로, 이를 넘어갈 경우 off-switch 컨테이너들에게 스케줄링을 시도한다. 디폴트값은 -1인데, 이 때 off-switch 컨테이너에게 할당하기 위한 임계값은 *L * C / N* 이 된다. L 은 location(노드/랙)의 수, C 는 요청된 컨테이너의 수, N 은 클러스터의 크기이다.

---

실제로 해당 설정파일을 찾아서 확인해보면 두 프로퍼티가 기본값으로 설정되어있는 것을 확인할 수 있는데, 필요에 맞게 적용할 수 있겠다.

```bash
vi /opt/hadoop/etc/hadoop/capacity-scheduler.xml

...
<property>
    <name>yarn.scheduler.capacity.node-locality-delay</name>
    <value>40</value>
</property>

<property>
    <name>yarn.scheduler.capacity.rack-locality-additional-delay</name>
    <value>-1</value>
</property>
...
```

<br>

리소스매니저의 다른 스케줄러인 FairScheduler도 똑같이 ```노드 -> 같은 랙 -> 다른 랙```의 3단계 과정을 거쳐 locality 를 준수한다.
프로퍼티의 이름과 설정 값의 형식에 조금의 차이는 있다.