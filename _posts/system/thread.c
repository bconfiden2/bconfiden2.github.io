#include <stdio.h>
#include <assert.h>
#include <pthread.h>

void* thread(void* arg)
{
    printf("%s\n", (char*) arg);
    return NULL;
}

int main(int argc, char* argv[])
{
    pthread_t p1, p2;
    int rc;
    printf("Thread main BEGIN\n");
    pthread_create(&p1, NULL, thread, "Thread 1");
    pthread_create(&p2, NULL, thread, "Thread 2");
    pthread_join(p2, NULL);
    pthread_join(p1, NULL);
    printf("Thread main END\n");
    return 0;
}