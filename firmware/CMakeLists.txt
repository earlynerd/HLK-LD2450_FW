cmake_minimum_required(VERSION 3.16)
project(ld2450_firmware LANGUAGES C)

# Host validation only. Actual BR23 compilation uses tools/build_br23.py.
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
add_library(radar_wire STATIC src/radar_wire.c)
target_include_directories(radar_wire PUBLIC include)

find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
set(LD2450_RADAR_CONFIG "${CMAKE_CURRENT_SOURCE_DIR}/config/radar_baseline_mode2.json"
    CACHE FILEPATH "Radar experiment JSON profile")
get_filename_component(LD2450_RADAR_CONFIG "${LD2450_RADAR_CONFIG}" ABSOLUTE)
set(RADAR_GENERATED "${CMAKE_CURRENT_BINARY_DIR}/generated")
add_custom_command(
  OUTPUT "${RADAR_GENERATED}/radar_config_generated.c" "${RADAR_GENERATED}/radar_config_generated.h"
  COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/generate_radar_config.py"
          --config "${LD2450_RADAR_CONFIG}" --out "${RADAR_GENERATED}"
  DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tools/generate_radar_config.py" "${LD2450_RADAR_CONFIG}"
          "${CMAKE_CURRENT_SOURCE_DIR}/../output/radar_init/manifest.json"
          "${CMAKE_CURRENT_SOURCE_DIR}/../oncstzcza54pd.ufw"
          "${CMAKE_CURRENT_SOURCE_DIR}/../5o09fdkye1jo8.ufw"
          "${CMAKE_CURRENT_SOURCE_DIR}/../output/ufw_analysis/oncstzcza54pd/flash_images/flash.bin/files/app.bin"
          "${CMAKE_CURRENT_SOURCE_DIR}/../output/ufw_analysis/5o09fdkye1jo8/flash_images/flash.bin/files/app.bin"
  VERBATIM)
add_library(radar_init STATIC src/radar_init.c "${RADAR_GENERATED}/radar_config_generated.c")
target_include_directories(radar_init PUBLIC include PRIVATE "${RADAR_GENERATED}")

include(CTest)
if(BUILD_TESTING)
  add_library(br23_host_model STATIC target/br23/peripherals.c src/app.c tests/mock_sdk.c)
  target_compile_definitions(br23_host_model PRIVATE LD2450_HOST_TEST)
  target_include_directories(br23_host_model PUBLIC include tests PRIVATE target/br23)
  target_link_libraries(br23_host_model PUBLIC radar_init)
  add_executable(test_radar_wire tests/test_radar_wire.c)
  target_link_libraries(test_radar_wire PRIVATE radar_wire)
  add_executable(test_peripherals tests/test_peripherals.c)
  target_include_directories(test_peripherals PRIVATE target/br23)
  target_compile_definitions(test_peripherals PRIVATE LD2450_HOST_TEST)
  target_link_libraries(test_peripherals PRIVATE br23_host_model)
  add_executable(test_radar_init tests/test_radar_init.c)
  target_link_libraries(test_radar_init PRIVATE radar_init)
  add_test(NAME captured_records COMMAND test_radar_wire "${CMAKE_CURRENT_SOURCE_DIR}/tests/fixtures")
  add_test(NAME br23_peripherals COMMAND test_peripherals)
  add_test(NAME radar_init_sequence COMMAND test_radar_init)
  add_executable(test_uart_update tests/test_uart_update.c src/uart_update_protocol.c)
  target_include_directories(test_uart_update PRIVATE include)
  add_test(NAME uart_update_protocol COMMAND test_uart_update)
  add_executable(test_uart_loader tests/test_uart_loader.c src/uart_update_protocol.c)
  target_compile_definitions(test_uart_loader PRIVATE LD2450_LOADER_HOST_TEST)
  target_include_directories(test_uart_loader PRIVATE include tests)
  add_test(NAME uart_loader_adapter COMMAND test_uart_loader)
  foreach(target radar_wire radar_init br23_host_model test_radar_wire test_peripherals test_radar_init test_uart_update test_uart_loader)
    if(MSVC)
      target_compile_options(${target} PRIVATE /W4 /WX)
    else()
      target_compile_options(${target} PRIVATE -Wall -Wextra -Werror)
    endif()
  endforeach()
endif()
