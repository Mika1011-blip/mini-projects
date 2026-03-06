# Ticket Reservation System (ECE B2)

Console-based C++ reservation system for trains, tickets, and passengers.

## Main Files

- `main.cpp`: application entrypoint.
- `header.h`, `functions.cpp`, `global.cpp`, `wrapped_functions.cpp`: models and business logic.
- Data files:
  - `train_management_file.txt`
  - `user_management_file.txt`
  - `billet_management_file.txt`
  - `archives.txt`
- Code::Blocks project files: `system_billet_reservation.*`.
- Archived copy: `projet cpp/`.

## Features

- Passenger and reservation management.
- Ticket generation and pricing by class and distance.
- Text-file persistence for users, trains, tickets, and archives.
- Reservation cancellation tracking.

## Build and Run

### Code::Blocks

- Open `system_billet_reservation.cbp`.
- Build and run from the IDE.

### g++ (manual)

- `g++ -std=c++17 main.cpp functions.cpp global.cpp wrapped_functions.cpp -o reservation_app`
- `./reservation_app`

## Notes

- This is a learning project with manual memory ownership patterns.
- Backup data text files before destructive test scenarios.
