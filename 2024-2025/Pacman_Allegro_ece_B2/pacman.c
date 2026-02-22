//
// Created by erwoo on 24/11/2024.
//

#include"pacman.h"

int lireMap (char* fichierMap, T_map* map)
{
    FILE *fichier = NULL;
    fichier = fopen(fichierMap, "r");//ouverture en lecture seule du fichier texte de la map

    if (fichier == NULL)
        return 1;

    char ligne[100];

    map->nbLignes = 0;
    map->nbColonnes = 0;
    map->textMap = NULL;

    int erreurLecture = 0;

    while(fgets(ligne, sizeof(ligne), fichier) != NULL && erreurLecture == 0) {//lecture de la map
        int i = 0;
        while (*(ligne+i) != '\n')// pointer arithmetic (array decays into pointer), (ligne + i) returns memory adress of ligne + i position in ligne array, * serve to access it's value
        {
            i++;
        }
        if (map->nbLignes == 0)
        {
            map->nbColonnes = i;
        }
        else
        {
            if (map->nbColonnes != i) {
                erreurLecture = 1;// in case unequal distribution size of column.
            }
        }
        if (map->textMap == NULL)
        {
            map->nbLignes = 1;//give it's first row if map was not created
            map->textMap = malloc((map->nbColonnes)*(map->nbLignes)*sizeof(int));// sizing map
        }
        else
        {
            (map->nbLignes)++; // when map is created
            map->textMap = realloc(map->textMap/*pointer to be resized*/, (map->nbColonnes)*(map->nbLignes)*sizeof(int));//resizing map
        }
        for (int j=0; j<(map->nbColonnes); j++)
        {
            int value = *(ligne+j) - '0';// '0' represent Ascii value , which in the arithmetic operation *(ligne+j) - '0' will return an integer value
            *(map->textMap+(map->nbLignes-1)*(map->nbColonnes)+j) = value; //assigning the value to the address location in textmap.
        }
    }

    fclose(fichier);

    return 0;

}

void initPacman(T_pacman *pacman) {
    pacman->x = 14;
    pacman->y = 23;
}

void initFantome(T_fantome *fantome, int i) {
    fantome->x = 13+i;
    fantome->y = 15;
    fantome->c = i+1;
}

void voirMapTexte (T_map map)//afficher map dans le console (ne valeur int)
{
    printf("nb lignes : %d\n", map.nbLignes);
    printf("nb colonnes : %d\n", map.nbColonnes);
    for (int i=0; i <map.nbLignes; i++)
    {
        for (int j=0; j<map.nbColonnes; j++)
        {
            printf("%d",*(map.textMap+i*map.nbColonnes+j));
        }
        printf("\n");
    }
}

void afficherMap (BITMAP* p, T_map map, int w, int h, int l, BITMAP* mur){
    rectfill(p, 0, 0, w, h, makecol(0,0,0)); // couleur de fond
    for (int i=0; i<map.nbLignes; i++)
    {
        for (int j=0; j<map.nbColonnes; j++)
        {
            if (*(map.textMap+i*map.nbColonnes+j) == 1) {
                stretch_sprite(p, mur, j*l, i*l, MUR_SIZE, MUR_SIZE);//affichage d un mur si 1 sinon couleur de fond
            }
        }
    }
}

void afficherDiamants (BITMAP* p, T_diamant* diamants, int l, BITMAP* diamant){
    for (int i=0; i<NB_DIAMANTS; i++)
    {
        if (diamants[i].etat == 1)
            stretch_sprite(p, diamant, diamants[i].c*l, diamants[i].l*l, MUR_SIZE, MUR_SIZE);//affichage diamants si etat = 1
    }
}

void afficherPacman(BITMAP* buffer, T_pacman pacman, BITMAP* img) {
    int x = pacman.x * MUR_SIZE;
    int y = pacman.y * MUR_SIZE;
    stretch_sprite(buffer, img, x, y, MUR_SIZE, MUR_SIZE);
}

void deplacerPacman(T_pacman* pacman, T_map map, int key_code) {
    int x = pacman->x;
    int y = pacman->y;

    if (key_code == KEY_UP) y--;//touche du claviers pour faire bouger pacMan
    else if (key_code == KEY_DOWN) y++;
    else if (key_code == KEY_LEFT) x--;
    else if (key_code == KEY_RIGHT) x++;

    if (x < 0) x = map.nbColonnes - 1;//passage d un coté à l autre si teleportation
    else if (x > (map.nbColonnes - 1)) x = 0;
    else if (y < 0) y = map.nbLignes - 1;
    else if (y > (map.nbLignes - 1)) y = 0;

    if (x >= 0 && x < map.nbColonnes && y >= 0 && y < map.nbLignes) {
        if (*(map.textMap + y * map.nbColonnes + x) != 1) {//mouvement pacMan si pas de mur
            pacman->x = x;
            pacman->y = y;
        }
    }
}

void afficherFantomes(BITMAP* buffer, T_fantome *fantomes, BITMAP** img) {
    for (int i = 0; i < NB_FANTOME; ++i) {
        int x = fantomes[i].x * MUR_SIZE;
        int y = fantomes[i].y * MUR_SIZE;
        stretch_sprite(buffer, *(img+i), x, y, MUR_SIZE, MUR_SIZE);
    }
}

void deplacerFantome(T_fantome* fantome, T_map map, T_pacman pacman) {
    int x = fantome->x;
    int y = fantome->y;

//    int deltaX = pacman.x - fantome->x;
//    int deltaY = pacman.y - fantome->y;

    int hV = rand()%2; // 0 deplacement horizontal, 1 vertical
    int pM = rand()%2; // 0 deplacement -1, 1

    if (hV == 0 && pM == 0) x--;//deplacement des fantome aleatoirement
    else if (hV == 0 && pM == 1) x++;
    else if (hV == 1 && pM == 0) y--;
    else if (hV == 1 && pM == 1) y++;

    if (x >= 0 && x < map.nbColonnes && y >= 0 && y < map.nbLignes) {
        if (*(map.textMap + y * map.nbColonnes + x) != 1) {//verification pas de murs
            fantome->x = x;
            fantome->y = y;
        }
    }
}

int testerCollisionDiamant(T_pacman pacman, T_diamant diamant) {
    if (diamant.etat == 1 && pacman.x == diamant.c && pacman.y == diamant.l)//teste collision avec un diamant
        return 1;
    return 0;
}

int testerCollisionFantome(T_pacman pacman, T_fantome fantome) {
    if (pacman.x == fantome.x && pacman.y == fantome.y)//teste collision avec un fantome
        return 1;
    return 0;
}

int testerTousDiamantsRamasses(T_diamant* diamants) {
    for (int i = 0; i < NB_DIAMANTS; i++) {
        if (diamants[i].etat == 1) {
            return 0; // Il reste des diamants
        }
    }
    return 1; // Tous les diamants ont été collectés
}
