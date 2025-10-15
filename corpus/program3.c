#include <stdio.h>

int main() {
    char board[3][3];
    int choice, row, col, gameOver = 0, validMove;
    char player = 'X';
    char playAgain = 'y';
    int xWins = 0, oWins = 0, draws = 0;
    int round = 1;

    while (playAgain == 'y' || playAgain == 'Y') {
        char val = '1';
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                board[i][j] = val++;
            }
        }

        gameOver = 0;
        player = 'X';
        printf("\n===== TIC TAC TOE - ROUND %d =====\n", round);

        while (!gameOver) {
            printf("\n");
            for (int i = 0; i < 3; i++) {
                printf(" %c | %c | %c ", board[i][0], board[i][1], board[i][2]);
                if (i != 2) printf("\n---|---|---\n");
            }
            printf("\n");

            validMove = 0;
            while (!validMove) {
                printf("Player %c, enter position (1-9): ", player);
                scanf("%d", &choice);

                if (choice < 1 || choice > 9) {
                    printf("Invalid input! Choose between 1-9.\n");
                    continue;
                }

                row = (choice - 1) / 3;
                col = (choice - 1) % 3;

                if (board[row][col] == 'X' || board[row][col] == 'O') {
                    printf("That spot is already taken! Try again.\n");
                } else {
                    board[row][col] = player;
                    validMove = 1;
                }
            }

            int win = 0;
            for (int i = 0; i < 3; i++) {
                if (board[i][0] == player && board[i][1] == player && board[i][2] == player)
                    win = 1;
                if (board[0][i] == player && board[1][i] == player && board[2][i] == player)
                    win = 1;
            }
            if (board[0][0] == player && board[1][1] == player && board[2][2] == player)
                win = 1;
            if (board[0][2] == player && board[1][1] == player && board[2][0] == player)
                win = 1;

            int full = 1;
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++) {
                    if (board[i][j] >= '1' && board[i][j] <= '9') {
                        full = 0;
                    }
                }
            }

            if (win) {
                printf("\n");
                for (int i = 0; i < 3; i++) {
                    printf(" %c | %c | %c ", board[i][0], board[i][1], board[i][2]);
                    if (i != 2) printf("\n---|---|---\n");
                }
                printf("\nPlayer %c wins!\n", player);
                if (player == 'X') xWins++;
                else oWins++;
                gameOver = 1;
            } else if (full) {
                printf("\n");
                for (int i = 0; i < 3; i++) {
                    printf(" %c | %c | %c ", board[i][0], board[i][1], board[i][2]);
                    if (i != 2) printf("\n---|---|---\n");
                }
                printf("\nIt's a draw!\n");
                draws++;
                gameOver = 1;
            } else {
                player = (player == 'X') ? 'O' : 'X';
            }
        }

        printf("\n===== SCOREBOARD =====\n");
        printf("Player X wins: %d\n", xWins);
        printf("Player O wins: %d\n", oWins);
        printf("Draws: %d\n", draws);

        printf("\nDo you want to play again? (y/n): ");
        scanf(" %c", &playAgain);
        round++;
    }

    printf("\n===== FINAL RESULTS =====\n");
    printf("Total Rounds Played: %d\n", round - 1);
    printf("Player X Wins: %d\n", xWins);
    printf("Player O Wins: %d\n", oWins);
    printf("Draws: %d\n", draws);

    if (xWins > oWins)
        printf("Overall Winner: Player X \n");
    else if (oWins > xWins)
        printf("Overall Winner: Player O \n");
    else
        printf("Overall Result: It's a Tie!\n");

    printf("\nThank you for playing!\n");
    return 0;
}
