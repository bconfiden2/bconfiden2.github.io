#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char* argv[])
{
    printf("(pid: %d) main starts\n", (int)getpid());
    int rc = fork();
    if(rc < 0)
    {
        fprintf(stderr, "fork failed!\n");
        exit(1);
    }
    else if(rc == 0)
    {
        printf("(pid: %d) I am child\n", (int)getpid());
    }
    else
    {
        printf("(pid: %d) I am parent of %d\n", (int)getpid(), rc);
    }
}