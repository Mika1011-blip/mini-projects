//
// Created by erwoo on 24/11/2024.
//


#ifndef PROJET_ALLEGRO_PARC_ATTRACTION_PACMAN_H
#define PROJET_ALLEGRO_PARC_ATTRACTION_PACMAN_H

#include <allegro.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <math.h>

#define MUR_SIZE 20 //taille d un mur
#define NB_MAP 3 //nombre de maps
#define NB_DIAMANTS 10 // nombre de diamants
#define NB_FANTOME 4 //nombre de fantome

typedef struct//structure de la map
{
    int* textMap;//map -pointer serve to dynamically change structure of the map in run-time , if static, the size of the map would be determined at the compile time.
    int nbLignes;//nombre de ligne de la map
    int nbColonnes;//nombre de colonne de la map
} T_map;

typedef struct//structure du jeu
{
    int score; // score
    int vies; // nb vies
} T_jeu;

typedef struct//structure de la position de pacman
{
    int x; // position colonnne
    int y; // position ligne
} T_pacman;

typedef struct//structure de la position des fantome
{
    int x; // position colonnne
    int y; // position ligne
    int c; //couleur de 0 à 4
} T_fantome;


typedef struct//structure des diamants
{
    int l;//position ligne
    int c;//position colonne
    int etat;//diams ramasse 0 ou non 1
} T_diamant;

int lireMap (char* fichierMap, T_map* map);//lecture de la map
void voirMapTexte (T_map map);//affichage des donnes de la map
void initPacman(T_pacman *pacman);//spawn du pacMan
void initFantome(T_fantome *fantome, int i);//spawn des fantomes
void afficherMap (BITMAP* p, T_map map, int w, int h, int l, BITMAP* mur);//afficher la map
void afficherDiamants (BITMAP* p, T_diamant* diamants, int l, BITMAP* diamant);//afficher les diamants
void afficherPacman(BITMAP* buffer, T_pacman pacman, BITMAP* img);//afficher pacMan
void deplacerPacman(T_pacman* pacman, T_map map, int key_code);//mouvement de pacMan
void afficherFantomes(BITMAP* buffer, T_fantome *fantomes, BITMAP** img);//affichage des fantomes
void deplacerFantome(T_fantome* fantome, T_map map, T_pacman pacman);//mouvement des fantomes
int testerCollisionDiamant(T_pacman pacman, T_diamant diamant);//ramassage des diamants
int testerCollisionFantome(T_pacman pacman, T_fantome fantome);//pacMan touche fantome
int testerTousDiamantsRamasses(T_diamant* diamants);//verification des diamants


#endif //PROJET_ALLEGRO_PARC_ATTRACTION_PACMAN_H
