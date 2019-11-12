#include <stdio.h>
#include <stdlib.h>

int do_thing(int n) {
    int *ptr_array[n];
    // allocate my space
    for (int i = 0; i < n; i ++) {
       ptr_array[i] = (int *)malloc(10*sizeof(int));
    }

    int sum = 0;
    // fill the slots with some complicated computations
    for (int i = 0; i < n; i ++) {
        for (int j = 0; j < 7 * n; j += (i+1)) {
            //printf("%p,\t %d\n", ptr_array[i] + (j % 10)*sizeof(int), j);
            *(ptr_array[i] + (j % 10)*sizeof(int)) = j;
        }
        for (int j = 0; j < 10; j++) {
            sum += *(ptr_array[i] + (j%10)*sizeof(int));
        }
        //printf("%d\n", sum);
    }

    // free all the things.
    for (int i = 0; i < n; i ++) {
        free(ptr_array[i]);
    }
    return sum;
}

int main(int argc, char const *argv[]) {
    int sum = do_thing(5);
    printf("%d\n", sum);
    return 0;
}
