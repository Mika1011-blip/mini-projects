#ifndef HEADER_H_INCLUDED
#define HEADER_H_INCLUDED

#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <cmath>
#include <ctime>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <random>


using namespace std;

// Prefixes
extern const string train_prefix;
extern const string passager_prefix;
extern const string billet_prefix;
extern const string reservation_prefix;

// Type class
extern const vector<string> array_type_classe;

// Map settings
extern const int map_height;
extern const int map_width;

// Stations locations settings
extern const vector<vector<int>> stations_locs;


//Remember to store these in external files.
extern vector<string> storage_trainID;
extern vector<string> storage_passagerID;
extern vector<string> storage_billetID;
extern vector<string> storage_reservationID;



typedef struct struct_stations
{
    string id_station;
    string station_name;
    int x;
    int y;
} str_stations;
extern vector<str_stations> stations;


// Forward declaration of classes to resolve circular dependencies
class Train;
class Billet;

// Class Train
class Train
{
private :
    const string id_train;
    const string horaire_depart;
    const string horaire_arrivee;
    const int capacite;
    int places_libres;
public:
    const struct_stations ville_depart; //public
    const struct_stations ville_arrivee; //public
    // Constructor
    Train(
        const string& input_id_train,
        const struct_stations input_ville_depart,
        const struct_stations input_ville_arrivee,
        const string& input_horaire_depart,
        const string& input_horaire_arrivee,
        int input_capacite,
        int input_places_libres
    );

    // Methods
    void verifierDisponibilite() const;
    void afficherInfosTrain() const;

    //gets
    string get_idTrain()const;
    string get_horaireDepart()const;
    string get_horaireArrivee()const;
    int get_capacite()const;
    int get_places_libres()const;

    //modify
    void incr_places_libres();
    void decr_places_libres();

    ~Train();
};

// Class Billet
class Billet
{
private:
    string id_billet;
    string type_classe;
    string date_voyage;
    float prix;
public:
    Train* BLT_train; // public
    // Constructor
    Billet(
        const string& input_id_billet,
        const string& input_type_classe,
        Train* input_BLT_train,
        const string& input_date_voyage
    );

    // Methods
    void afficherDetailsBillets() const;
    void calculerPrix();

    //Gets
    string get_id_billet()const;
    string get_type_classe()const;
    string get_date_voyage() const;
    float get_prix()const;

    ~Billet();
};

// Class Passager
class Passager
{
protected:
    const string nom;
    const string prenom;
    const string id_passager;
    vector<Billet*> PSG_reservation;               // Store pointers
    //vector<Billet*> PSG_historique_reservation;    // Store pointers
public:
    // Constructor
    Passager(
        const string& input_nom,
        const string& input_prenom,
        const string& input_id_passager
    );

    // Accessor methods
    string get_nom() const;
    string get_prenom() const;
    string get_id_passager() const;
    vector<Billet*>& get_PSG_reservation();
    //vector<Billet*> get_PSG_historique_reservation() const;

    // Methods
    void ajouterReservation(const Billet* billet);
    void annulerReservation(const Billet* billet);
    //void ajouterHistoriqueReservation(const Billet* billet);

    Billet* afficherReservations() const;
    //void afficherHistoriqueReservation() const;

    void afficherInfo();
    virtual ~Passager();
};

class Archives : public Passager {
public:
    map<Billet*, string> archived_billets;

    Archives(const string& input_nom,
             const string& input_prenom,
             const string& input_id_passager);

    void ajouter_historiqueReservations(Billet* cancel_billet, string motiv);

    void afficherArchives() const;

    ~Archives() {}
};

//clasee calendrier
class Calendrier {
public:
    map<string, vector<Train*>> train_schedule;
    void import_train_schedule(const map<string, vector<Train*>>& input_schedule);
    //void initialize_train_schedule();
    void afficher_calendrier() const;

    string demander_date() const;
    Train* search_trains(const string& date) const;

    ~Calendrier();
};


// Class Reservation
class Reservation
{
public:
    const string id_reservation;
    Passager* RSV_passager; // Use pointer for circular dependency
    Billet* RSV_billet;     // Use pointer for circular dependency

    // Constructor
    Reservation(
        const string& input_id_reservation,
        Passager* input_RSV_passager,
        Billet* input_RSV_billet
    );

    // Methods
    void confirmerReservation(vector<Passager*>& passager_data,
                                        vector<Billet*>& billet_data,
                                        Calendrier* calendrier_data) const;
    void annulerReservation(vector<Passager*>& passager_data,
                                        vector<Billet*>& billet_data,
                                        Calendrier* calendrier_data,
                                        bool was_confirmed) const;
    void afficherDetailsReservation() const;
    ~Reservation();
};



//functions
string generate_id(const string& prefix, vector<string>& storage_billetID);
void generate_trainmap(const vector<vector<int>> & stations_locs, const int map_width, const int map_height);
void initialize_stations(
    str_stations& stationA,
    str_stations& stationB,
    str_stations& stationC,
    str_stations& stationD,
    str_stations& stationE,
    const vector<vector<int>>& stations
);


void save_data_files(/*vector<Train*> train_data,*/
                     vector<Archives*> archives_data,
                     vector<Billet*> billet_data,
                     vector<Passager*> passager_data,
                     Calendrier* calendrier_data);


void initialize_stations(
    vector<str_stations>& stations,
    const vector<vector<int>>& stations_locs
);

void extract_data_file(
    /*vector<Train*>& train_data,*/
    vector<str_stations>& stations,
    vector<Billet*>& billet_data,
    vector<Passager*>& passager_data,
    vector<Archives*>& archives_data,
    Calendrier* calendrier_data // Added pointer to Calendrier
) ;

void system_loop(
    /*vector<Train*>& train_data,*/
    vector<Archives*>& archives_data,
    vector<Billet*>& billet_data,
    vector<Passager*>& passager_data,
    vector<Reservation*>& reservation_data,
    Calendrier* calendrier_data
);

void initialize_train_vector(Calendrier* calendrier);

string get_current_date();
bool is_date_old(string& base_date, string& given_date);
string get_station_name();
#endif // HEADER_H_INCLUDED
