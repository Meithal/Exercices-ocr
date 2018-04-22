#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <dirent.h>
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
    int i;

    i = 0;
    while(array[i]) {
        free(array[i++]);
    }
    free(array);
}

char ** string_into_arrays(char * string) {

    int nb_of_words = 0;
    for (char *letter = string; *letter != '\0'; letter++)
        if (*letter == '\n')
            ++nb_of_words;

    char ** array_words = calloc((size_t) nb_of_words + 2,  sizeof(char *));

    for(
        char
                * start             = string,
                **word              = array_words - 1,
                position_letter     = 0;
        *string != '\0' ;
        string++
        )
    {
        if(string == start || *string == '\n') {
            word ++;
            *word = malloc(50);
            memset(*word, 0, 50);
            position_letter = 0;
        }

        if(*string == '\r' || *string == '\n')
            continue;
        else {
            (*word)[position_letter++] = *string;
        }
    }

    return array_words;
}

int main() {
    printf("Hello, World!\n");

    if (!in_directory(".", "words.txt")) {
        puts("Words.tct missing !\n");
        return EXIT_FAILURE;
    }

    FILE * fwords = fopen("words.txt", "rb");

    if (fwords == NULL) {
        puts("System failure opening the word file\n");
        return EXIT_FAILURE;
    }

    fseek(fwords, 0L, SEEK_END);
    size_t file_size = (size_t) ftell(fwords);
    rewind(fwords);
    char* words = malloc(file_size);
    fread(words, sizeof(char), file_size, fwords);
    fclose(fwords);
    fwords = NULL;

    char ** arr_words = string_into_arrays(words);

    srand((unsigned int) time(0));
    int number_of_words = 0;
    while (arr_words[number_of_words] != NULL )
        puts(arr_words[number_of_words++]);
    int choosen_number = rand() % number_of_words;

    printf("Chosen number: %d\n", choosen_number);

//    char ** a = listdir(".");
//    for (char ** cursor = a; cursor != '\0'; cursor++) {
//        puts(*cursor);
//    }
//    free_array_of_char(a);
}
