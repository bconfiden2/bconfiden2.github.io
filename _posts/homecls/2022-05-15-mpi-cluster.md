---
layout: post
title: "MPI 클러스터 설치"
tags: homecls
---

클러스터상에서 특정 프로그램을 돌릴 때, 여러 노드들이 메시지라는 간접적인 방법을 활용해 통신함으로써 각각의 자원들을 공유하듯이 사용할 수 있다.

MPI는 이러한 메시지의 전달 방식에 대한 표준화된 라이브러리로써, 대표적인 병렬(분산) 프로그래밍 도구들 중 하나이다.

설치하는 것은 그렇게 어렵지 않기 때문에 간단하게 집에 있는 홈클러스터에 설치하여 hello world 를 출력해볼 생각이다.
<br>

### MPI 설치

우선 MPI는 표준이기 때문에, 이에 대한 구현체로는 MPICH와 OpenMPI 등이 있는데, 둘 다 apt에서 지원해주고 있다.

클러스터상의 전체 노드들에 mpich의 경우에는 ```sudo apt-get install mpich```, OpenMPI의 경우에는 ```sudo apt-get install libopenmpi-dev openmpi-bin openmpi-doc```와 같이 설치해준다.

앤서블 등을 활용하면 한번에 명령을 보낼 수 있다.

아닐 경우에는 ssh 의 -t 옵션을 사용하여 명령어에 가상 터미널을 붙여 sudo 권한에서 요구하는 비밀번호를 입력할 수 있게 해주면, 매번 ssh 접속해서 설치하고 나오는 번거로움을 피할 수 있다.

```bash
bconfiden2@h01:~$ ssh -t h02 "sudo apt-get install -y mpich"
[sudo] password for bconfiden2:
Reading package lists... Done
Building dependency tree
Reading state information... Done
mpich is already the newest version (3.3.2-2build1).
0 upgraded, 0 newly installed, 0 to remove and 195 not upgraded.
Connection to quoka01 closed.
```

직접 리모트에 접속하지 않더라도, ssh에 넘겨준 sudo 가 필요한 명령어를 실행하기 위한 비밀번호를 입력할 수 있게 되며, 명령을 다 실행한 이후에는 접속이 자동으로 종료되어 다시 로컬 프롬프트로 돌아온 것을 확인할 수 있다.
<br>

### /etc/hosts 설정 & ssh-key 등록 & nfs 마운트

기본적으로 클러스터 내의 각 노드들이 서로의 호스트명을 인식할 수 있어야 하고, ssh key 를 서로의 autorhized_keys에 등록해줘야 한다.

현재 홈클러스터에서는 기본적으로 해당 요구사항들이 다 만족되어있기 때문에, 굳이 따로 설정해줄 필요는 없다.

필요할 경우 ```/etc/hosts```와 ```ssh-keygen``` 등을 활용하면 된다.

MPI 프로그램을 돌릴 때 사용하는 데이터들에 대해서, 각 노드들이 공통적으로 접근할 수 있는 파일시스템이 하나 필요한데, nfs 서버를 하나 만들어서 마운트해갈 수 있다.

즉, 마스터로 사용중인 노드의 특정한 경로를 nfs 서버로 열어준 뒤, 다른 노드들이 동일하게 마운트해가서 데이터를 자유롭게 가져갈 수 있게 한다.

이 요구사항 역시 필요한 경우 앞선 nfs를 활용한 공유 디렉토리 설정하기를 참고하여 세팅해줄 수 있겠다.
<br>

### Hello World 프로그램

설치를 완료했다면, 간단한 Hello World 프로그램을 컴파일해서 mpi 로 실행시켜보자.

```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    // Initialize the MPI environment
    MPI_Init(NULL, NULL);

    // Get the number of processes
    int world_size;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    // Get the rank of the process
    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

    // Get the name of the processor
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;
    MPI_Get_processor_name(processor_name, &name_len);

    // Print off a hello world message
    printf("Hello world from processor %s, rank %d out of %d processors\n",
           processor_name, world_rank, world_size);

    // Finalize the MPI environment.
    MPI_Finalize();
}
```

mpi 프로그램을 컴파일 할 때는, mpicc(C) 혹은 mpicxx(C++) 라는 별도의 컴파일러를 사용해야 한다.

실행은 mpirun 을 사용하며, -n 옵션에 프로세스 개수를, -hosts 옵션으로 실행시킬 노드들을, 그리고 실행 파일을 넘겨주면 된다.

```bash
bconfiden2@h01:~$ mpicc helloworld.c
bconfiden2@h01:~$ ls
a.out   helloworld.c
bconfiden2@h01:~$ mpirun -np 3 -host h01,h02,h03 ./a.out
Hello world from processor h01, rank 0 out of 3 processors
Hello world from processor h02, rank 1 out of 3 processors
Hello world from processor h03, rank 2 out of 3 processors
```