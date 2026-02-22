#include "header.h"
//get current date
string get_current_date()
{
    auto today = std::chrono::system_clock::now();//get today date
    time_t time_in_seconds = std::chrono::system_clock::to_time_t(today); //convert into seconds from 1970
    tm* date_structure = std::localtime(&time_in_seconds); //convert seconds into date structure (year,month,day)


    // Use ostringstream to format the date as YYYY-MM-DD
    ostringstream date_oss;
    date_oss << setw(4) << (date_structure->tm_year + 1900) << "-"
             << setfill('0') << setw(2) << (date_structure->tm_mon + 1) << "-"
             << setfill('0') << setw(2) << date_structure->tm_mday;


    return date_oss.str();
}

bool is_date_old(string& base_date, string& given_date)
{
    return given_date < base_date;
}



// generate id
string generate_id(const string& prefix, vector<string>& storage_ID)
{
    string new_id;
    bool unique_flag;
    int max_attempts = 1000;
    int attempts = 0;

    do
    {
        if (attempts++ > max_attempts)
        {
            cout << "Error: Failed to generate unique ID!" << endl;
            return "";
        }
        unique_flag = true;
        new_id = prefix + to_string(rand() % 900000 + 100000);
        for (const string& ID : storage_ID)
        {
            if (new_id == ID)
            {
                unique_flag = false;
                break;
            }
        }
    }
    while (!unique_flag);

    storage_ID.push_back(new_id);
    return new_id;
}




void initialize_stations(
    vector<str_stations>& stations,
    const vector<vector<int>>& stations_locs
)
{
    stations.resize(5);
    stations[0] = {"STR01", "Aberion", stations_locs[0][0], stations_locs[0][1]};
    stations[1] = {"STR02", "Brayden", stations_locs[1][0], stations_locs[1][1]};
    stations[2] = {"STR03", "Cameron", stations_locs[2][0], stations_locs[2][1]};
    stations[3] = {"STR04", "Delmont", stations_locs[3][0], stations_locs[3][1]};
    stations[4] = {"STR05", "Eldon", stations_locs[4][0], stations_locs[4][1]};
}




void generate_trainmap(const vector<vector<int>> & stations_locs, const int map_width, const int map_height)
{
    cout << "\n+-------------------------------------------------+" << endl;
    cout << "|                  Train Map                      |" << endl;
    cout << "+-------------------------------------------------+" << endl;

    for (const auto& loc : stations_locs)
    {
        if (loc[0] < 0 || loc[0] >= map_width || loc[1] < 0 || loc[1] >= map_height)
        {
            cout << "Error: Station location out of bounds!" << endl;
            return;
        }
    }

    bool is_station = false;
    for (int y = 0; y < map_height; y++)
    {
        for (int x = 0; x < map_width; x++)
        {
            is_station = false;


            if (y == 0 || y == map_height - 1)
            {
                cout << "_";
            }

            else if (x == 0 || x == map_width - 1)
            {
                cout << "|";
            }

            else if (
                (x == stations_locs[0][0] && y == stations_locs[0][1]) ||
                (x == stations_locs[1][0] && y == stations_locs[1][1]) ||
                (x == stations_locs[2][0] && y == stations_locs[2][1]) ||
                (x == stations_locs[3][0] && y == stations_locs[3][1]) ||
                (x == stations_locs[4][0] && y == stations_locs[4][1])
            )
            {
                is_station = true;
                if (x == stations_locs[0][0] && y == stations_locs[0][1])
                {
                    cout << "A";
                }
                else if (x == stations_locs[1][0] && y == stations_locs[1][1])
                {
                    cout << "B";
                }
                else if (x == stations_locs[2][0] && y == stations_locs[2][1])
                {
                    cout << "C";
                }
                else if (x == stations_locs[3][0] && y == stations_locs[3][1])
                {
                    cout << "D";
                }
                else if (x == stations_locs[4][0] && y == stations_locs[4][1])
                {
                    cout << "E";
                }
            }


            if (!is_station && x != 0 && x != map_width - 1 && y != 0 && y != map_height - 1)
            {
                cout << " ";
            }
        }
        cout << endl;
    }
}





void save_data_files(vector<Archives*> archives_data,
                     vector<Billet*> billet_data,
                     vector<Passager*> passager_data,
                     Calendrier* calendrier_data)
{
    cout << "\n+-------------------------------------------------+" << endl;
    cout << "|               Saving Passager Data             |" << endl;
    cout << "+-------------------------------------------------+" << endl;

    fstream user_management_file("user_management_file.txt", ios::out);
    for (Passager* each_passager : passager_data)
    {
        vector<Billet*> get_PSG_reservation_VAR = each_passager->get_PSG_reservation();
        if (get_PSG_reservation_VAR.empty())
        {
            user_management_file << each_passager->get_nom() << ";"
                                 << each_passager->get_prenom() << ";"
                                 << each_passager->get_id_passager() << endl;

        }
        else
        {
            for (Billet* each_billet : get_PSG_reservation_VAR)
            {
                user_management_file << each_passager->get_nom() << ";"
                                     << each_passager->get_prenom() << ";"
                                     << each_passager->get_id_passager() << ";"
                                     << each_billet->get_id_billet() << endl;
            }
        }
    }
    user_management_file.close();
    cout << "Saved passager data to 'user_management_file.txt'\n";

    cout << "Saving Archives Data..." << endl;
    fstream archives_file("archives.txt", ios::out);
    for (Archives* each_archive : archives_data)
    {
        for (const auto& [each_billet, each_motive] : each_archive->archived_billets)
        {
            archives_file << each_archive->get_nom() << ";"
                          << each_archive->get_prenom() << ";"
                          << each_archive->get_id_passager() << ";"
                          << each_billet->get_id_billet() << ";"
                          << each_motive << endl;
        }
    }
    archives_file.close();
    cout << "Saved archives data to 'archives.txt'\n";

    cout << "Saving Billet Data..." << endl;
    fstream billet_management_file("billet_management_file.txt", ios::out);
    for (Billet* each_billet : billet_data)
    {
        billet_management_file << each_billet->get_id_billet() << ";"
                               << each_billet->get_type_classe() << ";"
                               << each_billet->BLT_train->get_idTrain() << ";"
                               << each_billet->get_date_voyage() << ";"
                               << each_billet->get_prix() << endl;
    }
    billet_management_file.close();
    cout << "Saved billet data to 'billet_management_file.txt'\n";

    cout << "Saving Train Data..." << endl;
    fstream train_management_file("train_management_file.txt", ios::out);
    for (const auto& [date, trains] : calendrier_data->train_schedule)
    {
        for (Train* each_train : trains)
        {
            if (!each_train) continue;
            train_management_file << each_train->get_idTrain() << ";"
                                  << each_train->ville_depart.station_name << ";"
                                  << each_train->ville_arrivee.station_name << ";"
                                  << each_train->get_horaireDepart() << ";"
                                  << each_train->get_horaireArrivee() << ";"
                                  << each_train->get_capacite() << ";"
                                  << each_train->get_places_libres() << ";"
                                  << date << endl;
        }
    }
    train_management_file.close();
    cout << "Saved train data to 'train_management_file.txt'\n";
}



void extract_data_file(
    /*vector <Train*>& train_data,*/
    vector<str_stations>& stations,
    vector <Billet*>& billet_data,
    vector<Passager*>& passager_data,
    vector<Archives*>& archives_data,
    Calendrier* calendrier_data
)
{
    vector<Billet*> old_billets;

    //cout << "extracting train data ..."<< endl;

    cout << "\n+-------------------------------------------------+" << endl;
    cout << "|                  Extracting Data                |" << endl;
    cout << "+-------------------------------------------------+" << endl;

// ------------------------- Extract Train Data -------------------------
    cout << "Extracting from 'train_management_file.txt'..." << endl;
    fstream train_management_file("train_management_file.txt", ios::in);
    if (!train_management_file.is_open())
    {
        cerr << "[Error] Could not open 'train_management_file.txt'. A new file will be created." << endl;
        train_management_file.open("train_management_file.txt", ios::out);
    }

    string line;
    while (getline(train_management_file, line))
    {
        //cout << "getting lines from train"<<endl;
        string field;
        vector<string> fields;

        for (char ch : line)
        {
            if (ch == ';')
            {
                fields.push_back(field);
                field.clear();
            }
            else
            {
                field += ch;
            }
        }
        if (!field.empty())
        {
            fields.push_back(field);
        }

        //cout << "fields extracted ..." << endl;
        if (fields.size() == 8)
        {
            // Process train data
            str_stations str_ville_arrive, str_ville_depart;
            for (const str_stations& each_station : stations)
            {
                if (each_station.station_name == fields[1]) str_ville_depart = each_station;
                if (each_station.station_name == fields[2]) str_ville_arrive = each_station;
            }

            Train* new_train = new Train(
                fields[0], str_ville_depart, str_ville_arrive, fields[3], fields[4],
                stoi(fields[5]), stoi(fields[6])
            );

            string train_date = fields[7];
            calendrier_data->import_train_schedule({{train_date, {new_train}}});
            storage_trainID.push_back(fields[0]);
        }
        else
        {
            cerr << "[Error] Invalid train data: " << line << endl;
        }
    }
    //calendrier_data->afficher_calendrier();

    train_management_file.close();
    cout << "Train data extraction complete." << endl;


    // ------------------------- Extract Billet Data -------------------------
    cout << "Extracting from 'billet_management_file.txt'..." << endl;
    fstream billet_management_file;
    billet_management_file.open("billet_management_file.txt", ios::in);

    if (!billet_management_file.is_open())
    {
        cerr << "[Error] Could not open 'billet_management_file.txt'. A new file will be created." << endl;
        billet_management_file.open("billet_management_file.txt", ios::out);
    }

    while (getline(billet_management_file, line))
    {
        string field;
        vector<string> fields;

        for (char ch : line)
        {
            if (ch == ';')
            {
                fields.push_back(field);
                field.clear();
            }
            else
            {
                field += ch;
            }
        }
        if (!field.empty())
        {
            fields.push_back(field);
        }
        if (fields.size() != 5)
        {
            cerr << "[Error] Invalid billet data: " << line << endl;
            continue;
        }

        // Extract Train object by Train ID
        Train* extract_train_data = nullptr;
        for (const auto& [date,trains] : calendrier_data->train_schedule)
        {

            for(Train* each_train : trains)
            {
                string get_train_id_var = each_train->get_idTrain();
                if (get_train_id_var == fields[2])
                {
                    extract_train_data = each_train;
                    break;
                }
            }

        }

        if (extract_train_data == nullptr)
        {
            cerr << "[Error] No matching train for billet ID: " << fields[0] << endl;
            continue;
        }

        // Create Billet object and store it in billet_data vector
        Billet* extract_billet_data = new Billet(
            fields[0],           // Billet ID
            fields[1],           // Type Classe
            extract_train_data,  // Reference to Train object
            fields[3]            // Date Voyage
        );
        //extract_billet_data->afficherDetailsBillets();
        string current_date = get_current_date();
        if(is_date_old(current_date,fields[3]))
        {
            //cout << "outdate billet detected" << endl;
            old_billets.push_back(extract_billet_data);
        }
        billet_data.push_back(extract_billet_data);
        storage_billetID.push_back(fields[0]); // Store billet ID
        // Clear fields for the next line
        fields.clear();
    }

    billet_management_file.close();
    cout << "Billet data extraction complete." << endl;

    // ------------------------- Extract Passager Data -------------------------
    cout << "Extracting from 'user_management_file.txt'..." << endl;


    //cout << "extracting passager data" << endl;


// Open the file
    fstream passager_management_file("user_management_file.txt", ios::in);
    if (!passager_management_file.is_open())
    {
        cerr << "[Error] Could not open 'user_management_file.txt'. A new file will be created." << endl;
        passager_management_file.open("user_management_file.txt", ios::out);
    }

    while (getline(passager_management_file, line))
    {
        vector<string> fields;
        string field;
        for (char ch : line)
        {
            if (ch == ';')
            {
                fields.push_back(field);
                field.clear();
            }
            else
            {
                field += ch;
            }
        }
        if (!field.empty()) fields.push_back(field);

        if (!fields.empty())
        {
            // Fields: 0 - nom, 1 - prenom, 2 - passenger ID, 3 - billet reservation (optional)
            string passenger_id = fields[2];
            string billet_id = (fields.size() > 3) ? fields[3] : "NONE";

            bool passager_found_flag = false;
            Billet* psg_billet_extraction = nullptr;

            // Locate billet by ID
            if (billet_id != "NONE")
            {
                for (Billet* each_billet : billet_data)
                {
                    if (each_billet->get_id_billet() == billet_id)
                    {
                        psg_billet_extraction = each_billet;
                        break;
                    }
                }
                if (!psg_billet_extraction)
                {
                    cerr << "[Warning] No matching billet found for ID: " << billet_id << endl;
                }
            }

            // Check if the passenger already exists
            for (Passager* each_passager : passager_data)
            {
                if (each_passager->get_id_passager() == passenger_id)
                {
                    if (psg_billet_extraction)
                    {
                        each_passager->ajouterReservation(psg_billet_extraction);
                    }
                    passager_found_flag = true;
                    break;
                }
            }

            // Create new Passager object if not found
            if (!passager_found_flag)
            {
                Passager* new_passager = new Passager(fields[0], fields[1], passenger_id);
                if (psg_billet_extraction)
                {
                    new_passager->ajouterReservation(psg_billet_extraction);
                }
                passager_data.push_back(new_passager);
                storage_passagerID.push_back(passenger_id);
            }

            // Handle outdated billets for archiving
            if (psg_billet_extraction)
            {
                string current_date = get_current_date();
                string get_billet_date_var = psg_billet_extraction->get_date_voyage();
                if (is_date_old(current_date,get_billet_date_var ))
                {
                    bool archive_found = false;
                    for (Archives* each_archive : archives_data)
                    {
                        if (each_archive->get_id_passager() == passenger_id)
                        {
                            each_archive->ajouter_historiqueReservations(psg_billet_extraction, "Terminee");
                            archive_found = true;
                            break;
                        }
                    }
                    if (!archive_found)
                    {
                        Archives* new_archive = new Archives(fields[0], fields[1], passenger_id);
                        new_archive->ajouter_historiqueReservations(psg_billet_extraction, "Terminee");
                        archives_data.push_back(new_archive);
                    }
                }
            }
        }
    }
    passager_management_file.close();
    cout << "Passager data extraction complete." << endl;



    // Archives extraction logic
    cout << "Extracting from 'archives.txt'..." << endl;

    fstream archives_file("archives.txt", ios::in);
    if (!archives_file.is_open())
    {
        cerr << "[Error] Could not open 'archives.txt'. A new file will be created." << endl;
        archives_file.open("archives.txt", ios::out);
        return; // If the file is empty, no data to extract
    }


    while (getline(archives_file, line))
    {
        vector<string> fields;
        string field;
        for (char ch : line)
        {
            if (ch == ';')
            {
                fields.push_back(field);
                field.clear();
            }
            else
            {
                field += ch;
            }
        }
        if (!field.empty()) fields.push_back(field);

        if (fields.size() != 5)   // Ensure valid data format
        {
            cerr << "[Error] Invalid archive entry: " << line << endl;
            continue;
        }

        // Fields: 0 - nom, 1 - prenom, 2 - passager_id, 3 - billet_id, 4 - motive
        string nom = fields[0];
        string prenom = fields[1];
        string passager_id = fields[2];
        string billet_id = fields[3];
        string motive = fields[4];

        // Locate or create the archive for this passager
        Archives* target_archive = nullptr;
        for (Archives* each_archive : archives_data)
        {
            if (each_archive->get_id_passager() == passager_id)
            {
                target_archive = each_archive;
                break;
            }
        }

        if (!target_archive)
        {
            target_archive = new Archives(nom, prenom, passager_id);
            archives_data.push_back(target_archive);
        }

        // Locate the billet
        Billet* target_billet = nullptr;
        for (Billet* each_billet : billet_data)
        {
            if (each_billet->get_id_billet() == billet_id)
            {
                target_billet = each_billet;
                break;
            }
        }

        if (!target_billet)
        {
            cerr << "[Warning] Billet ID " << billet_id << " not found for passager ID: " << passager_id << endl;
            continue;
        }

        // Add billet to the archive
        target_archive->ajouter_historiqueReservations(target_billet, motive);
    }

    archives_file.close();
    cout << "Archives data extraction complete." << endl;


}


void initialize_train_vector(Calendrier* calendrier_data)
{
    const int capacite = 100;

    if (stations.empty())
    {
        cerr << "Erreur: Liste de stations vide." << endl;
        return;
    }

    if (calendrier_data == nullptr)
    {
        cerr << "Erreur: Objet Calendrier non initialise." << endl;
        return;
    }

    // Prepare date range (next 30 days)
    auto today = chrono::system_clock::now();
    vector<string> dates;
    for (int i = 0; i <= 30; ++i)
    {
        auto current_date = today + chrono::hours(24 * i); // Add 24 hours for each day
        time_t time = chrono::system_clock::to_time_t(current_date);
        tm* tm = localtime(&time);
        ostringstream oss;
        oss << put_time(tm, "%Y-%m-%d");
        dates.push_back(oss.str());
    }

    int num_stations = stations.size();
    vector<string> horaires_depart = {"9:00", "15:00", "21:00"};
    vector<string> horaires_arrivees = {"12:00", "18:00", "00:00"};

    // Iterate over dates and ensure each date has a valid schedule
    for (const auto& date : dates)
    {
        if (calendrier_data->train_schedule.find(date) == calendrier_data->train_schedule.end())
        {
            // No schedule exists for this date, create new trains
            vector<Train*> trains_for_date;
            for (int i = 0; i < num_stations; i++)
            {
                for (int j = 0; j < num_stations; j++)
                {
                    if (stations[i].id_station != stations[j].id_station)
                    {
                        for (size_t h = 0; h < horaires_depart.size(); h++)
                        {
                            string new_id = generate_id(train_prefix, storage_trainID);
                            Train* new_train = new Train(
                                new_id,
                                stations[i],
                                stations[j],
                                horaires_depart[h],
                                horaires_arrivees[h],
                                capacite,
                                capacite
                            );
                            //train_data.push_back(new_train);
                            trains_for_date.push_back(new_train);
                        }
                    }
                }
            }
            // Add the trains for this date to the calendar
            calendrier_data->train_schedule[date] = trains_for_date;
        }
    }
}

string get_station_name()
{
    int choix;
    int num_choix = static_cast<int>(stations.size()) + 1;

    for (size_t i = 0; i < stations.size(); i++)
    {
        cout << i + 1 << ". " << stations[i].station_name << endl;
    }
    cout << num_choix << ". Retourner." << endl;

    while (true)
    {
        cout << "Selectionnez une station (1 - " << num_choix << "): ";
        cin >> choix;

        if (choix < 1 || choix > num_choix || cin.fail())
        {
            cout << "Erreur : veuillez entrer un numero valide entre 1 et " << num_choix << "." << endl;
            cin.clear();
            cin.ignore(1000, '\n');
        }
        else
        {
            break;
        }
    }

    if (choix == num_choix)
    {
        return "";
    }
    else
    {
        return stations[choix - 1].station_name;
    }
}

int menu_principal()
{
    vector<string> options = {"Voir Calendrier", "Voir Passagers", "Reservations","Quitter"};
    int choix = -1;

    while (true)
    {
        cout << "=== Menu Principal ===" << endl;
        for (size_t i = 0; i < options.size(); i++)
        {
            cout << i + 1 << ". " << options[i] << endl;
        }
        cout << "Veuillez entrer votre choix (1-" << options.size() << "): ";

        cin >> choix;

        if (cin.fail() || choix < 1 || choix > static_cast<int>(options.size()))
        {
            cout << "Erreur: Veuillez entrer un nombre valide." << endl;
            cin.clear();
            cin.ignore(1000, '\n');
        }
        else
        {
            break;
        }
    }
    return choix;
}


int menu_billet_class(const vector<string> options, Train* selected_train) {
    string get_selected_train_depart_var = (selected_train->ville_depart).station_name;

    float calculated_distance = sqrt(pow(float((selected_train->ville_depart.x) -
                                               (selected_train->ville_arrivee.x)), 2) +
                                     pow(float((selected_train->ville_depart.y) -
                                               (selected_train->ville_arrivee.y)), 2));

    float prix_premier_var = calculated_distance * 1.5;
    float prix_deuxieme_var = calculated_distance * 1.2;
    vector<float> calculated_prix = {prix_premier_var, prix_deuxieme_var};

    int choix = -1;

    while (true) {
        cout << "\n=== Choisir une Classe ===" << endl;
        cout << "+--------------------------------------------+" << endl;
        cout << "| No. | Classe            | Prix ($)         |" << endl;
        cout << "+--------------------------------------------+" << endl;
        for (size_t i = 0; i < options.size(); i++) {
            cout << "| " << setw(3) << i + 1 << " | " << setw(17) << options[i]
                 << " | " << setw(16) << fixed << setprecision(2) << calculated_prix[i] << " |" << endl;
        }
        cout << "+--------------------------------------------+" << endl;
        cout << "Veuillez entrer votre choix (1-" << options.size() << "): ";

        cin >> choix;

        if (cin.fail() || choix < 1 || choix > static_cast<int>(options.size())) {
            cout << "Erreur: Veuillez entrer un nombre valide." << endl;
            cin.clear();
            cin.ignore(1000, '\n');
        } else {
            break;
        }
    }
    return choix - 1;
}


void menu_reservation(vector<Reservation*>& reservation_data,
                      vector<Billet*>& billet_data,
                      vector<Passager*>& passager_data,
                      Calendrier* calendrier_data,
                      Reservation* new_reservation)
{
    // Display reservation(s)
    cout << "=== Liste des Reservations ===\n";
    if (new_reservation != nullptr)
    {
        new_reservation->afficherDetailsReservation();
    }
    else if (!reservation_data.empty())
    {
        for (Reservation* each_reservation : reservation_data)
        {
            each_reservation->afficherDetailsReservation();
        }
    }
    else
    {
        cout << "Aucune reservation disponible.\n";
        return;
    }

    // User action menu
    int choix = -1;
    cout << "[1] Confirmer une reservation\n"
         << "[2] Annuler une reservation\n"
         << "[3] Quitter\n";

    while (true)
    {
        cin >> choix;
        if (cin.fail() || choix < 1 || choix > 3)
        {
            cout << "Erreur: Veuillez entrer un nombre valide (1-3).\n";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
        else
        {
            break;
        }
    }

    // Handle user choice
    if (choix == 1) // Confirm reservation
    {
        cout << "Entrez l'ID de reservation a confirmer : ";
        string input_reservation_id;
        cin >> input_reservation_id;

        for (Reservation* each_reservation : reservation_data)
        {
            if (each_reservation->id_reservation == input_reservation_id)
            {
                // Confirm the reservation
                each_reservation->confirmerReservation(passager_data, billet_data, calendrier_data);
                cout << "Reservation confirmee avec succes.\n";
                reservation_data.clear();
                return;
            }
        }
        cout << "Erreur: Reservation non trouvee.\n";
    }
    else if (choix == 2) // Cancel reservation
    {
        cout << "Entrez l'ID de reservation a annuler : ";
        string input_reservation_id;
        cin >> input_reservation_id;

        for (Reservation* each_reservation : reservation_data)
        {
            if (each_reservation->id_reservation == input_reservation_id)
            {
                // Confirm the reservation
                each_reservation->annulerReservation(passager_data, billet_data, calendrier_data,false);
                cout << "Reservation annulee avec succes.\n";
                reservation_data.clear();
                return;
            }
        }
        cout << "Erreur: Reservation non trouvee.\n";
    }
    else if (choix == 3) // Quit
    {
        cout << "Retour au menu precedent.\n";
        return;
    }
}




void menu_voir_calendrier(vector<Reservation*>& reservation_data,
                          vector<Billet*>& billet_data,
                          vector<Passager*>& passager_data,
                          Passager* a_passager,
                          Calendrier* calendrier_data)
{
    string billet_class;

    // Show the calendar
    calendrier_data->afficher_calendrier();// limited to available dates only, remove train id section

    // Prompt the user to confirm if they want to continue
    char choice;
    while (true)
    {
        cout << "Voulez-vous continuer? (o/n): ";
        cin >> choice;

        if (choice != 'o' && choice != 'O' && choice != 'n' && choice != 'N')
        {
            cout << "Erreur: Veuillez entrer 'o' pour continuer ou 'n' pour annuler." << endl;
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
        else
        {
            break;
        }
    }

    if (choice == 'n' || choice == 'N')
    {
        cout << "Processus annule par l'utilisateur." << endl;
        return;
    }

    // Ask for a date
    string selected_date = calendrier_data->demander_date();
    if (selected_date.empty())
    {
        cout << "Erreur: Aucune date selectionnee ou entree invalide." << endl;
        return;
    }

    Train* selected_train = calendrier_data->search_trains(selected_date);//modify afficher_trains_par_date function to search_trains(selected_date) include departure and destination
    if (!selected_train)
    {
        cout << "Erreur: Aucun train disponible pour option selectionnee." << endl;
        return;
    }

    // Option for a new passenger or existing passenger
    if (a_passager == nullptr)   // New passenger case
    {
        string input_nom, input_prenom;

        cout << "=== Creation d'un nouveau passager ===" << endl;
        cout << "Entrez le nom du passager: ";
        cin >> input_nom;
        if (!cin || input_nom.empty())
        {
            cout << "Erreur: Nom invalide." << endl;
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            return;
        }

        cout << "Entrez le prenom du passager: ";
        cin >> input_prenom;
        if (!cin || input_prenom.empty())
        {
            cout << "Erreur: Prenom invalide." << endl;
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            return;
        }

        billet_class = array_type_classe[menu_billet_class(array_type_classe, selected_train)];
        string new_psg_id = generate_id(passager_prefix, storage_passagerID);
        string new_billet_id = generate_id(billet_prefix, storage_billetID);
        string new_reservation_id = generate_id(reservation_prefix, storage_reservationID);

        Passager* new_passager = new Passager(input_nom, input_prenom, new_psg_id);
        Billet* new_billet = new Billet(new_billet_id, billet_class, selected_train, selected_date);
        Reservation* new_reservation = new Reservation(new_reservation_id, new_passager, new_billet);

        // Add to respective data vectors
        passager_data.push_back(new_passager);
        cout << "case new passager : adding new passager succeeded." << endl;
        //billet_data.push_back(new_billet); //not yet till it's confirmed
        reservation_data.push_back(new_reservation);
        cout << "Case new passager : adding new reservation succeeded." << endl;
        menu_reservation(reservation_data, billet_data, passager_data, calendrier_data, new_reservation);
    }
    else     // Existing passenger case
    {
        billet_class = array_type_classe[menu_billet_class(array_type_classe, selected_train)];
        string new_billet_id = generate_id(billet_prefix, storage_billetID);
        string new_reservation_id = generate_id(reservation_prefix, storage_reservationID);

        Billet* new_billet = new Billet(new_billet_id, billet_class, selected_train, selected_date);
        Reservation* new_reservation = new Reservation(new_reservation_id, a_passager, new_billet);

        // Add to respective data vectors
        //billet_data.push_back(new_billet);
        reservation_data.push_back(new_reservation);
        cout << "Case given passager : adding new reservation succeeded." << endl;
        menu_reservation(reservation_data, billet_data, passager_data, calendrier_data, new_reservation);
    }
}



Passager* menu_voir_passagers(vector<Passager*> passager_data) {
    int choix = -1;

    while (true) {
        cout << "=== Menu Voir Passagers ===" << endl;
        cout << "+-------------------------------------------------------------+" << endl;
        cout << "| No. | ID Passager   | Nom               | Prenom            |" << endl;
        cout << "+-------------------------------------------------------------+" << endl;

        if (passager_data.empty()) {
            cout << "| Aucun passager disponible.                                 |" << endl;
            cout << "+-------------------------------------------------------------+" << endl;
            cout << "1. Retourner" << endl;
            cout << "Veuillez entrer votre choix: ";
            cin >> choix;
            if (choix == 1) return nullptr;
        } else {
            for (size_t i = 0; i < passager_data.size(); i++) {
                cout << "| " << setw(3) << i + 1 << " | "
                     << setw(13) << passager_data[i]->get_id_passager() << " | "
                     << setw(18) << passager_data[i]->get_nom() << " | "
                     << setw(18) << passager_data[i]->get_prenom() << " |" << endl;
            }
            cout << "+-------------------------------------------------------------+" << endl;
            cout << passager_data.size() + 1 << ". Retourner\n\n" << endl ;
        }

        cout << "Veuillez entrer votre choix (1-" << passager_data.size() + 1 << "): ";
        cin >> choix;

        if (cin.fail() || choix < 1 || choix > static_cast<int>(passager_data.size() + 1)) {
            cout << "Erreur: Veuillez entrer un nombre valide." << endl;
            cin.clear();
            cin.ignore(1000, '\n');
        } else if (choix == static_cast<int>(passager_data.size() + 1)) {
            return nullptr; // Return to the previous menu
        } else {
            return passager_data[choix - 1];
        }
    }
}




int menu_passager(Passager* a_passager)
{
    vector<string> options =
    {
        "Afficher les Reservations",
        "Afficher l'Historique des Reservations",
        "Ajouter une Reservation",
        "Retourner"
    };

    int choix = -1;
    while (true)
    {
        cout << "=== Menu Passager ===" << endl;
        a_passager->afficherInfo();

        for (size_t i = 0; i < options.size(); i++)
        {
            cout << i + 1 << ". " << options[i] << endl;
        }
        cout << "Veuillez entrer votre choix (1-" << options.size() << "): ";

        cin >> choix;

        if (cin.fail() || choix < 1 || choix > static_cast<int>(options.size()))
        {
            cout << "Erreur: Veuillez entrer un nombre valide." << endl;
            cin.clear();
            cin.ignore(1000, '\n');
        }
        else
        {
            return choix;
        }
    }
}

void annuler_confirme_billet(Passager* selected_passager,
                             Billet* selected_billet,
                             vector<Archives*>& archives_data)
{
    if (!selected_passager || !selected_billet)
    {
        cerr << "[ERREUR] Passager ou billet invalide pour annulation." << endl;
        return;
    }

    // Ensure reservations are retrieved by reference
    vector<Billet*>& reservations = selected_passager->get_PSG_reservation();
    auto it = find(reservations.begin(), reservations.end(), selected_billet);

    if (it != reservations.end())
    {
        reservations.erase(it);
        cout << "Billet ID: " << selected_billet->get_id_billet() << " supprime des reservations du passager." << endl;
    }
    else
    {
        cerr << "[ERREUR] Billet non trouve dans les reservations du passager." << endl;
        return;
    }

    string passager_id = selected_passager->get_id_passager();
    Archives* target_archive = nullptr;

    // Find or create archive for this passager
    for (auto& each_archive : archives_data)
    {
        if (each_archive->get_id_passager() == passager_id)
        {
            target_archive = each_archive;
            break;
        }
    }

    if (!target_archive)
    {
        target_archive = new Archives(selected_passager->get_nom(),
                                      selected_passager->get_prenom(),
                                      selected_passager->get_id_passager());
        archives_data.push_back(target_archive);
        cout << "Nouvel archive cree pour le passager: " << selected_passager->get_nom()
             << " " << selected_passager->get_prenom() << endl;
    }

    target_archive->ajouter_historiqueReservations(selected_billet, "Annule");
    cout << "Billet ID: " << selected_billet->get_id_billet() << " ajoute aux archives." << endl;
}


void menu_afficher_reservations(Passager* selected_passager, vector<Archives*>& archives_data)
{
    if (!selected_passager)
    {
        cerr << "[ERREUR] Passager invalide." << endl;
        return;
    }

    Billet* selected_billet = selected_passager->afficherReservations();
    if (selected_billet)
    {
        int choix;
        cout << "\n1. Annuler" << endl;
        cout << "2. Retourner" << endl;

        while (true)
        {
            cout << "Veuillez entrer votre choix (1-2): ";
            cin >> choix;
            if (cin.fail() || (choix != 1 && choix != 2))
            {
                cin.clear();
                cin.ignore(1000, '\n');
                cerr << "[ERREUR] Entree invalide. Veuillez entrer 1 ou 2." << endl;
                continue;
            }

            if (choix == 1)
            {
                annuler_confirme_billet(selected_passager, selected_billet, archives_data);
                return;
            }
            else if (choix == 2)
            {
                return;
            }
        }
    }
    else
    {
        //cout << "[INFO] Aucune reservation selectionnee." << endl;
        return;
    }
}

void afficherHistoriqueArchives(Passager* selected_passager, const vector<Archives*>& archives_data)
{
    if (!selected_passager)
    {
        cerr << "[ERREUR] Passager invalide." << endl;
        return;
    }

    // Locate the archive for the selected passenger
    Archives* target_archive = nullptr;
    for (const auto& each_archive : archives_data)
    {
        if (each_archive->get_id_passager() == selected_passager->get_id_passager())
        {
            target_archive = each_archive;
            break;
        }
    }

    // If no archive exists for the passenger
    if (!target_archive)
    {
        cout << "\n+-------------------------------------------------+" << endl;
        cout << "| Aucune archive trouvée pour le passager.       |" << endl;
        cout << "+-------------------------------------------------+" << endl;
        return;
    }

    // Display the archive
    cout << "\n+-------------------------------------------------+" << endl;
    cout << "| Historique des Reservations pour Passager       |" << endl;
    cout << "+-------------------------------------------------+" << endl;
    cout << "| Nom          : " << target_archive->get_nom() << endl;
    cout << "| Prenom       : " << target_archive->get_prenom() << endl;
    cout << "| ID Passager  : " << target_archive->get_id_passager() << endl;
    cout << "+-------------------------------------------------+" << endl;

    if (target_archive->archived_billets.empty())
    {
        cout << "| Aucun billet archivé                             |" << endl;
    }
    else
    {
        cout << "| Billet ID         | Motive                      |" << endl;
        cout << "+-------------------+-----------------------------+" << endl;

        for (const auto& [billet, motive] : target_archive->archived_billets)
        {
            cout << "| " << setw(17) << left << billet->get_id_billet()
                 << "| " << setw(27) << motive << " |" << endl;
        }
    }
    cout << "+-------------------------------------------------+" << endl;
}


void system_loop(
    vector<Archives*>& archives_data,
    vector<Billet*>& billet_data,
    vector<Passager*>& passager_data,
    vector<Reservation*>& reservation_data,
    Calendrier* calendrier_data
)
{
    bool is_running = true;

    while (is_running)
    {
        generate_trainmap(stations_locs, map_width, map_height); // Generate map visualization
        int choice = menu_principal(); // Main menu

        switch (choice)
        {
        case 1: // Voir Calendrier
        {
            menu_voir_calendrier(reservation_data, billet_data, passager_data, nullptr, calendrier_data);
            break; // Ensure we return to the main loop after handling
        }

        case 2: // Voir Passagers
        {
            bool is_viewing_passengers = true;
            while (is_viewing_passengers)
            {
                Passager* selected_passager = menu_voir_passagers(passager_data);
                if (selected_passager)
                {
                    bool is_in_passenger_menu = true;
                    while (is_in_passenger_menu)
                    {
                        int passager_choice = menu_passager(selected_passager);
                        switch (passager_choice)
                        {
                        case 1: // Afficher les Reservations
                            menu_afficher_reservations(selected_passager,archives_data);
                            break;

                        case 2: // Afficher Historique des Reservations
                            afficherHistoriqueArchives(selected_passager, archives_data);
                            break;

                        case 3: // Ajouter une Reservation
                            menu_voir_calendrier(reservation_data, billet_data, passager_data, selected_passager, calendrier_data);
                            break;

                        case 4: // Retourner
                            is_in_passenger_menu = false;
                            break;

                        default:
                            cout << "Erreur: Choix invalide." << endl;
                            break;
                        }
                    }
                }
                else
                {
                    is_viewing_passengers = false; // Exit if no passenger is selected
                }
            }
            break;
        }

        case 3: // Gerer les Reservations
        {
            cout << "=== Menu Gerer les Reservations ===" << endl;
            if (!reservation_data.empty())
            {
                for (Reservation* each_reservation : reservation_data)
                {
                    each_reservation->afficherDetailsReservation();
                    menu_reservation(reservation_data, billet_data, passager_data, calendrier_data, nullptr);
                }
            }
            else
            {
                cout << "Aucune reservation disponible." << endl;
            }
            break;
        }

        case 4: // Quitter
        {
            cout << "Exiting the system. Goodbye!" << endl;
            is_running = false;
            break;
        }

        default:
        {
            cout << "Erreur: Choix invalide." << endl;
            break;
        }
        }
    }
}

