---
layout: post
title: "위상 정렬(Topological Sort)과 DAG 구조"
tags: algorithm
---

DAG란 Directed Acyclic Graph의 약자로, 방향성을 가지며 루프를 생성하지 않는 그래프를 의미한다.

사전적 의미는 조금 난해하지만, 비유를 들자면 스타크래프트에서는 특정 건물을 짓기 위해 선행되어야 하는 건물들이 존재하는데, 이런 건물 간의 관계라고도 볼 수 있다.

실제 게임과는 조금 다르더라도, 배럭스를 짓기 위해 커맨드가 필요하고, 팩토리를 짓기 위해서 배럭스와 엔지니어링베이가 필요한 경우도 DAG 구조의 그래프가 된다.

좀 더 와닿는 예시로는 대학교에서의 커리큘럼이 있는데, 아래 그림이 잘 나타내는 것 같아서 가져왔다.

<figure style="display:block; text-align:center;">
  <img src="https://user-images.githubusercontent.com/22045163/90796313-19e8e580-e34a-11ea-99cb-9f3c4a8cbc55.jpg">
  <figcaption style="text-align:center; font-size:12px; color:#808080">
    https://github.com/Seogeurim/Algorithm-practice/blob/master/notes/Graph/TopologicalSort.md
  </figcaption>
</figure>

수학1을 들어야 수학2를 들을 수 있고, 거기에 선형대수까지 들어야만 이산수학 그리고 자료구조를, 이와는 별개로 프로그래밍 - 프로그래밍 언어를 따로 또 들어야만 최종적으로 알고리즘을 들을 수 있는 형태이다.

그래프에 존재하는 노드들의 우선순위를 나타낸다고도 말할 수 있다.

<br>

## 개념


위상정렬은 이러한 DAG 에서 일의 순서를 찾는 알고리즘이다.

즉, 방향 그래프에 존재하는 노드들 간에 선행되어야 하는 순서를 지키면서, 모든 노드들을 순서대로 정렬하는 것이다.

위의 커리큘럼 예시에서 위상 정렬을 수행할 경우에는 ```수학1 - 선형대수 - 프로그래밍 - 수학2 - 프로그래밍언어 - 이산수학 - 자료구조 - 알고리즘```이 되겠다.

방법은 단순한데, 그래프에서 in-degree가 0 인 노드들을 찾아서 하나하나 처리해나가는 것이다.

in-degree가 0이라는 뜻은, 나를 가리키고 있는 노드(선행되어야 하는 노드)가 아무것도 없다는 말과 같기 때문에, 현 시점에서 나는 아무 제약 없이 바로 처리할 수 있다는 뜻이 된다.

그렇다고해서 노드 하나를 처리할 때 마다 매번 모든 노드의 진입 차수를 검사해주는 것은 비효율적이다.

따라서 에지리스트를 입력 받아 단방향 그래프를 구성하는 과정에서, 간선마다 부모 노드의 in-degree를 1씩 증가시켜 최종적으로 모든 노드의 in-degree 값을 저장해놓는다.

이후에는 특정 노드를 처리 완료할 때, 자신이 가리키고 있는 모든 부모 노드들의 각자 in-degree 값을 1씩 감소시킴으로써, 0이 되는 시점에 해당 노드를 처리할 수 있다고 판단하는 식이다.

특정 시점에 in-degree가 0인 노드들이 여러개 있을 경우 그러한 노드들 사이의 순서는, 풀어야 하는 문제에 맞춰서 설정하면 된다(일반적으로는 신경 쓰지 않음).

물론 이런 방식은 모두 그래프가 단방향이고, 비순환적인 DAG 구조여야만 성립한다.

<br>

## 코드

```python
graph = [[] for _ in range(N)]
# 노드별 in-degree 값을 관리할 리스트
indegree = [0 for _ in range(N)]
for e in edges.split('\n'):
    p, q = map(int, e.split())
    # 간선을 한쪽 방향으로 연결해준 뒤
    graph[p].append(q)
    # q 의 in-degree 는 1 증가
    indegree[q] += 1

answer = []
# 아무 조건 없이 수행 가능한(in-degree 가 0인) 노드들부터 시작
q = [i for i,v in enumerate(indegree) if v==0]
while len(q) > 0:
    nq = []
    for cur in q:
        answer.append(cur)
        # 현재 노드와 연결된 다음 노드들을 검사하면서
        for nxt in graph[cur]:
            # 해당 노드의 in-degree를 1 빼줌으로써 현재 노드 완성됐다고 처리
            indegree[nxt] -= 1
            # 해당 노드보다 선행되어야 할 노드들이 전부 처리되었을 경우, 큐에 추가
            if indegree[nxt] == 0:
                nq.append(nxt)
    q = nq
print(answer)
```

<br>

## 예시

<figure style="display:block; text-align:center;">
  <img src="https://onlinejudgeimages.s3-ap-northeast-1.amazonaws.com/problem/14907/1.png">
  <figcaption style="text-align:center; font-size:12px; color:#808080">
    https://www.acmicpc.net/problem/14907
  </figcaption>
</figure>

1. 노드 A를 제외한 나머지 노드들은 전부 누군가 선행되어야 하는 노드들이 있기 때문에 in-degree가 0이 아니므로, A에서 시작한다.

2. A를 처리 완료했기 때문에, 전체 노드들 중 A를 완료함으로써 처리 가능해지는 노드들이 있는지 확인한다.

3. 이는 그래프에서 A가 가리키고 있는 노드 B와 D를 탐색하는 과정에서 각 노드들의 in-degree를 하나씩 지워주고, 인디그리가 0이 되는 경우에 해당한다.

4. A를 처리함으로써 B와 D의 처리가 가능해졌기 때문에, 두개 노드에서 각각 그 다음 노드들을 확인한다. 이 때 B와 D의 처리 순서 자체는 크게 상관쓰지 않는다.

5. B의 처리 과정에서 노드 C의 in-degree가 0이 되어 C를 처리할 수 있게 되었지만, D의 처리가 완료되었다고 해서 바로 노드 E의 처리는 가능하지 않다.

6. 아직 C에서 E로 가는 간선이 있어서, 노드 E의 in-degree가 1이기 때문이다.

7. 따라서 B 덕분에 처리 가능해진 C를 처리하는데, C가 마무리 됨으로써 E가 처리 가능해졌고, F의 경우는 마찬가지로 아직 노드 E가 처리되지 않았기 때문에 대기한다.

8. E의 처리가 완료된 이후에 마지막으로 F가 처리되며, 위상 정렬을 수행한 결과는 A-B-D-C-E-F 가 된다.