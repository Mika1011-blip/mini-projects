# Pacman Allegro (ECE B2)

Pacman-style game written in C using Allegro 4.

## What is in this folder

- `main.c`, `pacman.c`, `pacman.h` : gameplay logic, movement, collisions.
- `map/` : map files (`map1.txt`, `map2.txt`, `map3.txt`).
- `images/`, `font/` : game assets.
- `CMakeLists.txt` : CMake build entry.
- Code::Blocks project files (`*.cbp`, `*.depend`).

## Build

### CMake

- `cmake -S . -B build`
- `cmake --build build`

`CMakeLists.txt` links Allegro with `-lalleg44`, so Allegro 4 must be installed and discoverable.

### Code::Blocks

Open `Allegro_project.cbp` and build from IDE.

## Run

- Launch generated executable.
- Controls: arrow keys to move, `ESC` to quit.

## Notes

- Project includes committed build output (`bin/`, `obj/`, `cmake-build-debug/`).
- Relative asset paths are expected from the project working directory.
