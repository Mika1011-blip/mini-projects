#include "header.h"

// Définition de la fonction initialize_stations
void initialize_stations(vector<str_stations>& stations, const vector<vector<int>>& stations_locs) {
    if (stations_locs.size() != 5) {
        cerr << "Erreur : Il faut exactement 5 emplacements pour les stations.\n";
        return;
    }

    stations.resize(5);
    stations[0] = {"STR01", "Aberion", stations_locs[0][0], stations_locs[0][1]};
    stations[1] = {"STR02", "Brayden", stations_locs[1][0], stations_locs[1][1]};
    stations[2] = {"STR03", "Cameron", stations_locs[2][0], stations_locs[2][1]};
    stations[3] = {"STR04", "Delmont", stations_locs[3][0], stations_locs[3][1]};
    stations[4] = {"STR05", "Eldon", stations_locs[4][0], stations_locs[4][1]};
}
// Constructors and destructors
Train::Train(const string& input_id_train, const struct_stations input_ville_depart,
             const struct_stations input_ville_arrivee, const string& input_horaire_depart,
             const string& input_horaire_arrivee, int input_capacite, int input_places_libres)
        : id_train(input_id_train), ville_depart(input_ville_depart), ville_arrivee(input_ville_arrivee),
          horaire_depart(input_horaire_depart), horaire_arrivee(input_horaire_arrivee),
          capacite(input_capacite), places_libres(input_places_libres) {}

Train::~Train() {}

Billet::Billet(const string& input_id_billet, const string& input_type_classe, Train* input_BLT_train,
               const string& input_date_voyage)
        : id_billet(input_id_billet), type_classe(input_type_classe), BLT_train(input_BLT_train),
          date_voyage(input_date_voyage), prix(calculerPrix()) {}

Billet::~Billet() {}

Passager::Passager(const string& input_nom, const string& input_prenom, const string& input_id_passager)
        : nom(input_nom), prenom(input_prenom), id_passager(input_id_passager) {}

Passager::~Passager() {}

Reservation::Reservation(const string& input_id_reservation, Passager* input_RSV_passager, Billet* input_RSV_billet)
        : id_reservation(input_id_reservation), RSV_passager(input_RSV_passager), RSV_billet(input_RSV_billet) {}

Reservation::~Reservation() {}

// Train methods
void Train::verifierDisponibilite() const {
    cout << (places_libres > 0 ? "Disponible" : "Indisponible") << endl;
}

void Train::reserverPlace() {
    if (places_libres > 0) {
        places_libres--;
    } else {
        cout << "Aucune place disponible !" << endl;
    }
}

void Train::annulerReservation() {
    places_libres++;
}

void Train::afficherInfosTrain() const {
    cout << "Train ID : " << id_train << endl;
    cout << "Ville départ : " << ville_depart.station_name << endl;
    cout << "Ville destination : " << ville_arrivee.station_name << endl;
    cout << "Horaire départ : " << horaire_depart << endl;
    cout << "Horaire arrivée : " << horaire_arrivee << endl;
    cout << "Capacité : " << capacite << endl;
    cout << "Places disponibles : " << places_libres << endl;
}

// Billet methods
void Billet::afficherDetailsBillets() const {
    cout << "Billet ID : " << id_billet << endl;
    cout << "Classe : " << type_classe << endl;
    cout << "Prix : " << prix << endl;
    cout << "Date voyage : " << date_voyage << endl;
    BLT_train->afficherInfosTrain();
}

float Billet::calculerPrix() const {
    float distance = sqrt(
            pow(BLT_train->ville_arrivee.x - BLT_train->ville_depart.x, 2) +
            pow(BLT_train->ville_arrivee.y - BLT_train->ville_depart.y, 2)
    );

    if (type_classe == "premier") {
        return distance * 1.5;
    } else if (type_classe == "deuxieme") {
        return distance * 1.2;
    }
    return 0.0f;
}

// Passager methods
void Passager::ajouterReservation(const Billet* billet) {
    PSG_reservation.push_back(*billet);
}

void Passager::annulerReservation(const Billet* billet) {
    for (auto it = PSG_reservation.begin(); it != PSG_reservation.end();) {
        if (it->id_billet == billet->id_billet) {
            historiqueReservations.push_back(*it); // Move to history
            it = PSG_reservation.erase(it);
        } else {
            ++it;
        }
    }
}

void Passager::afficherReservations() const {
    cout << "Réservations pour " << nom << " " << prenom << " :\n";
    for (const Billet& billet : PSG_reservation) {
        billet.afficherDetailsBillets();
    }
}

void Passager::afficherHistorique() const {
    cout << "Historique des billets pour " << nom << " " << prenom << " :\n";
    for (const Billet& billet : historiqueReservations) {
        billet.afficherDetailsBillets();
    }
}

// Reservation methods
void Reservation::confirmerReservation() const {
    RSV_passager->ajouterReservation(RSV_billet);
    RSV_billet->BLT_train->reserverPlace();
}

void Reservation::annulerReservation() const {
    RSV_passager->annulerReservation(RSV_billet);
    RSV_billet->BLT_train->annulerReservation();
}

void Reservation::afficherDetailsReservation() const {
    cout << "Réservation ID : " << id_reservation << endl;
    RSV_passager->afficherReservations();
    RSV_billet->afficherDetailsBillets();
}

// Calendrier methods
void Calendrier::ajouterHoraire(const string& date, Train* train) {
    horaires[date].push_back(train);
}

void Calendrier::afficherCalendrier(const string& date) const {
    auto it = horaires.find(date);
    if (it != horaires.end()) {
        cout << "Horaires pour la date " << date << " :\n";
        for (const Train* train : it->second) {
            train->afficherInfosTrain();
        }
    } else {
        cout << "Aucun train prévu pour cette date.\n";
    }
}

// Helper functions
string generate_id(const string& prefix, vector<string>& storage_ID) {
    string new_id;
    do {
        new_id = prefix + to_string(rand() % 900000 + 100000);
    } while (find(storage_ID.begin(), storage_ID.end(), new_id) != storage_ID.end());
    storage_ID.push_back(new_id);
    return new_id;
}

void save_data_files(vector<Train*> train_data, vector<Billet*> billet_data, vector<Passager*> passager_data) {
    fstream train_file("trains.txt", ios::out);
    for (Train* train : train_data) {
        train_file << train->id_train << ";" << train->ville_depart.station_name << ";"
                   << train->ville_arrivee.station_name << ";" << train->horaire_depart << ";"
                   << train->horaire_arrivee << ";" << train->capacite << ";" << train->places_libres << "\n";
    }
    train_file.close();

    fstream billet_file("billets.txt", ios::out);
    for (Billet* billet : billet_data) {
        billet_file << billet->id_billet << ";" << billet->type_classe << ";"
                    << billet->BLT_train->id_train << ";" << billet->date_voyage << ";" << billet->prix << "\n";
    }
    billet_file.close();

    fstream passager_file("passagers.txt", ios::out);
    for (Passager* passager : passager_data) {
        for (const Billet& billet : passager->PSG_reservation) {
            passager_file << passager->nom << ";" << passager->prenom << ";" << passager->id_passager << ";"
                          << billet.id_billet << "\n";
        }
    }
    passager_file.close();
}

void extract_data_file(vector<Train*>& train_data, vector<Billet*>& billet_data,
                       vector<Passager*>& passager_data, vector<str_stations>& stations) {
    // Extraction logic similar to save_data_files
}
