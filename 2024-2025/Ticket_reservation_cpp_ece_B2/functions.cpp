#include "header.h"

//define constructors

Train :: Train(
    const string& input_id_train,
    const struct_stations input_ville_depart,
    const struct_stations input_ville_arrivee,
    const string& input_horaire_depart,
    const string& input_horaire_arrivee,
    int input_capacite,
    int input_places_libres
) :
    id_train(input_id_train),
    ville_depart(input_ville_depart),
    ville_arrivee(input_ville_arrivee),
    horaire_depart(input_horaire_depart),
    horaire_arrivee(input_horaire_arrivee),
    capacite(input_capacite),
    places_libres(input_places_libres)
{}

string Train::get_idTrain()const
{
    return id_train;
}
string Train::get_horaireDepart()const
{
    return horaire_depart;
}
string Train::get_horaireArrivee()const
{
    return horaire_arrivee;
}
int Train::get_capacite()const
{
    return capacite;
}
int Train::get_places_libres()const
{
    return places_libres;
}

//modify
void Train::incr_places_libres()
{
    places_libres++;
}
void Train::decr_places_libres()
{
    places_libres--;
}

Billet :: Billet(
    const string& input_id_billet,
    const string& input_type_classe,
    Train* input_BLT_train,
    const string& input_date_voyage
) :
    id_billet(input_id_billet),
    type_classe(input_type_classe),
    BLT_train(input_BLT_train),
    date_voyage(input_date_voyage)
{
    calculerPrix();
    //cout << prix;
}
string Billet::get_id_billet()const
{
    return id_billet;
}
string Billet::get_type_classe()const
{
    return type_classe;
}
string Billet::get_date_voyage()const
{
    return date_voyage;
}
float Billet::get_prix()const
{
    return prix;
}

Passager :: Passager(

    const string& input_nom,
    const string& input_prenom,
    const string& input_id_passager
) :
    nom(input_nom),
    prenom(input_prenom),
    id_passager(input_id_passager)
{}

string Passager::get_nom()const
{
    return nom;
}
string Passager::get_prenom()const
{
    return prenom;
}
string Passager::get_id_passager()const
{
    return id_passager;
}
vector<Billet*>& Passager::get_PSG_reservation() {
    return PSG_reservation;
}

/*
vector<Billet*> Passager::get_PSG_historique_reservation()const
{
    return PSG_historique_reservation;
}*/


Reservation :: Reservation(
    const string& input_id_reservation,
    Passager* input_RSV_passager,
    Billet* input_RSV_billet
):
    id_reservation(input_id_reservation),
    RSV_passager(input_RSV_passager),
    RSV_billet(input_RSV_billet)


{}

Archives::Archives(const string& input_nom,
                   const string& input_prenom,
                   const string& input_id_passager):
    Passager(input_nom,input_prenom,input_id_passager)
{}


Train::~Train() {}
Billet::~Billet() {}
Passager::~Passager() {}
Reservation::~Reservation() {}
Calendrier::~Calendrier() {}



//methods
void Train ::verifierDisponibilite()const
{
    if (places_libres > 0)
    {
        cout << "disponible" << endl;
    }
    else
    {
        cout << "indisponible" << endl;
    }

}
void Train::afficherInfosTrain() const
{
    cout << "\n+---------------- Train Information ----------------+" << endl;
    cout << "| Train ID           : " << setw(30) << left << id_train << "|" << endl;
    cout << "| Ville Depart       : " << setw(30) << left << ville_depart.station_name << "|" << endl;
    cout << "| Ville Destination  : " << setw(30) << left << ville_arrivee.station_name << "|" << endl;
    cout << "| Horaire Depart     : " << setw(30) << left << horaire_depart << "|" << endl;
    cout << "| Horaire Arrivee    : " << setw(30) << left << horaire_arrivee << "|" << endl;
    cout << "| Capacite           : " << setw(30) << left << capacite << "|" << endl;
    cout << "| Places Disponibles : " << setw(30) << left << places_libres << "|" << endl;
    cout << "+--------------------------------------------------+\n" << endl;
}

void Billet::afficherDetailsBillets() const
{
    cout << "\n+---------------- Billet Details -----------------+" << endl;
    cout << "| Billet ID         : " << setw(30) << left << id_billet << "|" << endl;
    cout << "| Classe            : " << setw(30) << left << type_classe << "|" << endl;
    cout << "| Prix($)           : " << setw(30) << left << prix << "|" << endl;
    cout << "| Date Depart       : " << setw(30) << left << date_voyage << "|" << endl;
    cout << "+-------------------------------------------------+\n" << endl;
    //cout << "Train Information: " << endl;
    BLT_train->afficherInfosTrain();
}

void Billet :: calculerPrix()
{
    float calculated_distance = sqrt(pow(float(abs((BLT_train->ville_depart.x)-
                                         (BLT_train->ville_arrivee.x))), 2) +
                                     pow(float(abs((BLT_train->ville_depart.y)-
                                             (BLT_train->ville_arrivee.y))), 2));
    if(type_classe == "premier")
    {
        prix =  calculated_distance * 1.5;
        //cout << prix;
    }
    else if (type_classe == "deuxieme")
    {
        prix =  calculated_distance * 1.2;
        //cout << prix;
    }
    else
    {
        prix = 0.0;
    }
    //cout << prix;
}


void Passager::afficherInfo()
{
    string current_date = get_current_date();
    cout << "\n+---------------- Passager Information ----------------+" << endl;
    cout << "| ID               : " << setw(30) << left << id_passager << "|" << endl;
    cout << "| Nom              : " << setw(30) << left << nom << "|" << endl;
    cout << "| Prenom           : " << setw(30) << left << prenom << "|" << endl;
    cout << "+-----------------------------------------------------+" << endl;
    cout << "Reservations: " << endl;
    if (PSG_reservation.empty()) {
        cout << "  Aucun billet disponible." << endl;
    } else {
        size_t available_billet = 0;
        for (size_t i = 0; i < PSG_reservation.size(); i++) {

            string get_each_billet_date_var = PSG_reservation[i]->get_date_voyage();
            if(!is_date_old(current_date,get_each_billet_date_var)){
                available_billet++;
                cout << "  " << available_billet << ". " << PSG_reservation[i]->get_id_billet() << endl;
            }
        }
        if(available_billet == 0){
                cout << "  Aucun billet disponible." << endl;
        }

    }
    cout << "+-----------------------------------------------------+\n" << endl;
}


void Passager ::ajouterReservation(const Billet* billet)
{
    PSG_reservation.push_back(const_cast<Billet*>(billet)); // Store pointer
}


/*
void Passager::ajouterHistoriqueReservation(const Billet* billet)
{
    PSG_historique_reservation.push_back(const_cast<Billet*>(billet));
}
*/

void Passager::annulerReservation(const Billet* billet)
{
    for (auto it = PSG_reservation.begin(); it != PSG_reservation.end();)
    {
        if ((*it)->get_id_billet() == billet->get_id_billet())
        {
            delete *it; // Free the memory
            it = PSG_reservation.erase(it); // Erase and update iterator
        }
        else
        {
            ++it; // Increment only if no erasure
        }
    }
}

Billet* Passager::afficherReservations() const
{
    string current_date = get_current_date();
    cout << "\n=== Reservations pour " << nom << " " << prenom << " ===" << endl;

    if (PSG_reservation.empty()) {
        cout << "Pas de reservation disponible.\n";
        return nullptr;
    }

    cout << "+--------------------------------------------+" << endl;
    cout << "| No. | Billet ID   | Date Voyage   | Details |" << endl;
    cout << "+--------------------------------------------+" << endl;

    size_t reservation_count = 0;
    for (size_t i = 0; i < PSG_reservation.size(); ++i) {
        string get_billet_date_var = PSG_reservation[i]->get_date_voyage();
        if (!is_date_old(current_date, get_billet_date_var)) {
            reservation_count++;
            cout << "| " << setw(3) << reservation_count << " | "
                 << setw(10) << PSG_reservation[i]->get_id_billet() << " | "
                 << setw(13) << get_billet_date_var << " | ";
            PSG_reservation[i]->afficherDetailsBillets();
            cout << endl;
        }
    }

    if (reservation_count == 0) {
        cout << "| Aucun billet valide disponible            |" << endl;
        cout << "+--------------------------------------------+\n" << endl;
        return nullptr;
    } else {
        string get_input_billet_id_var;
        cout << "1. Retourner" << endl;
        cout << "2. Selectionner De Billet (Entrer Billet ID) : ";
        while (true) {
            cin >> get_input_billet_id_var;
            for (Billet* each_billet : PSG_reservation) {
                string get_each_billet_id_var = each_billet->get_id_billet();
                if (get_each_billet_id_var == get_input_billet_id_var) {
                    return each_billet;
                }
                if (get_input_billet_id_var == "1") {
                    return nullptr;
                }
            }
            cout << "[ERREUR] Billet ID Invalide.\n"
                 << "*Pour Retourner Tappes 1*" << endl;
            cin.clear();
            cin.ignore(1000, '\n');
        }
    }
}





/*
void Passager ::afficherHistoriqueReservation()const
{
    cout << "Historique des billets pour " << nom << " " << prenom << " :\n";
    if(!PSG_historique_reservation.empty())
    {
        for (Billet* PSG_billet : PSG_historique_reservation)
        {
            PSG_billet->afficherDetailsBillets();
            cout << endl << endl;
        }
    }
    else
    {
        cout << "Pas de reservation" << endl;
    }
}*/

void Reservation::confirmerReservation(vector<Passager*>& passager_data,
                                       vector<Billet*>& billet_data,
                                       Calendrier* calendrier_data) const
{
    Passager* target_passager = nullptr;
    for (Passager* each_passager : passager_data)
    {
        if (each_passager->get_id_passager() == RSV_passager->get_id_passager())
        {
            target_passager = each_passager;
            break;
        }
    }

    if (!target_passager)
    {
        cout << "Erreur : Passager ID non trouve dans passager_data." << endl;
        return;
    }
    billet_data.push_back(RSV_billet);
    bool train_found = false;
    for (const auto& [date, trains] : calendrier_data->train_schedule)
    {
        for (Train* each_train : trains)
        {
            if (each_train->get_idTrain() == RSV_billet->BLT_train->get_idTrain())
            {
                if (each_train->get_places_libres() > 0)
                {
                    each_train->decr_places_libres();
                    train_found = true;
                    break;
                }
                else
                {
                    cout << "Erreur : Aucun place libre sur ce train." << endl;
                    return;
                }
            }
        }
        if (train_found) break;
    }

    if (!train_found)
    {
        cout << "Erreur : Train ID non trouve dans calendrier_data." << endl;
        return;
    }
    target_passager->ajouterReservation(RSV_billet);

    cout << "Reservation confirmee avec succes pour le passager "
         << target_passager->get_nom() << " "
         << target_passager->get_prenom() << "." << endl;
}

void Reservation::annulerReservation(vector<Passager*>& passager_data,
                                     vector<Billet*>& billet_data,
                                     Calendrier* calendrier_data,
                                     bool was_confirmed) const
{
    if (was_confirmed)
    {
        for (Passager* each_passager : passager_data)
        {
            if (each_passager->get_id_passager() == RSV_passager->get_id_passager())
            {
                each_passager->annulerReservation(RSV_billet);
                break;
            }
        }
        for (auto& [date, trains] : calendrier_data->train_schedule)
        {
            for (Train* each_train : trains)
            {
                if (each_train->get_idTrain() == RSV_billet->BLT_train->get_idTrain())
                {
                    each_train->incr_places_libres();
                    break;
                }
            }
        }

        auto billet_it = std::remove_if(billet_data.begin(), billet_data.end(),
                                        [this](Billet* each_billet)
        {
            return each_billet->get_id_billet() == RSV_billet->get_id_billet();
        });

        if (billet_it != billet_data.end())
        {
            delete *billet_it;  // Free memory for the billet
            billet_data.erase(billet_it, billet_data.end());  // Erase from the vector
        }
    }

    // Step 4: Clean up the reservation object regardless of confirmation state
    delete this; // Assuming `this` is dynamically allocated.
}






void Reservation::afficherDetailsReservation() const
{
    cout << "\n+---------------- Reservation Details ----------------+" << endl;
    cout << "| Reservation ID   : " << setw(30) << left << id_reservation << "|" << endl;
    cout << "+-----------------------------------------------------+" << endl;
    //cout << "Passager Information: " << endl;
    RSV_passager->afficherInfo();
    //cout << "Billet Information: " << endl;
    RSV_billet->afficherDetailsBillets();
    //cout << "+-----------------------------------------------------+\n" << endl;
}

/*
void initialize_train_vector(vector<Train*>& train_data);


void Calendrier::initialize_train_schedule()
{
    // Get today's date
    auto today = std::chrono::system_clock::now();
    std::time_t current_time = std::chrono::system_clock::to_time_t(today);
    std::tm* current_date = std::localtime(&current_time);

    // Iterate over the next 30 days
    for (int i = 0; i < 5; ++i)
    {
        std::tm next_date = *current_date;
        next_date.tm_mday += i; // Add days
        std::mktime(&next_date); // Normalize the date structure

        // Format the date as "YYYY-MM-DD"
        std::ostringstream date_stream;
        date_stream << std::put_time(&next_date, "%Y-%m-%d");
        std::string date_str = date_stream.str();

        // Check if the date is already in the map
        if (train_schedule.find(date_str) == train_schedule.end())
        {
            // Initialize a vector of Train* for the new date
            vector<Train*> trains_for_day;
            initialize_train_vector(trains_for_day); // Assuming this function initializes train data
            train_schedule[date_str] = trains_for_day;
        }
    }
}
*/
void Calendrier::import_train_schedule(const map<string, vector<Train*>>& input_schedule)
{
    // Import all dates from input_schedule
    for (const auto& [date, trains] : input_schedule)
    {
        // If the date already exists, append the trains to the existing vector
        if (train_schedule.find(date) != train_schedule.end())
        {
            train_schedule[date].insert(train_schedule[date].end(), trains.begin(), trains.end());
        }
        else
        {
            // If the date does not exist, create a new entry
            train_schedule[date] = trains;
        }
    }
    //cout << "Importation complete: nouvelles dates ajoutees." << endl;
}


void Calendrier::afficher_calendrier() const
{
    cout << "\n+-------------------------------------------------+" << endl;
    cout << "|           === Calendrier des Trains ===         |" << endl;
    cout << "+-------------------------------------------------+" << endl;

    cout << "========================================" << endl;
    cout << "|      Date       |  Nombre de Trains  |" << endl;
    cout << "========================================" << endl;

    auto today = std::chrono::system_clock::now();//get today date
    time_t current_time = std::chrono::system_clock::to_time_t(today); //convert into seconds from 1970
    tm* current_date = std::localtime(&current_time); //convert seconds into date structure (year,month,day)

    for (int i = 0; i <= 30; ++i)
    {
        tm next_date = *current_date;
        next_date.tm_mday += i; // add a day.
        mktime(&next_date);

        ostringstream date_stream;
        date_stream << put_time(&next_date, "%Y-%m-%d");
        string date_str = date_stream.str();

        auto it = train_schedule.find(date_str);
        int train_count = 0;

        if (it != train_schedule.end())
        {
            const vector<Train*>& trains = it->second;
            train_count = static_cast<int>(trains.size());
        }

        cout << "| " << setw(15) << date_str << " | "
             << setw(18) << train_count << " |" << endl;
    }

    cout << "========================================" << endl;
}




/*void Calendrier::afficher_calendrier() const
{
    cout << "=== Calendrier des Trains ===" << endl;

    for (const auto& [date, trains] : train_schedule)
    {
        cout << "Date: " << date << endl;
        if (trains.empty())
        {
            cout << "  Aucun train pour cette date." << endl;
        }
        else
        /*{
            cout << "Train ID : ";
            for (const Train* train : trains)
            {
                string get_id_train = train->get_idTrain();
                cout << get_id_train <<", " ;
            }
            cout << endl;
        }
        cout << endl;
    }
}*/

string Calendrier::demander_date() const
{
    string date_str;
    int year, month, day;

    while (true)
    {
        cout << "=== Demander une Date ===" << endl;

        // Get year
        while (true)
        {
            cout << "Entrez l'annee (format AAAA) : ";
            cin >> year;
            if (cin.fail() || year < 2024 || year > 3000)
            {
                cout << "Erreur : Veuillez entrer une annee valide.\n";
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
            }
            else
            {
                break;
            }
        }

        // Get month
        while (true)
        {
            cout << "Entrez le mois (format MM) : ";
            cin >> month;
            if (cin.fail() || month < 1 || month > 12)
            {
                cout << "Erreur : Veuillez entrer un mois valide (1-12).\n";
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
            }
            else
            {
                break;
            }
        }

        // Get day
        while (true)
        {
            cout << "Entrez le jour (format JJ) : ";
            cin >> day;
            if (cin.fail() || day < 1 || day > 31)
            {
                cout << "Erreur : Veuillez entrer un jour valide (1-31).\n";
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
            }
            else
            {
                break;
            }
        }

        // Format date as YYYY-MM-DD

        ostringstream date_stream;
        date_stream << setfill('0') << setw(4) << year << "-"
                    << setw(2) << month << "-"
                    << setw(2) << day;
        date_str = date_stream.str();//conversion into string format YYYY-MM-DD

        // Check if the date exists in the schedule

        string current_date = get_current_date();
        if (train_schedule.find(date_str) != train_schedule.end() && !is_date_old(current_date,date_str))//if doesn't find the key-value pair, return iterator equal to .end() iterator (end of map)
        {
            return date_str; // Date is valid and exists
        }
        else
        {
            cout << "Erreur : Date non disponible dans le calendrier.\n";
            cout << "Voulez-vous reessayer ? (o/n) : ";
            while(true)
            {
                char retry;
                cin >> retry;
                if (retry == 'n' || retry == 'N' )
                {
                    return "";
                }
                else if(retry == 'o' || retry == 'O')
                {
                    break;
                }
                else
                {
                    cout << "Erreur: Veuillez entrer 'o' pour continuer ou 'n' pour annuler. >> : ";
                    cin.clear();
                    cin.ignore(numeric_limits<streamsize>::max(), '\n');
                }
            }

        }
    }
}




Train* Calendrier::search_trains(const string& date) const
{
    auto it = train_schedule.find(date);
    if (it == train_schedule.end())
    {
        cout << "Aucune donnee disponible pour la date selectionnee.\n";
        return nullptr;
    }

    const vector<Train*>& trains = it->second;
    vector<Train*> trains_filtered_dst_dprt;

    if (trains.empty())
    {
        cout << "Aucun train planifie pour la date selectionnee.\n";
        return nullptr;
    }

    // Get departure and destination stations
    cout << "=== Selection de la station de depart ===\n";
    string depart = get_station_name();
    if (depart.empty())
    {
        return nullptr; // User chose to return
    }

    cout << "=== Selection de la station de destination ===\n";
    string dest = get_station_name();
    if (dest.empty())
    {
        return nullptr; // User chose to return
    }

    if (depart == dest)
    {
        cout << "Erreur : La station de depart et de destination doivent etre differentes.\n";
        return nullptr;
    }

    // Filter trains based on departure and destination
    cout << "=== Trains pour le " << date << " [" << depart << " -> " << dest << "] ===\n";
    for (const Train* train : trains)
    {
        if (train->ville_depart.station_name == depart &&
                train->ville_arrivee.station_name == dest)
        {
            trains_filtered_dst_dprt.push_back(const_cast<Train*>(train));
            cout << trains_filtered_dst_dprt.size() << ". ";
            train->afficherInfosTrain();
            cout << endl;
        }
    }

    // If no trains match the criteria
    if (trains_filtered_dst_dprt.empty())
    {
        cout << "Erreur : Aucun train disponible pour le trajet selectionne.\n";
        return nullptr;
    }

    // User selects a train from the filtered list
    while (true)
    {
        cout << "Entrez le numero du train a selectionner ou '0' pour retourner : ";
        int choix;
        cin >> choix;

        if (!cin || choix < 0 || choix > static_cast<int>(trains_filtered_dst_dprt.size()))
        {
            cout << "Erreur: Veuillez entrer un numero valide.\n";
            cin.clear();
            cin.ignore(1000, '\n');
        }
        else if (choix == 0)
        {
            return nullptr; // User chose to return
        }
        else
        {
            int get_places_libres_var = trains_filtered_dst_dprt[choix - 1]->get_places_libres();
            if(get_places_libres_var == 0)
            {
                cout << "Train non disponible" << endl;
                return nullptr;
            }
            return trains_filtered_dst_dprt[choix - 1];
        }
    }
}

void Archives::ajouter_historiqueReservations(Billet* cancel_billet, string motiv)
{
    if (!cancel_billet)
    {
        cerr << "Error: Attempting to add a null billet to archives." << endl;
        return;
    }
    //cout << "getting billet id .." << endl;
    //cout << "debugging billet vector" << endl;
    //cancel_billet->afficherDetailsBillets();
    string get_billet_id_var = cancel_billet->get_id_billet();
    //cout << "Entering Loop archived_billets" << endl;
    // Check if the billet is already in archives
    for (const auto& [each_billet, each_motiv] : archived_billets)
    {
        //cout << "looping in archived_billets map ..." << endl;
        string get_each_billet_id_var = each_billet->get_id_billet();
        if (get_billet_id_var == get_each_billet_id_var)
        {
            //cout << "Billet already in archives: " << get_billet_id_var << endl;
            return;
        }
    }

    // Add the billet to archives
    //cout << "adding to map..." << endl;
    archived_billets[cancel_billet] = motiv;
    //cout << "added." << endl;
    //cout << "Billet ID: " << get_billet_id_var << " added to archives with motive: " << motiv << endl;
}



void Archives::afficherArchives() const
{
    cout << "+-------------------------------------------------+" << endl;
    cout << "|               Passenger Archives                |" << endl;
    cout << "+-------------------------------------------------+" << endl;
    cout << "| Name          | " << get_nom() << " " << get_prenom() << "                     |" << endl;
    cout << "| Passenger ID  | " << get_id_passager() << "                             |" << endl;
    cout << "+-------------------------------------------------+" << endl;

    if (archived_billets.empty())
    {
        cout << "| No archived billets available                  |" << endl;
        cout << "+-------------------------------------------------+" << endl;
        return;
    }

    cout << "| Billet ID       | Motive                       |" << endl;
    cout << "+-----------------+-----------------------------+" << endl;

    for (const auto& [billet, motive] : archived_billets)
    {
        cout << "| " << setw(15) << billet->get_id_billet()
             << " | " << setw(28) << motive << " |" << endl;
    }

    cout << "+-------------------------------------------------+" << endl;
}




