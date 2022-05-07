#include <stdio.h>
#include <pthread.h>

static volatile int counter = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void* test(void* arg)
{
    printf("%s: begin\n", (char*)arg);
    int i;
    for(i = 0 ; i < 10000 ; i++)
    {
        pthread_mutex_lock(&lock);
        counter += 1;
        pthread_mutex_unlock(&lock);
    }
    printf("%s: end\n", (char*)arg);
    return NULL;
}

int main(int argc, char* argv[])
{
    pthread_t t1, t2;
    printf("main: begin, counter = %d\n", counter);
    pthread_create(&t1, NULL, test, "T1");
    pthread_create(&t2, NULL, test, "T2");
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("main: end, counter = %d\n", counter);
    return 0;
}