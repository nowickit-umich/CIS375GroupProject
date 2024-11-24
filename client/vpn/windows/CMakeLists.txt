cmake_minimum_required(VERSION 3.10)
project(windows_vpn)

# Add source files
set(SOURCES
    src/pch.cpp
    src/pch.h
    src/dllmain.cpp
    src/framework.h
    src/windows_vpn.cpp
    src/windows_vpn.h
)

# Create shared library (DLL)
add_library(windows_vpn SHARED ${SOURCES})

# Link external .lib file
target_link_libraries(windows_vpn PRIVATE rasapi32.lib)

# Copy the DLL after it is built
add_custom_command(TARGET windows_vpn POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
    "$<TARGET_FILE:windows_vpn>" "../"
)