#ifndef HEADER_H_INCLUDED
#define HEADER_H_INCLUDED

#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <ctime>
#include <fstream>
#include <cmath>
#include <map>
#include <algorithm>

using namespace std;

// Structure pour les stations
typedef struct struct_stations {
    string id_station;
    string station_name;
    int x;
    int y;
} str_stations;

// Forward declaration des classes pour éviter les dépendances circulaires
class Train;
class Billet;

// Classe Train
class Train {
public:
    const string id_train;
    const string horaire_depart;
    const string horaire_arrivee;
    const int capacite;
    struct_stations ville_depart;
    struct_stations ville_arrivee;
    int places_libres;

    // Constructeur
    Train(const string& input_id_train, const struct_stations input_ville_depart,
          const struct_stations input_ville_arrivee, const string& input_horaire_depart,
          const string& input_horaire_arrivee, int input_capacite, int input_places_libres);

    // Méthodes
    void verifierDisponibilite() const;
    void reserverPlace();
    void annulerReservation();
    void afficherInfosTrain() const;
    ~Train();
};

// Classe Billet
class Billet {
public:
    string id_billet;
    string type_classe;
    Train* BLT_train;
    string date_voyage;
    float prix;

    // Constructeur
    Billet(const string& input_id_billet, const string& input_type_classe, Train* input_BLT_train,
           const string& input_date_voyage);

    // Méthodes
    void afficherDetailsBillets() const;
    float calculerPrix() const;
    ~Billet();
};

// Classe Passager
class Passager {
public:
    const string nom;
    const string prenom;
    const string id_passager;
    vector<Billet> PSG_reservation;
    vector<Billet> historiqueReservations; // Nouveau : Historique des billets

    // Constructeur
    Passager(const string& input_nom, const string& input_prenom, const string& input_id_passager);

    // Méthodes
    void ajouterReservation(const Billet* billet);
    void annulerReservation(const Billet* billet);
    void afficherReservations() const;
    void afficherHistorique() const; // Nouveau : Affichage de l'historique
    ~Passager();
};

// Classe Reservation
class Reservation {
public:
    const string id_reservation;
    Passager* RSV_passager;
    Billet* RSV_billet;

    // Constructeur
    Reservation(const string& input_id_reservation, Passager* input_RSV_passager, Billet* input_RSV_billet);

    // Méthodes
    void confirmerReservation() const;
    void annulerReservation() const;
    void afficherDetailsReservation() const;
    ~Reservation();
};

// Classe Calendrier pour la gestion des horaires des trains
class Calendrier {
public:
    map<string, vector<Train*>> horaires;

    // Méthodes
    void ajouterHoraire(const string& date, Train* train);
    void afficherCalendrier(const string& date) const;
};

// Fonctions utilitaires
string generate_id(const string& prefix, vector<string>& storage_billetID);
void generate_trainmap(const vector<vector<int>>& stations_locs, const int map_width, const int map_height);

void initialize_stations(vector<str_stations>& stations, const vector<vector<int>>& stations_locs);

void save_data_files(vector<Train*> train_data, vector<Billet*> billet_data, vector<Passager*> passager_data);

void extract_data_file(vector<Train*>& train_data, vector<Billet*>& billet_data,
                       vector<Passager*>& passager_data, vector<str_stations>& stations);

#endif // HEADER_H_INCLUDED
