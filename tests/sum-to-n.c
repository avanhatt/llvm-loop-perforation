#include <stdio.h>

int sum_to_n(int n) {
    int sum = 0;
    for (int i = 0; i < n; i ++) {
       sum += i;
    }
    return sum;
}

int main(int argc, char const *argv[]) {
    int sum = sum_to_n(5);
    printf("%d\n", sum);
    return 0;
}