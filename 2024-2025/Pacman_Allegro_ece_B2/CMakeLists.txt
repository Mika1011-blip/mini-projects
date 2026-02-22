cmake_minimum_required(VERSION 3.23)
project(ProjetPacman C)

set(CMAKE_C_STANDARD 99)

add_executable(ProjetPacman main.c pacman.c pacman.h)

target_link_libraries(ProjetPacman -lmingw32 -lalleg44)