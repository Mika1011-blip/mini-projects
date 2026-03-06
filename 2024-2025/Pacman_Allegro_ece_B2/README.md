# Pacman Allegro (ECE B2)

Pacman-style game written in C with Allegro 4.

## Main Files

- `main.c`, `pacman.c`, `pacman.h`: game loop, movement, collision logic.
- `map/`: map definitions (`map1.txt`, `map2.txt`, `map3.txt`).
- `images/`, `font/`: game assets.
- `CMakeLists.txt`: CMake build entry.
- `Allegro_project.cbp`: Code::Blocks project file.

## Build

### CMake

- `cmake -S . -B build`
- `cmake --build build`

`CMakeLists.txt` links Allegro as `-lalleg44`, so Allegro 4 must be installed and visible in your toolchain.

### Code::Blocks

- Open `Allegro_project.cbp`.
- Build and run from the IDE.

## Run

- Start executable from project root (assets are loaded with relative paths).
- Controls: arrow keys to move, `ESC` to quit.

## Notes

- This folder includes local build outputs (`bin/`, `obj/`, `cmake-build-debug/`).
- Keep assets and maps in place or update load paths in code.
