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

/**
 * Return an array of filenames in the provided path
 * @param path
 * @return An array of filenames. The last element is a NULL character
 */
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

/**
 * Split a string by newlines and return an array
 * @param string
 * @return
 */
char ** list_words(char * string) {
    char ** returned_array = NULL;

    for(char * c = string; *c != '\0'; c++) {
        
    }
    returned_array = calloc((size_t) telldir(dp) + 1, sizeof(char*));
    rewinddir(dp);
    size_t i = 0;
    while ((ep = readdir(dp))) {
        returned_array[i] = malloc(strlen(ep->d_name) + 1);
        strcpy(returned_array[i], ep->d_name);
        i += 1;
    }
    return returned_array;
}

int main() {
    printf("Hello, World!\n");

    if (!in_directory(".", "mots.txt")) {
        puts("Fichier mots.txt manquant !");
        return EXIT_FAILURE;
    }
    else {
        FILE * fmots = fopen("mots.txt", "r");
    }
    char ** a = listdir(".");
    for (char ** cursor = a; cursor != '\0'; cursor++) {
        puts(*cursor);
    }
    free_array_of_char(a);
}