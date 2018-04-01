#include <stdio.h>
#include <stdlib.h>
#include <memory.h>

int main() {
    char lettreEntree;
    char *motMystere = "rouge";
    int coupsRestants = 10;
    int gagne = 0;
    char *caracteres_devines = malloc(sizeof(char));
    *caracteres_devines = '\0';

    printf("Bienvenue dans le jeu du pendu!\n");

    do {

        printf("Entrer une lettre (il vous reste %d coup%s)\n> ",
               coupsRestants,
               coupsRestants > 1 ? "s" : "");
        scanf(" %c", &lettreEntree);

        gagne = 1;
        printf("\n");
        for(char *c = motMystere; *c != '\0'; c++) {
            if(*c == lettreEntree) {
                if(!strchr(caracteres_devines, lettreEntree)) {
                    size_t curlen = strlen(caracteres_devines);
                    caracteres_devines = realloc(caracteres_devines, sizeof(char) * (curlen+1));
                    caracteres_devines[curlen] = lettreEntree;
                    caracteres_devines[curlen + 1] = '\0';
                }
                putchar(*c);
            } else if (strchr(caracteres_devines, *c)) {
                putchar(*c);
            }
            else {
                gagne = 0;
                putchar('_');
            }
        }
        putchar('\n');
        coupsRestants--;
    } while(!gagne && coupsRestants);

    if(gagne)
        printf("Bravo, vous avez gagne.");
    else {
        printf("Vous n'avez plus de coups.");
    }
    free(caracteres_devines);
    return 0;
}