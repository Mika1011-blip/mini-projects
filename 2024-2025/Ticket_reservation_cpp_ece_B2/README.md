# Ticket Reservation System (ECE B2)

Console-based C++ reservation system for trains, tickets, and passengers.

## What is in this folder

- `main.cpp` : app entrypoint.
- `header.h`, `functions.cpp`, `global.cpp`, `wrapped_functions.cpp` : domain models and business logic.
- Data files:
  - `train_management_file.txt`
  - `user_management_file.txt`
  - `billet_management_file.txt`
  - `archives.txt`
- Code::Blocks project files (`system_billet_reservation.*`).
- Archived subcopy: `projet cpp/`.

## Features

- Passenger and reservation management.
- Ticket generation and pricing by class/distance.
- In-memory schedule/calendar + persistence to text files.
- Reservation cancellation tracking in archives.

## Build / Run

### Code::Blocks

- Open `system_billet_reservation.cbp`
- Build and run from IDE.

### g++ (manual)

- `g++ -std=c++17 main.cpp functions.cpp global.cpp wrapped_functions.cpp -o reservation_app`
- `./reservation_app`

## Notes

- This is a learning project with raw pointers and manual ownership.
- Keep backup copies of data text files before large tests.
