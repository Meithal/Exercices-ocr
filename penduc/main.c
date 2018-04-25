#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <dirent.h>

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

char ** string_into_arrays(char * string) {

    int nb_of_words = 0;
    for (char * letter = string; * letter != '\0'; letter++)
        if (* letter == '\n')
            ++nb_of_words;

    char ** array_words = calloc((size_t) nb_of_words + 2,  sizeof(char *));

    for(
            char
                    * start             = string,
                    **word              = array_words - 1,
                    position_letter     = 0;
            * (string + 1) != '\0' ;
            string++
            )
    {
        if(string == start || *string == '\n') {
            word ++;
            * word = malloc(50);
            memset(* word, 0, 50);
            position_letter = 0;
        }

        if(* string == '\r' || * string == '\n')
            continue;
        else {
            (* word)[position_letter++] = * string;
        }
    }

    return array_words;
}

void release_string_into_arrays(char *** arr) {
    int i = 0;

    while((*arr)[i])
        free((*arr)[i++]);
    free(*arr);

    * arr = NULL;
}

void file_into_string(char * fname, char ** destination) {
    FILE * fwords = fopen(fname, "rb");

    if (fwords == NULL) {
        puts("System failure opening the word file\n");
        exit(EXIT_FAILURE);
    }

    fseek(fwords, 0L, SEEK_END);
    size_t file_size = (size_t) ftell(fwords);

    if (file_size < 0) {
        puts("Error finding the size of the file");
        exit(EXIT_FAILURE);
    }

    rewind(fwords);
    * destination = malloc(file_size);
    fread(* destination, sizeof(char), file_size, fwords);
    fclose(fwords);
}

void release_string(char * string) {
    free(string);
    *string = NULL;
}

int main() {
    char lettreEntree;
    int coupsRestants = 10;
    int gagne = 0;

    if (!in_directory(".", "mots.txt")) {
        puts("mots.txt missing !\n");
        return EXIT_FAILURE;
    }

    char * mots = NULL;
    file_into_string("mots.txt", &mots);
    char ** arr_mots = string_into_arrays(mots);
    release_string(mots);

    int nombre_de_mots = 0;
    while(arr_mots[nombre_de_mots] != '\0')
        ++nombre_de_mots;

    char * motMystere = arr_mots[rand() % nombre_de_mots];

    release_string_into_arrays(&arr_mots);

    char *caracteres_devines = malloc(sizeof(char)); *caracteres_devines = '\0';

    printf("Le jeu du pendu\n");

    do {

        printf("Entrer une lettre (il vous reste %d coup%s)\n> ",
               coupsRestants,
               coupsRestants > 1 ? "s" : "");
        scanf(" %c", &lettreEntree);

        gagne = 1;
        char lettre_trouvee = 0;
        printf("\n");
        for(char * c = motMystere; * c != '\0'; c++) {
            if(* c == lettreEntree) {
                if(!strchr(caracteres_devines, lettreEntree)) {
                    size_t curlen = strlen(caracteres_devines);
                    caracteres_devines = realloc(caracteres_devines, sizeof(char) * (curlen+1));
                    caracteres_devines[curlen] = lettreEntree;
                    caracteres_devines[curlen + 1] = '\0';
                    lettre_trouvee = 1;
                }
                putchar(* c);
            } else if (strchr(caracteres_devines, * c)) {
                putchar(* c);
            }
            else {
                gagne = 0;
                putchar('_');
            }
        }
        putchar('\n');
        if (!lettre_trouvee)
            --coupsRestants;
        lettre_trouvee = 0;
    } while(!gagne && coupsRestants);

    if(gagne)
        printf("Bravo, vous avez gagne.");
    else {
        printf("Vous n'avez plus de coups.");
    }
    free(caracteres_devines);
    return 0;
}