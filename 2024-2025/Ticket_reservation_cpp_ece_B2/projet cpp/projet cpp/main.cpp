#include "header.h"
vector<string> storage_passagerID;
vector<string> storage_billetID;
vector<string> storage_reservationID;



int main() {
    srand(time(NULL));

    // Préfixes pour ID
    const string train_prefix = "TRN";
    const string passager_prefix = "PSG";
    const string billet_prefix = "BLT";
    const string reservation_prefix = "RSV";

    // Initialisation des données
    vector<Train*> train_data;
    vector<Billet*> billet_data;
    vector<Passager*> passager_data;
    vector<str_stations> stations;

    // Calendrier pour les horaires
    Calendrier calendrier;

    // Coordonnées des stations
    const vector<vector<int>> stations_locs = {
            {10, 5}, {20, 15}, {30, 25}, {40, 35}, {50, 45}
    };

    initialize_stations(stations, stations_locs);
    extract_data_file(train_data, billet_data, passager_data, stations);

    int choix = -1;

    while (choix != 0) {
        cout << "\n===== MENU PRINCIPAL =====\n";
        cout << "1. Réserver un billet\n";
        cout << "2. Annuler une réservation\n";
        cout << "3. Afficher mes réservations\n";
        cout << "4. Afficher l'historique\n";
        cout << "5. Afficher le calendrier des trains\n";
        cout << "0. Quitter\n";
        cout << "Votre choix : ";
        cin >> choix;

        switch (choix) {
            case 1: {
                // Réserver un billet
                string nom, prenom, type_classe, date_voyage;
                int choix_train;

                cout << "Liste des trains disponibles :\n";
                for (size_t i = 0; i < train_data.size(); ++i) {
                    cout << i + 1 << ". ";
                    train_data[i]->afficherInfosTrain();
                }

                cout << "Choisissez un train (numéro) : ";
                cin >> choix_train;

                if (choix_train < 1 || choix_train > train_data.size()) {
                    cout << "Choix invalide.\n";
                    break;
                }

                Train* train_choisi = train_data[choix_train - 1];
                if (train_choisi->places_libres <= 0) {
                    cout << "Aucune place disponible sur ce train.\n";
                    break;
                }

                cout << "Entrez votre nom : ";
                cin >> nom;
                cout << "Entrez votre prénom : ";
                cin >> prenom;
                cout << "Entrez la classe (premier/deuxieme) : ";
                cin >> type_classe;
                cout << "Entrez la date du voyage (JJ/MM/AAAA) : ";
                cin >> date_voyage;

                string id_passager = generate_id(passager_prefix, storage_passagerID);
                Passager* passager = new Passager(nom, prenom, id_passager);
                passager_data.push_back(passager);

                string id_billet = generate_id(billet_prefix, storage_billetID);
                Billet* billet = new Billet(id_billet, type_classe, train_choisi, date_voyage);
                billet_data.push_back(billet);

                string id_reservation = generate_id(reservation_prefix, storage_reservationID);
                Reservation reservation(id_reservation, passager, billet);
                reservation.confirmerReservation();

                cout << "Réservation effectuée avec succès !\n";
                break;
            }

            case 2: {
                // Annuler une réservation
                string id_reservation;
                cout << "Entrez l'ID de votre réservation : ";
                cin >> id_reservation;

                bool reservation_trouvee = false;
                for (auto it = billet_data.begin(); it != billet_data.end(); ++it) {
                    if ((*it)->id_billet == id_reservation) {
                        (*it)->BLT_train->annulerReservation();
                        reservation_trouvee = true;
                        billet_data.erase(it);
                        cout << "Réservation annulée avec succès.\n";
                        break;
                    }
                }

                if (!reservation_trouvee) {
                    cout << "Réservation introuvable.\n";
                }
                break;
            }

            case 3: {
                // Afficher les réservations
                string nom, prenom;
                cout << "Entrez votre nom : ";
                cin >> nom;
                cout << "Entrez votre prénom : ";
                cin >> prenom;

                bool passager_trouve = false;
                for (Passager* passager : passager_data) {
                    if (passager->nom == nom && passager->prenom == prenom) {
                        passager->afficherReservations();
                        passager_trouve = true;
                        break;
                    }
                }

                if (!passager_trouve) {
                    cout << "Passager introuvable.\n";
                }
                break;
            }

            case 4: {
                // Afficher l'historique
                string nom, prenom;
                cout << "Entrez votre nom : ";
                cin >> nom;
                cout << "Entrez votre prénom : ";
                cin >> prenom;

                bool passager_trouve = false;
                for (Passager* passager : passager_data) {
                    if (passager->nom == nom && passager->prenom == prenom) {
                        passager->afficherHistorique();
                        passager_trouve = true;
                        break;
                    }
                }

                if (!passager_trouve) {
                    cout << "Passager introuvable.\n";
                }
                break;
            }

            case 5: {
                // Afficher le calendrier des trains
                string date;
                cout << "Entrez une date (JJ/MM/AAAA) : ";
                cin >> date;

                calendrier.afficherCalendrier(date);
                break;
            }

            case 0:
                cout << "Merci d'avoir utilisé l'application. Au revoir !\n";
                break;

            default:
                cout << "Choix invalide. Veuillez réessayer.\n";
        }
    }

    // Sauvegarder les données
    save_data_files(train_data, billet_data, passager_data);

    // Libérer la mémoire
    for (Train* train : train_data) delete train;
    for (Billet* billet : billet_data) delete billet;
    for (Passager* passager : passager_data) delete passager;

    return 0;
}
