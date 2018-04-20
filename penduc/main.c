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

#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>


char in_directory(char * dir_name, char * needle) {
    DIR * dir = opendir(dir_name);
    struct dirent * de;

    char found = 0;
    while ((de = readdir(dir))) {
        if(strcmp(de->d_name, needle) == 0) {
            found = 1;
        }
    }
    closedir(dir);

    return found;
}

struct dir_handler {
    DIR dir_object;
    struct dirent dir_entity_object;
    short (*in_directory)(struct dir_handler, char * , char *);
    char ** (*directories)(struct dir_handler);
    char ** (*files)(struct dir_handler);
};

struct dir_handler open_dir(char * path) {

}

char ** listdir(char * path) {
    DIR *dp = opendir(path);
    struct dirent *ep;
    char ** returned_array = NULL;
    if (dp != NULL) {
        while (readdir(dp));
        returned_array = calloc((size_t) telldir(dp) + 1, sizeof(char*));
        rewinddir(dp);
        size_t i = 0;
        while ((ep = readdir(dp))) {
            returned_array[i] = malloc(strlen(ep->d_name) + 1);
            strcpy(returned_array[i], ep->d_name);
            i += 1;
        }
    }
    return returned_array;
}

short free_array_of_char(char **array) {
    char ** cursor = array;
}

char ** string_into_arrays(char * chaine) {

    int nombre_de_mots = 0;
    for (char *lettre = chaine; *lettre != '\0'; lettre++)
        if (*lettre == '\n')
            nombre_de_mots += 1;

    char ** array_mots = malloc((size_t) nombre_de_mots * sizeof(char *) + 1);
    memset(array_mots, 0, (size_t) nombre_de_mots * sizeof(char *) + 1);
    for(
        char * debut = chaine, ** mot = (array_mots - 1), position_lettre = 0;
        *chaine != '\0' ;
        chaine++
        )
    {
        if(chaine == debut || *chaine == '\n') {
            mot ++;
            mot = malloc(50);
            memset(mot, 0, 50);
            position_lettre = 0;
        }

        if(*chaine == '\r' || *chaine == '\n')
            continue;
        else {
            mot[position_lettre++] = *chaine;
        }
    }

    return array_mots;
}

int main() {
    printf("Hello, World!\n");

    if (!in_directory(".", "mots.txt")) {
        puts("Fichier mots.txt manquant !\n");
        return EXIT_FAILURE;
    }
    else {
        FILE * fmots = fopen("mots.txt", "r");
        if (fmots == NULL) {
            puts("Probleme systeme lors de l'ouverture du fichier mots\n");
            return EXIT_FAILURE;
        }
        fseek(fmots, 0L, SEEK_END);
        size_t taille_fichier = (size_t) ftell(fmots);
        rewind(fmots);
        char* mots = malloc(taille_fichier);
        fread(mots, sizeof(char), taille_fichier, fmots);
        fclose(fmots);
        fmots = NULL;

//        printf(mots);

        char ** arr_mots = string_into_arrays(mots);

        srand((unsigned int) time(0));
        int nombre_de_mots = 0;
        for (; arr_mots[nombre_de_mots++] != NULL ; )
            printf(arr_mots[nombre_de_mots]);
        int nombre_choisi = rand() % nombre_de_mots;

        printf("Nombre choisi: %d\n", nombre_choisi);
    }

//    char ** a = listdir(".");
//    for (char ** cursor = a; cursor != '\0'; cursor++) {
//        puts(*cursor);
//    }
//    free_array_of_char(a);
}
