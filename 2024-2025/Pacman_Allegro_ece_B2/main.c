#include "pacman.h"
int main(){
    allegro_init();
    install_keyboard();//utilisation du clavier dans allegro
    install_mouse();//utilisation de la souris dans allegro
    set_color_depth(desktop_color_depth());

    FONT* ft = font;
/*    PALETTE palette;
    ft = load_font("../font/arialblack.pcx", palette, NULL);*/
    if (!ft) {
        printf("erreur font\n");
    }

    T_jeu jeu;//debut de partie
    jeu.score = 0;//init score
    jeu.vies = 3;//init vies

    T_map map;//variable map

    srand(time(NULL));//init aleatoire

    T_diamant diamants[NB_DIAMANTS];//variable diamants

    int numMap = 1;//gestion des maps
    char fichierMap[80];
    char*  fichierMap1 = "map/map";
    char  fichierMap2[2];
    char*  fichierMap3 = ".txt";

    //cahrgement des images
    BITMAP* murImg = load_bitmap("images/mur.bmp", NULL);

    BITMAP* diamantImg = load_bitmap("images/diams.bmp", NULL);

    BITMAP* p1 = load_bitmap("images/pacman1.bmp", NULL);

    BITMAP* p2 = load_bitmap("images/pacman2.bmp", NULL);

    BITMAP* f1 = load_bitmap("images/f1.bmp", NULL);

    BITMAP* f2 = load_bitmap("images/f2.bmp", NULL);

    BITMAP* f3 = load_bitmap("images/f3.bmp", NULL);

    BITMAP* f4 = load_bitmap("images/f4.bmp", NULL);

    BITMAP* imagesFantomes[NB_FANTOME];
    imagesFantomes[0] = f1;
    imagesFantomes[1] = f2;
    imagesFantomes[2] = f3;
    imagesFantomes[3] = f4;

    T_pacman pacman;//variable pacMan

    do {
        //chemin vers map
        strcpy(fichierMap, fichierMap1);
        sprintf(fichierMap2, "%d", numMap);
        strcat(fichierMap, fichierMap2);
        strcat(fichierMap, fichierMap3);

        if (lireMap (fichierMap, &map) == 1)//lecture map
        {
            printf("impossible de lire le fichier : %s", fichierMap);//message d erreur
            exit(EXIT_FAILURE);
        }

        //voirMapTexte(map);

        for (int i=0; i<NB_DIAMANTS; i++)//positionnement aleatoire des diamants sur la map
        {
            int ld, cd;
            int caseAvecDiamant = 0;
            do
            {
                ld = rand()%(map.nbLignes);
                cd = rand()%(map.nbColonnes);
                caseAvecDiamant = 0;
                for (int j=0; j<i; j++)
                {
                    if (diamants[j].c == cd && diamants[j].l == ld)
                        caseAvecDiamant = 1;
                }
                //interdiction sur mur ou zone inaccessible
            } while (*(map.textMap+ld*map.nbColonnes+cd) == 1 || *(map.textMap+ld*map.nbColonnes+cd) == 2 || caseAvecDiamant == 1);
            diamants[i].c = cd;
            diamants[i].l = ld;
            diamants[i].etat = 1;
        }

        int w = MUR_SIZE*map.nbColonnes;//init largeur ecran
        int h = MUR_SIZE*map.nbLignes;//init hauteur ecran

        if((set_gfx_mode(GFX_AUTODETECT_WINDOWED,w,h,0,0))!=0){//init fenetre allegro
            allegro_message("Pb de mode graphique") ;
            allegro_exit();
            exit(EXIT_FAILURE);
        }

        BITMAP* buffer_1 =  create_bitmap(w,h);//creation du double buffer

        initPacman(&pacman);//init pacMan

        T_fantome fantomes[NB_FANTOME];//init des fantomes
        for (int i = 0; i < NB_FANTOME; ++i) {
            initFantome(&fantomes[i], i);
        }

        int current_img = 1;//affichage de l image pacMan1

        while (!key[KEY_ESC] && jeu.vies > 0 && !testerTousDiamantsRamasses(diamants))//boucle sur une partie
        {
            afficherMap (buffer_1, map, w, h, MUR_SIZE, murImg);//affichage de la map dans le buffer

            if (key[KEY_UP] || key[KEY_DOWN] || key[KEY_LEFT] || key[KEY_RIGHT]) {//gestion des deplacements pacMan
                if (key[KEY_UP]) deplacerPacman(&pacman, map, KEY_UP);
                if (key[KEY_DOWN]) deplacerPacman(&pacman, map, KEY_DOWN);
                if (key[KEY_LEFT]) deplacerPacman(&pacman, map, KEY_LEFT);
                if (key[KEY_RIGHT]) deplacerPacman(&pacman, map, KEY_RIGHT);

                current_img = (current_img == 1) ? 2 : 1;//changement d image pacMan 1/2
            }

            BITMAP* imgPacman = (current_img == 1) ? p1 : p2;

            for (int i = 0; i < NB_FANTOME; ++i) {//deplacement des fantomes
                deplacerFantome(&fantomes[i], map, pacman);
            }

            for (int i = 0; i < NB_FANTOME; ++i) {//teste collision fantome
                int collision = testerCollisionFantome(pacman, fantomes[i]);
                if (collision == 1)//si collision
                {
                    jeu.vies--;//diminution du nombre de vie
                    initPacman(&pacman);//reinit position pacMan
                    for (int i = 0; i < NB_FANTOME; ++i) {//reinit position fantome
                        initFantome(&fantomes[i], i);
                    }
                }
            }

            for (int i = 0; i < NB_DIAMANTS; ++i) {//teste collision diamants
                int collision = testerCollisionDiamant(pacman, diamants[i]);
                if (collision == 1)
                {
                    jeu.score++;//augmentation du score
                    diamants[i].etat = 0;//diamant ramasse
                }
            }

            afficherFantomes(buffer_1, fantomes, imagesFantomes);//afficher fantome
            afficherPacman(buffer_1, pacman, imgPacman);//afficher pacMan
            afficherDiamants (buffer_1, diamants, MUR_SIZE, diamantImg);//afficher diamants

            printf("score %d vies %d\n", jeu.score, jeu.vies);//affichage score et vies dans la console

//            textprintf_ex(buffer_1, ft, 10, 10, makecol(0, 0, 255), -1, "score : %d", jeu.score);

            blit(buffer_1, screen,0,0,0,0,w,h);//changement de buffer


            rest(100);//pause entre chaque image
        }

        destroy_bitmap(buffer_1);//suppression du buffer

        numMap++;//passage a la map suivante

    } while (numMap <= NB_MAP && jeu.vies > 0 && !key[KEY_ESC]);//teste fin de jeu

    allegro_exit();//sortie allegro
    return 0;
}END_OF_MAIN();

