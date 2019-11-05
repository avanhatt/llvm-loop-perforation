#include <stdio.h>

double res[3][3]; // To store result
double a[3][3] = {{1, 1, 1}, {2, 2, 2}, {3, 3, 3}};
double b[3][3] = {{1, 2, 3}, {1, 2, 3}, {1, 2, 3}};

void _p_multiply() {
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            res[i][j] = 0;
            for (int k = 0; k < 3; k++) {
                res[i][j] += a[i][k]*b[k][j];
            }
        }
    }
}

int main(int argc, char const *argv[]) {
    _p_multiply();

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            printf("%f ", res[i][j]);
        }
        printf("\n");
    }

    int n = 10;

    while (n > 0) {
        n -= 2;
        printf("%d ", n);
    }

    return 0;
}