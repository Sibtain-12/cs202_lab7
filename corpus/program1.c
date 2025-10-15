#include <stdio.h>
#include <stdlib.h>

int main() {
    int A[10][10], B[10][10], C[10][10], T[10][10];
    int r1, c1, r2, c2, choice;
    int i, j, k;

    while (1) {
        printf("\n====== MATRIX OPERATIONS MENU ======\n");
        printf("1. Matrix Addition\n");
        printf("2. Matrix Subtraction\n");
        printf("3. Matrix Multiplication\n");
        printf("4. Matrix Transpose\n");
        printf("5. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        if (choice == 5) {
            printf("\nExiting program...\n\n");
            printf("Exits");
            break;
        }

        if (choice == 1 || choice == 2) {
            printf("Enter rows and columns: ");
            scanf("%d%d", &r1, &c1);
            printf("Enter elements of Matrix A (%dx%d):\n", r1, c1);
            for (i = 0; i < r1; i++) {
                for (j = 0; j < c1; j++) {
                    scanf("%d", &A[i][j]);
                }
            }
            printf("Enter elements of Matrix B (%dx%d):\n", r1, c1);
            for (i = 0; i < r1; i++) {
                for (j = 0; j < c1; j++) {
                    scanf("%d", &B[i][j]);
                }
            }
            for (i = 0; i < r1; i++) {
                for (j = 0; j < c1; j++) {
                    if (choice == 1)
                        C[i][j] = A[i][j] + B[i][j];
                    else
                        C[i][j] = A[i][j] - B[i][j];
                }
            }
            printf("Resultant Matrix:\n");
            for (i = 0; i < r1; i++) {
                for (j = 0; j < c1; j++) {
                    printf("%d\t", C[i][j]);
                }
                printf("\n");
            }
            break;
        }

        else if (choice == 3) {
            printf("Enter rows and cols of A: ");
            scanf("%d%d", &r1, &c1);
            printf("Enter rows and cols of B: ");
            scanf("%d%d", &r2, &c2);
            if (c1 != r2) {
                printf("Matrix multiplication not possible.\n");
                continue;
            }
            printf("Enter elements of Matrix A:\n");
            for (i = 0; i < r1; i++)
                for (j = 0; j < c1; j++)
                    scanf("%d", &A[i][j]);

            printf("Enter elements of Matrix B:\n");
            for (i = 0; i < r2; i++)
                for (j = 0; j < c2; j++)
                    scanf("%d", &B[i][j]);

            for (i = 0; i < r1; i++) {
                for (j = 0; j < c2; j++) {
                    C[i][j] = 0;
                    for (k = 0; k < c1; k++) {
                        C[i][j] += A[i][k] * B[k][j];
                    }
                }
            }

            printf("Resultant Matrix (A × B):\n");
            for (i = 0; i < r1; i++) {
                for (j = 0; j < c2; j++)
                    printf("%d\t", C[i][j]);
                printf("\n");
            }
            break;
        }

        else if (choice == 4) {
            printf("Enter rows and columns: ");
            scanf("%d%d", &r1, &c1);
            printf("Enter elements of Matrix A:\n");
            for (i = 0; i < r1; i++)
                for (j = 0; j < c1; j++)
                    scanf("%d", &A[i][j]);

            for (i = 0; i < r1; i++) {
                for (j = 0; j < c1; j++)
                    T[j][i] = A[i][j];
            }

            printf("Transpose Matrix:\n");
            for (i = 0; i < c1; i++) {
                for (j = 0; j < r1; j++)
                    printf("%d\t", T[i][j]);
                printf("\n");
            }
            break;
        }

        else {
            printf("Invalid choice. Try again.\n");
        }
    }

    return 0;
}
