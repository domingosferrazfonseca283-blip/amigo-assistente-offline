cmake_minimum_required(VERSION 3.22.1)
project(noemia_runtime)

add_library(noemia_runtime SHARED
        noemia_runtime.cpp
        noemia_runtime_core.cpp)

target_compile_features(noemia_runtime PRIVATE cxx_std_17)
target_include_directories(noemia_runtime PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
