---
layout: post
title: "공식 문서 outdated 파일 작업 방식 정리"
tags: k8s
---

공식 문서 한글화 팀은 쿠버네티스 버전이 올라감에 맞춰 변경되는(혹은 기타 이유로 수정되는) 영문 문서를 최대한 맞춰놓으려고 한다.

그러다 보니 영문 문서에는 변경되어있지만 한글 문서는 아직 반영되거나 수정되지 않은 내용들이 존재하는데, 이를 outdated 라고 하며 주기적으로 이들을 처리하기 위한 브랜치를 생성한다.

보통 손석호님(또는 서지훈님)이 브랜치를 만들고, 변경된 문서들엔 어떤것들이 있는지 그리고 어떻게 작업하는지도 간단히 설명해주는 PR을 열어주신다.

예를 들어 현시점(2023/01/09)에서 열린 풀리퀘(https://github.com/kubernetes/website/issues/38458)를 참조하면, dev-1.26-ko.1 브랜치로 작업중인 상황이다.

즉, 이전 브랜치인 dev-1.25-ko.1 과 현재 브랜치인 dev-1.26-ko.1 에서 영문 문서를 비교하게 된다면, 이 사이에 변경되었던 모든 영문 문서들에 대해 추적할 수 있게 된다.

여기서 찾아낸 문서들에 대하여 한글화 작업을 해주면 되는데, 이 때 내가 사용하는 방법은 아래와 같다.

<br>

먼저 내가 작업할 로컬 브랜치를 현재 브랜치(1.26)를 기준으로 하나 따준다.

```bash
git checkout -b [로컬브랜치] [upstream/현재브랜치]
```

```bash
bconfiden2ui-iMac :: ~/kubernetes-io » git checkout -b 0109-outdated upstream/de
v-1.26-ko.1
branch '0109-outdated' set up to track 'upstream/dev-1.26-ko.1'.
새로 만든 '0109-outdated' 브랜치로 전환합니다
```

로컬 브랜치에서 한글 문서를 변경해주고 원격에 푸시할 것이기 때문에, 이 브랜치를 기준으로 변경하려는 한글 문서를 자신이 사용하는 텍스트에디터로 열어준다.

이 때 열린 한글문서는 원격에서의 현재 브랜치를 기준으로 하므로 아직 영문 수정사항들이 반영되지 않은 상태이다.

<br>

다음으로는 이전 브랜치와 현재 브랜치를 git diff 를 사용하여 비교해준다.

변경 문서 부분에 한글 문서가 아닌 영문 문서 경로를 넣어줘야한다는 점을 주의해야 하는데, 한글 문서의 경우 이전과 현재 브랜치가 동일한 상태이기 때문이다.

두 브랜치 사이에는 영문 문서만이 갱신되어있기 때문에, 영문 문서에서 어떤 부분이 추가되거나 제거, 변경되었는지를 같이 확인하면서 한글 문서를 직접 변경하기 위해 같이 띄워놓는다.

```bash
git diff [upstream/이전브랜치] [upstream/현재브랜치] [변경 문서]
```

```bash
bconfiden2ui-iMac :: ~/kubernetes-io » git diff upstream/dev-1.25-ko.1 upstream/dev-1.26-ko.1 content/en/docs/contribute/
diff --git a/content/en/docs/contribute/advanced.md b/content/en/docs/contribute/advanced.md
index b825ad5e2c..c48712729c 100644
--- a/content/en/docs/contribute/advanced.md
+++ b/content/en/docs/contribute/advanced.md
@@ -2,7 +2,7 @@
 title: Advanced contributing
 slug: advanced
 content_type: concept
-weight: 98
+weight: 100
 ---

 <!-- overview -->
...
...
```

<br>

마지막으로는 현재 브랜치의 영문 문서를 텍스트에디터로 같이 켜놓는다.

굳이 필요한 일을 아니지만, 새롭게 추가된 부분이 있다면 복붙을 좀 더 원활하게 하기 위함이다.

뿐만 아니라, 현재 쿠버네티스 한글화 팀은 영문 문서와 한글 문서 간의 라인 수를 동일하게 가져가는 것을 지향하고 있기 때문에, 꼭 git diff로 변경된 사항 뿐만 아니라 다른 점이 있다면 라인을 비교해가면서 수정하기가 용이해진다.

추가적으로 현재 열려있는 outdated 파일에 대한 PR 창도 같이 확인하는데, git diff는 변경된 모든 문서들에 대해 추적하기 때문에 아직 한글화 되지 않은 영문 문서들의 변경사항들도 같이 보여주기 때문이다.

물론 해당 파일을 변경하려고 하다가 없는 것을 확인할 수도 있지만, 은근 번거롭다고 느껴져서 그냥 애초에 PR 창에서 타겟으로 하는 문서들을 순서대로 반영하는 편이다.

결과적으로 나는 현 브랜치의 한글 문서, 영문 문서를 텍스트에디터로 하나씩, git diff를 위한 터미널 하나, 현시점에서의 PR 창 하나까지 총 4개의 창을 모니터 두개에 띄워놓고 작업한다.