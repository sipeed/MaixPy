#pragma once

#include <pybind11/pybind11.h>

#include "maix_type.hpp"


namespace py = pybind11;

namespace PYBIND11_NAMESPACE
{
    namespace detail
    {
        template <>
        struct type_caster<maix::Bytes>
        {
        public:
            /**
             * This macro establishes the name 'Bytes' in
             * function signatures and declares a local variable
             * 'value' of type maix::Bytes
             */
            PYBIND11_TYPE_CASTER(maix::Bytes, const_name("maix.Bytes(bytes)"));

            /**
             * Conversion part 1 (Python->C++): convert a PyObject into a maix::Bytes
             * instance or return false upon failure. The second argument
             * indicates whether implicit conversions should be applied.
             */
            bool load(handle src, bool)
            {
                /* Extract PyObject from handle */
                PyObject *source = src.ptr();
                if (!PyBytes_Check(source))
                {
                    return false;
                }
                /* Try converting into a Python bytes value */
                PyObject *tmp = PyBytes_FromObject(source);
                if (!tmp)
                {
                    return false;
                }
                /* Now try to convert into a C++ int */
                value.data = NULL;
                value.data_len = 0;
                PyBytes_AsStringAndSize(tmp, (char **)&value.data, (Py_ssize_t *)&value.data_len);
                value.buff_len = value.data_len;
                Py_DECREF(tmp);
                /* Ensure return code was OK (to avoid out-of-range errors etc) */
                return !(value.data == NULL && !PyErr_Occurred());
            }

            /**
             * Conversion part 2 (C++ -> Python): convert an maix::Bytes instance into
             * a Python object. The second and third arguments are used to
             * indicate the return value policy and parent object (for
             * ``return_value_policy::reference_internal``) and are generally
             * ignored by implicit casters.
             */
            static handle cast(maix::Bytes *src, return_value_policy /* policy */, handle /* parent */)
            {
                handle data = PyBytes_FromStringAndSize((char *)src->data, src->data_len);
                // TODO: Is there a more efficient way(like borrow src and auto delete src when data or parent deleted)?
                delete src;
                return data;
            }
        };
    }
} // namespace PYBIND11_NAMESPACE::detail

