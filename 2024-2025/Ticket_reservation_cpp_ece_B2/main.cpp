#include "header.h"



int main(void)
{
    srand(time(NULL));



    // Initialize stations
    initialize_stations(stations, stations_locs);

    // Generate train map
    //cout << "Generated Train Map:\n";


    //init data
    //vector<Train*> train_data;// redundant , will be removed
    vector<Billet*> billet_data;
    vector<Passager*> passager_data;
    vector<Reservation*> reservation_data;
    vector<Archives*> archives_data;//do remember for each cancellation of reservation, will be registered here.
    Calendrier* calendrier_data = new Calendrier(); // replace vector<Train*> train_data


    //extract data
    extract_data_file(stations,billet_data, passager_data,archives_data,calendrier_data);
    //archives : passager data will be replicated during the extraction of passager data file if not yet exist.
    /*
    cout << "Debugging archives_data after extraction:" << endl;
    for (Archives* each_archives : archives_data)
    {
        if (each_archives)
        {
            each_archives->afficherArchives();
        }
        else
        {
            cout << "Null archive object detected in archives_data!" << endl;
        }
    }*/

    initialize_train_vector(/*train_data,*/calendrier_data);
    system_loop(/*train_data,*/archives_data,billet_data,passager_data,reservation_data,calendrier_data);

    //save data
    save_data_files(archives_data, billet_data, passager_data,calendrier_data);


    return 0;
}
