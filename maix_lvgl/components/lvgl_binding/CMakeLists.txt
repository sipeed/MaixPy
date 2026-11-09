############### Add include ###################
list(APPEND ADD_INCLUDE "${PROJECT_PATH}/binding"
                        "${PROJECT_PATH}/runtime")
list(APPEND ADD_PRIVATE_INCLUDE "")
###############################################

############ Add source files #################
set(binding_dir "${PROJECT_PATH}/binding")
file(MAKE_DIRECTORY "${binding_dir}")
set(binding_src "${binding_dir}/lvgl_python.c")
set_property(SOURCE "${binding_src}" PROPERTY GENERATED 1)
list(APPEND ADD_SRCS "${PROJECT_PATH}/runtime/lvpy_runtime.c"
                     "${binding_src}")
###############################################

###### Add required/dependent components ######
list(APPEND ADD_REQUIREMENTS lvgl python3)
###############################################

#### Add compile option for this component ####
list(APPEND ADD_DEFINITIONS -DLV_CPYTHON_BUILD
                            -DLV_CONF_INCLUDE_SIMPLE)
###############################################

###### Generate binding before compiling ######
add_custom_target(generate_lvgl_binding ALL
    COMMAND ${python} -u "${PROJECT_PATH}/tools/regenerate_binding.py" --sdk-path "${SDK_PATH}"
    COMMENT "Generating LVGL binding from MaixCDK's LVGL sources"
    VERBATIM)
###############################################

register_component(DYNAMIC)
add_dependencies(lvgl_binding generate_lvgl_binding)
