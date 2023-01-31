---
layout: post
title: "깃헙에 푸시된 커밋들을 스쿼시하여 하나의 커밋으로 올리기"
tags: git
---

깃헙에 여러개의 커밋을 푸시해놨지만, 이들을 하나의 커밋으로 깔끔하게 합치고 싶은 경우가 있다.

이럴 때는 커밋을 squash 하면 되는데, 풀리퀘를 스쿼시 머지해서 여러 커밋을 하나의 커밋으로 합쳐주는 것과 비슷하다.

<br>

## squash commit

우선 ```git rebase -i HEAD~N```으로 헤드로부터 N개 전의 커밋으로 이동하는데, -i 옵션을 줌으로써 interactive 하게 사용자가 N개의 커밋 내역들을 확인하고 편집할 수 있게 한다.

예를 들어 3개의 커밋을 하나로 합치려고 하는 경우, HEAD~3 로 3개 커밋을 하기 이전의 깃 상태로 이동하면서 그동안의 내역들을 아래처럼 텍스트 에디터로 띄워준다.

그 전에 우선 ```git log```로 HEAD 가 어딘지 등을 확인하는 것이 좋다.

```bash
commit aa5e99a8ff8c7474b10df342720ea002f3893f2b (HEAD -> rearrange)
Author: bconfiden2 <bconfiden2@naver.com>
Date:   Tue Jul 12 09:41:10 2022 +0900

    add Localizing Kubernetes documentation

commit b1b1cd0ed399e1e1e86f5fc2f40280232fec411a
Author: bconfiden2 <bconfiden2@naver.com>
Date:   Tue Jul 12 09:36:45 2022 +0900

    change weight of Document style

commit 7b18d62fa97604ff05ba61742f0c3189d1cf1d53
Author: bconfiden2 <bconfiden2@naver.com>
Date:   Tue Jul 12 09:35:19 2022 +0900

    add weight to localization_ko
```

현재 rearrange 라는 브랜치의 HEAD를 포함해 이전에 존재하는 3개의 커밋을 하나로 합쳐주기 위해, rebase 를 수행한다.

아래의 pick 어쩌고부터 시작하는 3개 줄은 터미널에 뜬 결과가 아닌 편집기 화면을 복사한 것이며, 3줄이 각각의 커밋을 나타낸다.

```bash
bconfiden2ui-iMac :: ko/docs/contribute » git rebase -i HEAD~3
pick 7b18d62fa9 add weight to localization_ko
pick b1b1cd0ed3 change weight of Document style
pick aa5e99a8ff add Localizing Kubernetes documentation

# Rebase 6d0db84674..aa5e99a8ff onto 6d0db84674 (3 commands)
```

하나의 커밋으로 스쿼시하기 위해서 나머지 2개의 ```pick```을 ```squash```로 편집한 뒤 저장한다.

```bash
pick 7b18d62fa9 add weight to localization_ko
squash b1b1cd0ed3 change weight of Document style
sqaush aa5e99a8ff add Localizing Kubernetes documentation
```

나의 경우 git에서 여는 디폴트 텍스트 에디터를 vi 로 설정해뒀기 때문에 :wq 로 저장해줬고, 그 뒤에 곧바로 다시 편집기 창이 뜬다.

여기서 커밋 메시지를 수정해준다.

```bash
# 커밋 3개가 섞인 결과입니다.
# 1번째 커밋 메시지입니다:

add weight to localization_ko

# 커밋 메시지 #2번입니다:

change weight of Document style

# 커밋 메시지 #3번입니다:

add Localizing Kubernetes documentation

# 변경 사항에 대한 커밋 메시지를 입력하십시오. '#' 문자로 시작하는
# 줄은 무시되고, 메시지를 입력하지 않으면 커밋이 중지됩니다.
#
# 시각:      Tue Jul 12 09:35:19 2022 +0900
#
# 대화형 리베이스 진행 중. 갈 위치는 6d0db84674
# Last commands done (3 commands done):
#    squash b1b1cd0ed3 change weight of Document style
#    squash aa5e99a8ff add Localizing Kubernetes documentation
# 명령이 남아있지 않음.
# 현재 'rearrange' 브랜치를 '6d0db84674' 위로 리베이스하는 중입니다.
#
# 커밋할 변경 사항:
#   새 파일:       content/ko/docs/contribute/localization.md
#   수정함:        content/ko/docs/contribute/localization_ko.md
#   수정함:        content/ko/docs/contribute/style/_index.md
```

squash 로 변경해줬던 커밋들은 pick 해준 커밋에 스쿼시 되며, 커밋 메시지는 마지막에 넣어준대로 설정되며 하나의 커밋으로 변경되었다!

<br>

## force push

내 로컬의 커밋들이나 변경사항이 원격(일반적으로 깃헙)의 상태와 맞지 않는 경우, 로컬의 상태를 강제로 푸시할 때 사용하는 방법이다.

```git push -f``` 혹은 ```git push --force``` 처럼 사용한다.

현재는 로컬에서 기존 커밋과 새로운 커밋을 스쿼시하여 하나의 커밋으로 만들어놨고, 원격에는 기존 커밋들만 존재하기 때문에 이를 합쳐서 푸시하려고 force-push 하고 싶은 상황이다.

만약 force-push 가 아니라 일반적으로 푸시하려고 하면, 아래 그림과 같은 상황이 무한 반복된다.

<img src="https://user-images.githubusercontent.com/58922834/215728265-561cab7f-a8e3-4b75-b0df-8f00614fbaed.png">

커밋을 푸시하려고 할 때 원격과 충돌이 일어나면서 git pull 을 통해 머지한 뒤 다시 푸시하라고 말하기 때문이다.

원격을 땡겨올 경우 로컬과 나뉜 브랜치를 합치게 되면 커밋이 다시 생겨 또 스쿼시를 진행하고, 푸시하려고 하니 원격과 다르다며 또 pull하라고 하는 굴레에 빠지는 것이다.

따라서 로컬의 상태를 원격에 강제로 푸시하는 force-push를 사용하며, 원격 저장소에 있던 내용들이 로컬에 맞게 덮어쓰여지기 때문에 중요한 내용들이 사라질 수도 있어서 조심해야 한다.

