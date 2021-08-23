---
layout: post
title: "[Kafka] bootstrap.servers 설정"
subtitle: ""
categories: bigdata
tags: kafka
---

Producer, Consumer(혹은 Streams, Connector 등등) 같은 애플리케이션들이 카프카와 통신하기 위해 ```bootstrap.servers```를 설정해줘서 해당 브로커에 접근할 수 있게 된다.

어떻게 bootstrap.servers 에 명시된 브로커들로부터 메시지를 읽고 쓰는지 알아보자.

<br>

## bootstrap.servers 의 역할

예를 들어 카프카 클러스터가 ```node1, node2, node3```로 총 3개의 브로커로 이루어졌고, 프로듀서 애플리케이션에서는 메시지를 Produce 할 때 bootstrap.servers 에 ```node1``` 브로커를 넣어줬다고 하자.

그러나 토픽들은 사실 여러 파티션으로 나뉘어 여러 브로커들에 분산되어 저장되기 때문에, 사실상 node1 에 접근한다고 해도 해당 브로커에서 메시지를 관리하고 있을 가능성이 높지 않다.(~~물론 예시 상황에서는 충분히 가능하지만, 클러스터에 브로커가 매우 많다고 할 때~~)

개별 브로커가 전체 카프카 클러스터의 데이터를 다 가지고 있는 것이 아니기 때문이다.

그렇기 때문에 bootstrap.servers의 역할은, 프로듀서/컨슈머 등이 직접 작업을 하기 위한 브로커가 아닌, 클러스터에 들어가기 위한 입구처럼 이해할 수 있다.

즉, **bootstrap.servers를 통해 카프카 클러스터에서 관리하는 메타데이터에 접근한 뒤, 실제로 메시지를 쓰거나 가져올 수 있는 브로커와 통신**하는 것이다.

카프카는 분산 시스템으로, 리더 파티션으로부터만 읽기와 쓰기 가능하다.

이 리더 파티션은 여러 브로커들 중 어떤 것이든 될 수 있기 때문에, 프로듀서나 컨슈머 같은 클라이언트가 해당 리더 파티션을 찾기 위해서는, 클러스터에서 어떤 것이 리더 역할을 하고 있는지 알아내야 한다.

이 때 bootstrap.servers로 설정된 브로커(```node1```)로 접속한 다음에 리더 파티션에 대한 메타데이터를 요청하고, 반환 받은 리더 파티션의 엔드포인트(```node3```)를 가지고 Produce/Consume을 시행한다.

예를 들어, 단일 노드에서 카프카가 동작하고 있다고 할지라도, bootstrap.servers를 통해 해당 노드에 접속하면, 동일한 노드(자기 자신)의 엔드포인트를 반환받아서 통신한다.

<br>

## bootstrap.servers 의 개수

bootstrap.servers에 하나의 브로커만 넣어줄 수도 있다.

물론 어떤 브로커여도 상관 없이 클러스터에 접근할 수 있기 때문에 해당 브로커를 통해 메타데이터를 받아올 수 있지만, 때마침 그 브로커가 고장이 난 상태용
따라서 bootstrap.servers에 여러개의 브로커를 넣어줌으로써 앞에서부터 순서대로 메타데이터를 요청한다.

예를 들어 클라이언트에서 ```boostrap.servers = node1:9092,node2:9092``` 처럼 설정하였다면, 처음에 ```node1```를 통해 클러스터의 메타데이터를 요청하고, 실패할 경우는 ```node2```에 요청한다. (만약에 node1 으로부터 정상적으로 반환받으면 node2 에는 요청을 하지 않는다.

공식문서에서는 클러스터 내의 모든 브로커를 다 입력할 필요는 없다고 하지만, 그래도 하나보다는 많이 넣어주는 것을 권장한다.

<br>

## 메타데이터

정리하자면, 프로듀서나 컨슈머(혹은 스트림즈, 커넥터 등등)에서 카프카에 요청을 날릴 때 명시해주는 브로커(```bootstrap.servers```)는 그저 카프카 클러스터의 메타데이터를 받아오기 위해 거쳐가는 과정일 뿐이다.

클라이언트가 처음에 bootstrap 브로커와 연결되면, 클러스터에 있는 메타데이터를 받아오고, 그 중 자신이 원하는 토픽의 리더 파티션을 갖고 있는 브로커를 찾아 해당 브로커로 다시 요청을 하는 방식이다.

만약에 리더 파티션을 가진 브로커와 통신하며 작업을 수행하던 중 해당 브로커에 장애가 발생하거나 리더 파티션이 재할당 된 경우에는 메타데이터를 다시 새롭게 요청하여 다른 엔드포인트를 반환받는다.