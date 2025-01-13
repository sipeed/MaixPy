############### Add include ###################
list(APPEND ADD_INCLUDE "include"
    )
list(APPEND ADD_PRIVATE_INCLUDE "")
###############################################

############ Add source files #################
# list(APPEND ADD_SRCS  "src/main.c"
#                       "src/test.c"
#     )
# append_srcs_dir(ADD_SRCS "src")       # append source file in src dir to var ADD_SRCS
# list(REMOVE_ITEM COMPONENT_SRCS "src/test2.c")
# FILE(GLOB_RECURSE EXTRA_SRC  "src/*.c")
# FILE(GLOB EXTRA_SRC  "src/*.c")
# list(APPEND ADD_SRCS  ${EXTRA_SRC})
# aux_source_directory(src ADD_SRCS)  # collect all source file in src dir, will set var ADD_SRCS
append_srcs_dir(ADD_SRCS "src")     # append source file in src dir to var ADD_SRCS
# list(REMOVE_ITEM COMPONENT_SRCS "src/test.c")
# set(ADD_ASM_SRCS "src/asm.S")
# list(APPEND ADD_SRCS ${ADD_ASM_SRCS})
# SET_PROPERTY(SOURCE ${ADD_ASM_SRCS} PROPERTY LANGUAGE C) # set .S  ASM file as C language
# SET_SOURCE_FILES_PROPERTIES(${ADD_ASM_SRCS} PROPERTIES COMPILE_FLAGS "-x assembler-with-cpp -D BBBBB")
###############################################

###### Add required/dependent components ######
# list(APPEND ADD_REQUIREMENTS pybind11 python3 basic nn peripheral vision comm network voice vision_extra
#                              ext_dev ext_dev_mlx90640 ext_dev_tof100)
###############################################

###### Add link search path for requirements/libs ######
# list(APPEND ADD_LINK_SEARCH_PATH "${CONFIG_TOOLCHAIN_PATH}/lib")
# list(APPEND ADD_REQUIREMENTS pthread m)  # add system libs, pthread and math lib for example here
# set (OpenCV_DIR opencv/lib/cmake/opencv4)
# find_package(OpenCV REQUIRED)
###############################################

############ Add static libs ##################
# list(APPEND ADD_STATIC_LIB "lib/libtest.a")
###############################################

#### Add compile option for this component ####
#### Just for this component, won't affect other 
#### modules, including component that depend 
#### on this component
# list(APPEND ADD_DEFINITIONS_PRIVATE -DAAAAA=1)

#### Add compile option for this component
#### and components depend on this component
# list(APPEND ADD_DEFINITIONS -DAAAAA222=1
#                             -DAAAAA333=1)
###############################################

############ Add static libs ##################
#### Update parent's variables like CMAKE_C_LINK_FLAGS
# set(CMAKE_C_LINK_FLAGS "${CMAKE_C_LINK_FLAGS} -Wl,--start-group libmaix/libtest.a -ltest2 -Wl,--end-group" PARENT_SCOPE)
###############################################

######### Add files need to download #########
# list(APPEND ADD_FILE_DOWNLOADS "{
# 'url': 'https://*****/abcde.tar.xz',
# 'urls': [],  # backup urls, if url failed, will try urls
# 'sites': [], # download site, user can manually download file and put it into dl_path
# 'sha256sum': '',
# 'filename': 'abcde.tar.xz',
# 'path': 'toolchains/xxxxx',
# 'check_files': []
# }"
# )
#
# then extracted file in ${DL_EXTRACTED_PATH}/toolchains/xxxxx,
# you can directly use then, for example use it in add_custom_command
##############################################

set(maixpy_wrapper_src "${CMAKE_BINARY_DIR}/maixpy_wrapper.cpp")
list(APPEND ADD_SRCS "${maixpy_wrapper_src}")
set_property(SOURCE ${maixpy_wrapper_src} PROPERTY GENERATED 1)
set(cmake_global_vars_json ${CMAKE_BINARY_DIR}/config/cmake_global_vars.json)
# if exists maixpy_wrapper_src then remove it to ensure it will be generated every build time, cause it's not easy to detect all header dependency
if(EXISTS ${maixpy_wrapper_src})
    file(REMOVE ${maixpy_wrapper_src})
endif()
add_custom_command(OUTPUT ${maixpy_wrapper_src}
    COMMAND ${python} -u ${CMAKE_CURRENT_SOURCE_DIR}/gen_api_cpp.py -o ${maixpy_wrapper_src} --sdk_path ${SDK_PATH}
    COMMENT "Generating maixpy_wrapper.cpp"
    VERBATIM
    )

# list(APPEND ADD_DEFINITIONS -Wl,-rpath=$ORIGIN/dl_lib)
# FIXME: $ character can not correctly convert to flag \$ORIGIN when build
# so we change it when compile end in gen_binary.cmake

# register component, DYNAMIC o NATIVE_COMMAND "${flags}")RED flags will make component compiled to dynamic(shared) lib
register_component(DYNAMIC)

