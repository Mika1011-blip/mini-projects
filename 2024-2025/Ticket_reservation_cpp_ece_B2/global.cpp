#include "header.h"

// Map settings
const int map_height = 25;
const int map_width = 100;

// Prefixes (already declared in header.h as extern)
const string train_prefix = "TRN";
const string passager_prefix = "PSG";
const string billet_prefix = "BLT";
const string reservation_prefix = "RSV";

// Class types
const vector<string> array_type_classe = {"premier", "deuxieme"};

// Stations and ID storage
const vector<vector<int>> stations_locs = {
    {92, 5}, {80, 21}, {10, 6}, {36, 3}, {41, 20},
};
vector<string> storage_trainID;
vector<string> storage_passagerID;
vector<string> storage_billetID;
vector<string> storage_reservationID;

vector<str_stations> stations;
