#include <stdio.h>

int main() {
    int choice, n, i, j;
    int arr[100];
    char repeat = 'y';

    while (repeat == 'y' || repeat == 'Y') {
        printf("\n==== NUMBER ANALYZER MENU ====\n");
        printf("1. Check Prime\n");
        printf("2. Calculate Factorial\n");
        printf("3. Generate Fibonacci Series\n");
        printf("4. Analyze Array (Sum, Avg, Min, Max)\n");
        printf("5. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        if (choice == 5) {
            printf("Exiting program...\n");
            break;
        }

        if (choice == 1) {
            printf("Enter a number: ");
            scanf("%d", &n);
            int isPrime = 1;
            if (n < 2) isPrime = 0;
            else {
                for (i = 2; i * i <= n; i++) {
                    if (n % i == 0) {
                        isPrime = 0;
                        break;
                    }
                }
            }
            if (isPrime)
                printf("%d is a Prime number.\n", n);
            else
                printf("%d is NOT a Prime number.\n", n);
        }

        else if (choice == 2) {
            printf("Enter a number: ");
            scanf("%d", &n);
            int fact = 1;
            for (i = 1; i <= n; i++) {
                fact *= i;
            }
            printf("Factorial of %d = %d\n", n, fact);
        }

        else if (choice == 3) {
            printf("Enter number of terms: ");
            scanf("%d", &n);
            int a = 0, b = 1, c;
            printf("Fibonacci Series: ");
            for (i = 0; i < n; i++) {
                printf("%d ", a);
                c = a + b;
                a = b;
                b = c;
            }
            printf("\n");
        }

        else if (choice == 4) {
            printf("Enter number of elements: ");
            scanf("%d", &n);
            for (i = 0; i < n; i++) {
                printf("arr[%d] = ", i);
                scanf("%d", &arr[i]);
            }
            int sum = 0, min = arr[0], max = arr[0];
            for (i = 0; i < n; i++) {
                sum += arr[i];
                if (arr[i] < min) min = arr[i];
                if (arr[i] > max) max = arr[i];
            }
            printf("Sum = %d\n", sum);
            printf("Average = %.2f\n", (float)sum / n);
            printf("Minimum = %d\nMaximum = %d\n", min, max);
        }

        else {
            printf("Invalid choice! Try again.\n");
        }

        printf("\nDo you want to perform another operation? (y/n): ");
        scanf(" %c", &repeat);
    }

    printf("\nThank you for using Number Analyzer!\n");
    return 0;
}
