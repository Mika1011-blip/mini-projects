cmake_minimum_required(VERSION 3.23)
project(projet_cpp)

set(CMAKE_CXX_STANDARD 14)

include_directories(.)

add_executable(projet_cpp
        billet_management_file.txt
        functions.cpp
        header.h
        main.cpp
        train_management_file.txt
        user_management_file.txt)
