#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

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
        char* args[3];
        args[0] = strdup("wc");
        args[1] = strdup("exec.c");
        args[2] = NULL;
        execvp(args[0], args);
    }
    else
    {
        int wc = wait(NULL);
        printf("(pid: %d) I am parent of %d, wait %d", (int)getpid(), rc, wc);
    }
}