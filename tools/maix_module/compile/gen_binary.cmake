
# set(CMAKE_C_LINK_EXECUTABLE "<CMAKE_C_COMPILER> <FLAGS> <CMAKE_C_LINK_FLAGS> <OBJECTS> -o <TARGET>.elf <LINK_LIBRARIES>")
# set(CMAKE_CXX_LINK_EXECUTABLE "<CMAKE_CXX_COMPILER> <FLAGS> <CMAKE_CXX_LINK_FLAGS> <OBJECTS> -o <TARGET>.elf <LINK_LIBRARIES>")

# add_custom_command(TARGET ${PROJECT_ID} POST_BUILD
#     COMMAND ${CMAKE_OBJCOPY} --output-format=binary ${CMAKE_BINARY_DIR}/${PROJECT_ID}.elf ${CMAKE_BINARY_DIR}/${PROJECT_ID}.bin
#     DEPENDS ${PROJECT_ID}
#     COMMENT "-- Generating binary file ...")

# variable #{g_dynamic_libs} have dependency dynamic libs and compiled dynamic libs(register component and assigned DYNAMIC or SHARED flag)

# remove endswith libpython*.so items and libmaix.so from g_dynamic_libs
set(final_dynamic_libs)
set(except_libs "libpython.*\\.so$"
                "libmaix\\.so$"
    )
foreach(item ${g_dynamic_libs})
    set(is_except FALSE)
    foreach(except ${except_libs})
        if(${item} MATCHES ${except})
            set(is_except TRUE)
            break()
        endif()
    endforeach()
    if(NOT is_except)
        list(APPEND final_dynamic_libs ${item})
    endif()
endforeach()

file(STRINGS "${PROJECT_PATH}/module_name.txt" ALL_LINES)
list(GET ALL_LINES 0 MODULE_NAME)

if(final_dynamic_libs)
    set(copy_dynamic_libs_cmd COMMAND mkdir -p ${PROJECT_BINARY_DIR}/dl_lib && cp ${final_dynamic_libs} ${PROJECT_BINARY_DIR}/dl_lib)
    set(copy_dynamic_libs_cmd2 COMMAND mkdir -p ${PROJECT_PATH}/${MODULE_NAME}/dl_lib && cp -r ${PROJECT_BINARY_DIR}/dl_lib/* ${PROJECT_PATH}/${MODULE_NAME}/dl_lib)
else()
    set(copy_dynamic_libs_cmd)
    set(copy_dynamic_libs_cmd2)
endif()

add_custom_command(TARGET ${PROJECT_ID} POST_BUILD
    # COMMAND mkdir -p ${PROJECT_DIST_DIR}
    ${copy_dynamic_libs_cmd}
    ${copy_dynamic_libs_cmd2}
    COMMAND python ${PROJECT_PATH}/compile/copy_so.py ${PROJECT_BINARY_DIR}/maix/libmaix.so ${PROJECT_PATH}
    DEPENDS ${PROJECT_ID}
    COMMENT "-- copy binary files to dist dir ...")

