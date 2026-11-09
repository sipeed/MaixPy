#include "lvpy_runtime.h"
#include "lvgl/src/lvgl_private.h"
#include <stdint.h>

PyObject *PyLvReferenceError = NULL;
PyObject *mp_lv_global_user_data = NULL;
PyObject *lvpy_nesting_obj = NULL;

PyTypeObject py_C_Pointer_type;
PyTypeObject py_lv_base_struct_type;
PyTypeObject py_blob_type;

static PyThread_type_lock lvgl_lock = NULL;
static long lvgl_lock_owner = -1;
static int lvgl_lock_depth = 0;
static int lvpy_nesting_count = 0;
static int lvpy_lock_save_key = -1;

static void lvpy_drain_pending_releases_if_idle(void);
static void lvpy_unlock_nodrain(void);
static void lvpy_defer_release(PyObject *obj);

typedef struct {
    PyTypeObject *type;
    size_t size;
} lv_struct_size_entry;

static lv_struct_size_entry *struct_size_entries = NULL;
static size_t struct_size_entry_count = 0;
static size_t struct_size_entry_cap = 0;

void lvpy_lock(void)
{
    if (!lvgl_lock) {
        return;
    }
    long tid = PyThread_get_thread_ident();
    if (lvgl_lock_depth > 0 && lvgl_lock_owner == tid) {
        lvgl_lock_depth++;
        return;
    }
    PyThread_acquire_lock(lvgl_lock, WAIT_LOCK);
    lvgl_lock_owner = tid;
    lvgl_lock_depth = 1;
}

static void lvpy_unlock_nodrain(void)
{
    if (!lvgl_lock || lvgl_lock_depth == 0) {
        return;
    }
    long tid = PyThread_get_thread_ident();
    if (lvgl_lock_owner != tid) {
        return;
    }
    lvgl_lock_depth--;
    if (lvgl_lock_depth == 0) {
        lvgl_lock_owner = -1;
        PyThread_release_lock(lvgl_lock);
    }
}

/* Every generated wrapper unlocks after its LVGL call, with the GIL held.
 * That is the safe moment to let go of callback dicts whose registrations
 * ended inside the call (see lvpy_release_callback_user_data). */
void lvpy_unlock(void)
{
    lvpy_unlock_nodrain();
    lvpy_drain_pending_releases_if_idle();
}

void lvpy_release_lock_for_python(void)
{
    long tid = PyThread_get_thread_ident();
    if (lvgl_lock_owner != tid || lvgl_lock_depth == 0) {
        if (lvpy_lock_save_key >= 0) {
            PyThread_set_key_value(lvpy_lock_save_key, (void *)(intptr_t)0);
        }
        return;
    }
    if (lvpy_lock_save_key >= 0) {
        PyThread_set_key_value(lvpy_lock_save_key, (void *)(intptr_t)lvgl_lock_depth);
    }
    while (lvgl_lock_depth > 0) {
        lvpy_unlock_nodrain();
    }
}

void lvpy_reacquire_lock_after_python(void)
{
    if (lvpy_lock_save_key < 0) {
        return;
    }
    int saved = (int)(intptr_t)PyThread_get_key_value(lvpy_lock_save_key);
    for (int i = 0; i < saved; i++) {
        lvpy_lock();
    }
    PyThread_set_key_value(lvpy_lock_save_key, (void *)(intptr_t)0);
}

void lvpy_nesting_inc(void)
{
    lvpy_nesting_count++;
    if (lvpy_nesting_obj) {
        PyObject *val = PyLong_FromLong(lvpy_nesting_count);
        if (val) {
            PyObject_SetAttrString(lvpy_nesting_obj, "value", val);
            Py_DECREF(val);
        } else {
            PyErr_Clear();
        }
    }
}

void lvpy_nesting_dec(void)
{
    if (lvpy_nesting_count > 0) {
        lvpy_nesting_count--;
    }
    if (lvpy_nesting_obj) {
        PyObject *val = PyLong_FromLong(lvpy_nesting_count);
        if (val) {
            PyObject_SetAttrString(lvpy_nesting_obj, "value", val);
            Py_DECREF(val);
        } else {
            PyErr_Clear();
        }
    }
}

void lv_struct_register_size(PyTypeObject *type, size_t size)
{
    if (!type || size == 0) return;
    for (size_t i = 0; i < struct_size_entry_count; i++) {
        if (struct_size_entries[i].type == type) {
            struct_size_entries[i].size = size;
            return;
        }
    }
    if (struct_size_entry_count >= struct_size_entry_cap) {
        size_t new_cap = struct_size_entry_cap ? struct_size_entry_cap * 2 : 32;
        lv_struct_size_entry *grown = realloc(struct_size_entries, new_cap * sizeof(lv_struct_size_entry));
        if (!grown) return;
        struct_size_entries = grown;
        struct_size_entry_cap = new_cap;
    }
    struct_size_entries[struct_size_entry_count].type = type;
    struct_size_entries[struct_size_entry_count].size = size;
    struct_size_entry_count++;
}

size_t lv_struct_get_size(PyTypeObject *type)
{
    if (!type) return 0;
    for (size_t i = 0; i < struct_size_entry_count; i++) {
        if (struct_size_entries[i].type == type) {
            return struct_size_entries[i].size;
        }
    }
    return 0;
}

void lv_struct_expose_size(PyTypeObject *type)
{
    PyObject *size_obj;

    if (!type) {
        return;
    }
    size_t size = lv_struct_get_size(type);
    if (size == 0) {
        return;
    }
    if (PyType_Ready(type) < 0) {
        PyErr_Clear();
        return;
    }
    size_obj = PyLong_FromSize_t(size);
    if (!size_obj) {
        PyErr_Clear();
        return;
    }
    if (type->tp_dict == NULL) {
        type->tp_dict = PyDict_New();
        if (type->tp_dict == NULL) {
            Py_DECREF(size_obj);
            PyErr_Clear();
            return;
        }
    }
    if (PyDict_SetItemString(type->tp_dict, "__SIZE__", size_obj) < 0) {
        PyErr_Clear();
    }
    Py_DECREF(size_obj);
}

static PyObject *py_nesting_get_value(PyObject *self, void *closure)
{
    (void)self;
    (void)closure;
    return PyLong_FromLong(lvpy_nesting_count);
}

static int py_nesting_set_value(PyObject *self, PyObject *value, void *closure)
{
    (void)self;
    (void)closure;
    if (!value) {
        PyErr_SetString(PyExc_TypeError, "cannot delete nesting value");
        return -1;
    }
    lvpy_nesting_count = (int)PyLong_AsLong(value);
    if (PyErr_Occurred()) return -1;
    return 0;
}

static PyGetSetDef py_nesting_getset[] = {
    {"value", py_nesting_get_value, py_nesting_set_value, NULL},
    {NULL}
};

static PyTypeObject py_nesting_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "lvgl._Nesting",
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_getset = py_nesting_getset,
};

PyObject *lvpy_create_nesting_obj(void)
{
    if (PyType_Ready(&py_nesting_type) < 0) return NULL;
    return PyType_GenericNew(&py_nesting_type, NULL, NULL);
}

static PyObject *py_lv_dereference(PyObject *self, PyObject *args)
{
    py_lv_struct_t *inst = (py_lv_struct_t *)self;
    Py_ssize_t size = 0;
    if (!PyArg_ParseTuple(args, "|n", &size)) return NULL;
    if (!inst->data) {
        PyErr_SetString(PyLvReferenceError, "struct data is NULL");
        return NULL;
    }
    if (size <= 0) {
        size = (Py_ssize_t)lv_struct_get_size(Py_TYPE(self));
    }
    if (size <= 0) {
        PyErr_SetString(PyExc_ValueError, "__dereference__ requires a byte size for this object");
        return NULL;
    }
    return PyMemoryView_FromMemory((char *)inst->data, size, PyBUF_WRITE);
}

static PyObject *py_blob_cast(PyObject *self, PyObject *args)
{
    py_lv_struct_t *inst = (py_lv_struct_t *)self;
    PyObject *type_obj = NULL;
    if (!PyArg_ParseTuple(args, "|O", &type_obj)) return NULL;
    if (!type_obj) {
        return PyLong_FromVoidPtr(inst->data);
    }
    if (!PyType_Check(type_obj)) {
        PyErr_SetString(PyExc_TypeError, "cast argument must be a type");
        return NULL;
    }
    py_lv_struct_t *out = PyObject_New(py_lv_struct_t, (PyTypeObject *)type_obj);
    if (!out) return NULL;
    out->data = inst->data;
    out->owns_data = 0;
    return (PyObject *)out;
}

static PyObject *py_lv_struct_cast(PyObject *cls, PyObject *args)
{
    PyObject *type_obj = NULL;
    PyObject *ptr_obj = NULL;

    (void)cls;
    if (!PyArg_ParseTuple(args, "OO", &type_obj, &ptr_obj)) {
        return NULL;
    }
    if (!PyType_Check(type_obj)) {
        PyErr_SetString(PyExc_TypeError, "cast argument must be a type");
        return NULL;
    }
    void *ptr = mp_to_ptr(ptr_obj);
    lvpy_drain_pending_releases_if_idle();
    if (!ptr) {
        if (PyErr_Occurred()) return NULL;
        Py_RETURN_NONE;
    }
    py_lv_struct_t *out = PyObject_New(py_lv_struct_t, (PyTypeObject *)type_obj);
    if (!out) {
        return NULL;
    }
    out->data = ptr;
    out->owns_data = 0;
    return (PyObject *)out;
}

static PyObject *py_lv_cast_instance(PyObject *self, PyObject *args)
{
    PyObject *ptr_obj = NULL;

    if (!PyArg_ParseTuple(args, "O", &ptr_obj)) {
        return NULL;
    }
    void *ptr = mp_to_ptr(ptr_obj);
    lvpy_drain_pending_releases_if_idle();
    if (!ptr && PyErr_Occurred()) return NULL;
    py_lv_struct_t *s = (py_lv_struct_t *)self;
    if (s->data && s->owns_data && s->data != ptr) {
        /* The struct now views someone else's memory: let go of its own. */
        lvpy_release_struct_holder(s->data);
        free(s->data);
    }
    if (s->data != ptr) s->owns_data = 0;
    s->data = ptr;
    return Py_NewRef(self);
}

static PyMethodDef py_base_struct_methods[] = {
    {"__cast__", (PyCFunction)py_lv_struct_cast, METH_VARARGS | METH_CLASS, NULL},
    {"__cast_instance__", py_lv_cast_instance, METH_VARARGS, NULL},
    {"__dereference__", py_lv_dereference, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

/* Match MicroPython lv_struct_subscr: Struct(N) allocates N elements; s[i] views element i. */
static PyObject *py_lv_struct_subscript(PyObject *self, PyObject *key)
{
    if (!PyLong_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "struct indices must be integers");
        return NULL;
    }
    Py_ssize_t index = PyLong_AsSsize_t(key);
    if (index == -1 && PyErr_Occurred()) {
        return NULL;
    }
    if (index < 0) {
        PyErr_SetString(PyExc_IndexError, "struct index out of range");
        return NULL;
    }
    size_t element_size = lv_struct_get_size(Py_TYPE(self));
    if (element_size == 0) {
        PyErr_SetString(PyExc_TypeError, "struct has unknown size");
        return NULL;
    }
    py_lv_struct_t *inst = (py_lv_struct_t *)self;
    if (!inst->data) {
        PyErr_SetString(PyLvReferenceError, "struct data is NULL");
        return NULL;
    }
    py_lv_struct_t *out = PyObject_New(py_lv_struct_t, Py_TYPE(self));
    if (!out) {
        return NULL;
    }
    out->data = (char *)inst->data + element_size * (size_t)index;
    out->owns_data = 0;
    return (PyObject *)out;
}

static int py_lv_struct_ass_subscript(PyObject *self, PyObject *key, PyObject *value)
{
    if (!PyLong_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "struct indices must be integers");
        return -1;
    }
    Py_ssize_t index = PyLong_AsSsize_t(key);
    if (index == -1 && PyErr_Occurred()) {
        return -1;
    }
    if (index < 0) {
        PyErr_SetString(PyExc_IndexError, "struct index out of range");
        return -1;
    }
    size_t element_size = lv_struct_get_size(Py_TYPE(self));
    if (element_size == 0) {
        PyErr_SetString(PyExc_TypeError, "struct has unknown size");
        return -1;
    }
    py_lv_struct_t *inst = (py_lv_struct_t *)self;
    if (!inst->data) {
        PyErr_SetString(PyLvReferenceError, "struct data is NULL");
        return -1;
    }
    void *element_addr = (char *)inst->data + element_size * (size_t)index;
    if (value == NULL) {
        memset(element_addr, 0, element_size);
        return 0;
    }
    if (!PyObject_TypeCheck(value, Py_TYPE(self))) {
        PyErr_Format(PyExc_TypeError, "expected %s", Py_TYPE(self)->tp_name);
        return -1;
    }
    py_lv_struct_t *other = (py_lv_struct_t *)value;
    if (!other->data) {
        PyErr_SetString(PyLvReferenceError, "struct data is NULL");
        return -1;
    }
    memcpy(element_addr, other->data, element_size);
    return 0;
}

static PyMappingMethods py_lv_struct_as_mapping = {
    .mp_length = NULL,
    .mp_subscript = py_lv_struct_subscript,
    .mp_ass_subscript = py_lv_struct_ass_subscript,
};

static PyMethodDef py_blob_methods[] = {
    {"__dereference__", py_lv_dereference, METH_VARARGS, NULL},
    {"__cast__", py_blob_cast, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

bool mp_obj_is_true(PyObject *obj)
{
    return obj && obj != Py_None && PyObject_IsTrue(obj);
}

PyObject *convert_to_bool(bool b)
{
    return PyBool_FromLong(b ? 1 : 0);
}

PyObject *convert_to_str(const char *str)
{
    if (!str) Py_RETURN_NONE;
    return PyUnicode_FromString(str);
}

const char *convert_from_str(PyObject *obj)
{
    if (!obj || obj == Py_None) return NULL;
    return PyUnicode_AsUTF8(obj);
}

PyObject *mp_obj_new_int(long v) { return PyLong_FromLong(v); }
PyObject *mp_obj_new_int_from_uint(unsigned long v) { return PyLong_FromUnsignedLong(v); }
PyObject *mp_obj_new_int_from_ll(long long v) { return PyLong_FromLongLong(v); }
PyObject *mp_obj_new_int_from_ull(unsigned long long v) { return PyLong_FromUnsignedLongLong(v); }
PyObject *mp_obj_new_float_from_f(float v) { return PyFloat_FromDouble(v); }

long mp_obj_get_int(PyObject *obj) { return PyLong_AsLong(obj); }

unsigned long long mp_obj_get_ull(PyObject *obj)
{
    return (unsigned long long)PyLong_AsUnsignedLongLong(obj);
}

double mp_obj_get_float(PyObject *obj) { return PyFloat_AsDouble(obj); }

void *copy_buffer(const void *buffer, size_t size)
{
    void *copy = malloc(size);
    if (copy) memcpy(copy, buffer, size);
    return copy;
}

static void *py_array_to_ptr(PyObject *arr, size_t element_size)
{
    if (!arr || arr == Py_None) return NULL;
    if (PyUnicode_Check(arr) || PyBytes_Check(arr) || PyByteArray_Check(arr) ||
        PyObject_CheckBuffer(arr)) {
        return mp_to_ptr(arr);
    }
    if (!PySequence_Check(arr)) {
        PyErr_Format(PyExc_TypeError, "Expected sequence or buffer, got '%s'",
            Py_TYPE(arr)->tp_name);
        return NULL;
    }
    Py_ssize_t len = PySequence_Size(arr);
    if (len < 0) return NULL;
    void *buf = malloc((size_t)len * element_size);
    if (!buf) {
        PyErr_NoMemory();
        return NULL;
    }
    unsigned char *element_addr = (unsigned char *)buf;
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PySequence_GetItem(arr, i);
        if (!item) {
            free(buf);
            return NULL;
        }
        unsigned long long val = PyLong_AsUnsignedLongLong(item);
        Py_DECREF(item);
        if (PyErr_Occurred()) {
            free(buf);
            return NULL;
        }
        memcpy(element_addr, &val, element_size);
        element_addr += element_size;
    }
    return buf;
}

static PyObject *py_array_from_ptr(void *lv_arr, size_t element_size)
{
    (void)element_size;
    if (!lv_arr) Py_RETURN_NONE;
    return ptr_to_mp(lv_arr);
}

void *mp_array_to_u8ptr(PyObject *arr) { return py_array_to_ptr(arr, 1); }
void *mp_array_to_i32ptr(PyObject *arr) { return py_array_to_ptr(arr, 4); }
void *mp_array_to_u16ptr(PyObject *arr) { return py_array_to_ptr(arr, 2); }
void *mp_array_to_u32ptr(PyObject *arr) { return py_array_to_ptr(arr, 4); }

PyObject *mp_array_from_u8ptr(void *arr) { return py_array_from_ptr(arr, 1); }
PyObject *mp_array_from_u16ptr(void *arr) { return py_array_from_ptr(arr, 2); }
PyObject *mp_array_from_i32ptr(void *arr) { return py_array_from_ptr(arr, 4); }
PyObject *mp_array_from_u32ptr(void *arr) { return py_array_from_ptr(arr, 4); }

PyObject *mp_read_ptr_C_Pointer(void *field)
{
    return ptr_to_mp(field);
}

PyObject *lv_to_mp_struct(PyTypeObject *type, void *lv_struct)
{
    if (!lv_struct) Py_RETURN_NONE;
    py_lv_struct_t *self = PyObject_New(py_lv_struct_t, type);
    if (!self) return NULL;
    self->data = lv_struct;
    self->owns_data = 0;
    return (PyObject *)self;
}

PyObject *lv_to_mp_struct_own(PyTypeObject *type, void *lv_struct)
{
    if (!lv_struct) Py_RETURN_NONE;
    py_lv_struct_t *self = PyObject_New(py_lv_struct_t, type);
    if (!self) {
        free(lv_struct);
        return NULL;
    }
    self->data = lv_struct;
    self->owns_data = 1;
    return (PyObject *)self;
}

void py_lv_struct_dealloc(py_lv_struct_t *self)
{
    if (self->data && self->owns_data) {
        lvpy_release_struct_holder(self->data);
        free(self->data);
        self->data = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}

py_lv_struct_t *mp_to_lv_struct(PyObject *obj)
{
    if (!obj || obj == Py_None) return NULL;
    if (!PyObject_TypeCheck(obj, &py_lv_base_struct_type) &&
        !PyObject_TypeCheck(obj, &py_blob_type)) {
        PyErr_SetString(PyExc_TypeError, "Expected struct object");
        return NULL;
    }
    return (py_lv_struct_t *)obj;
}

static int py_lv_struct_apply_dict(py_lv_struct_t *self, PyObject *dict)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(dict, &pos, &key, &value)) {
        if (PyObject_SetAttr((PyObject *)self, key, value) < 0) {
            return -1;
        }
    }
    return 0;
}

PyObject *make_new_lv_struct(PyTypeObject *type, PyObject *args, PyObject *kwargs, size_t elem_size)
{
    (void)kwargs;
    Py_ssize_t count = 1;
    PyObject *other = NULL;
    if (!PyArg_ParseTuple(args, "|O", &other)) return NULL;
    if (other && PyLong_Check(other)) {
        count = PyLong_AsSsize_t(other);
        other = NULL;
    }
    if (elem_size == 0) {
        elem_size = lv_struct_get_size(type);
    }
    py_lv_struct_t *self = PyObject_New(py_lv_struct_t, type);
    if (!self) return NULL;
    if (other && PyObject_TypeCheck(other, type)) {
        self->data = ((py_lv_struct_t *)other)->data;
        self->owns_data = 0;
        return (PyObject *)self;
    }
    if (elem_size == 0) {
        self->data = NULL;
        self->owns_data = 0;
    } else {
        self->data = calloc((size_t)count, elem_size);
        self->owns_data = self->data ? 1 : 0;
    }
    if (other && PyDict_Check(other)) {
        if (!self->data) {
            Py_DECREF(self);
            PyErr_SetString(PyExc_TypeError, "cannot construct struct from dict without a known size");
            return NULL;
        }
        if (py_lv_struct_apply_dict(self, other) < 0) {
            Py_DECREF(self);
            return NULL;
        }
    }
    return (PyObject *)self;
}

static PyObject *py_C_Pointer_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return make_new_lv_struct(type, args, kwds, 0);
}

static void py_lv_delete_cb(lv_event_t *e);

static int lvpy_obj_has_event_cb(lv_obj_t *lv_obj, lv_event_cb_t cb)
{
    uint32_t count = lv_obj_get_event_count(lv_obj);
    for (uint32_t i = 0; i < count; i++) {
        lv_event_dsc_t *dsc = lv_obj_get_event_dsc(lv_obj, i);
        if (dsc && lv_event_dsc_get_cb(dsc) == cb) return 1;
    }
    return 0;
}

PyTypeObject *py_get_base_obj_type(void)
{
    return py_lv_obj_types[0] ? py_lv_obj_types[0]->py_type : NULL;
}

PyObject *lv_to_mp(lv_obj_t *lv_obj)
{
    if (!lv_obj) Py_RETURN_NONE;
    py_lv_obj_t *self = (py_lv_obj_t *)lv_obj->user_data;
    if (!self) {
        PyTypeObject *py_type = py_get_base_obj_type();
        py_lv_obj_type_t **iter = &py_lv_obj_types[0];
        const lv_obj_class_t *cls = lv_obj_get_class(lv_obj);
        for (; *iter; iter++) {
            if ((*iter)->lv_obj_class == cls) {
                py_type = (*iter)->py_type;
                break;
            }
        }
        self = PyObject_New(py_lv_obj_t, py_type);
        if (!self) return NULL;
        self->lv_obj = lv_obj;
        self->callbacks = NULL;
        lv_obj->user_data = self;
        /* A wrapper that was dropped and recreated must not stack a second
         * delete hook on the object; the first one is still registered. */
        if (!lvpy_obj_has_event_cb(lv_obj, py_lv_delete_cb)) {
            lv_obj_add_event_cb(lv_obj, py_lv_delete_cb, LV_EVENT_DELETE, NULL);
        }
        /* PyObject_New → refcnt 1; return transfers that new reference. */
        return (PyObject *)self;
    }
    /* Cache hit: user_data is a borrowed association. Caller needs a new ref. */
    Py_INCREF((PyObject *)self);
    return (PyObject *)self;
}

lv_obj_t *mp_to_lv(PyObject *obj)
{
    if (!obj || obj == Py_None) return NULL;
    py_lv_obj_t *self = (py_lv_obj_t *)obj;
    PyTypeObject *base = py_get_base_obj_type();
    if (base && !PyObject_TypeCheck(obj, base) &&
        !PyType_IsSubtype(Py_TYPE(obj), base)) {
        PyErr_SetString(PyExc_TypeError, "Expected LVGL object");
        return NULL;
    }
    if (!self->lv_obj) {
        PyErr_SetString(PyLvReferenceError, "Referenced object was deleted!");
        return NULL;
    }
    return self->lv_obj;
}

PyObject *mp_get_callbacks(PyObject *obj)
{
    py_lv_obj_t *self = (py_lv_obj_t *)obj;
    if (!self->callbacks) {
        self->callbacks = PyDict_New();
        if (!self->callbacks) return NULL;
    }
    return self->callbacks;
}

void lvpy_dealloc_obj(py_lv_obj_t *self)
{
    if (self->lv_obj) {
        if (lv_is_initialized()) {
            self->lv_obj->user_data = NULL;
        }
        self->lv_obj = NULL;
    }
    Py_XDECREF(self->callbacks);
    self->callbacks = NULL;
    Py_TYPE(self)->tp_free((PyObject *)self);
}

void *mp_to_ptr(PyObject *obj)
{
    if (!obj || obj == Py_None) return NULL;
    if (PyDict_Check(obj)) return (void *)obj;
    if (PyObject_TypeCheck(obj, &py_lv_base_struct_type) ||
        PyObject_TypeCheck(obj, &py_blob_type)) {
        return ((py_lv_struct_t *)obj)->data;
    }
    if (PyObject_CheckBuffer(obj)) {
        /* The pointer is only valid while the buffer is exported. Hold the
         * export in a memoryview until the outermost LVGL call returns, so
         * Python code run during the call (an event callback, say) can't
         * resize or free the memory LVGL is reading. */
        PyObject *view = PyMemoryView_FromObject(obj);
        if (!view) return NULL;
        Py_buffer *b = PyMemoryView_GET_BUFFER(view);
        if (!PyBuffer_IsContiguous(b, 'C')) {
            Py_DECREF(view);
            PyErr_Format(PyExc_BufferError, "'%s' buffer is not contiguous",
                Py_TYPE(obj)->tp_name);
            return NULL;
        }
        void *p = b->buf;
        lvpy_defer_release(view);
        return p;
    }
    if (PyUnicode_Check(obj)) {
        return (void *)PyUnicode_AsUTF8(obj);
    }
    PyErr_Format(PyExc_TypeError, "Cannot convert '%s' to pointer", Py_TYPE(obj)->tp_name);
    return NULL;
}

PyObject *ptr_to_mp(void *data)
{
    return lv_to_mp_struct(&py_blob_type, data);
}

PyObject *get_callback_dict_from_user_data(void *user_data)
{
    if (!user_data) return NULL;
    PyObject *obj = (PyObject *)user_data;
    if (PyDict_Check(obj)) return obj;
    return mp_get_callbacks(obj);
}

/* Py_IsFinalizing() is 3.13+; _Py_IsFinalizing() covers 3.10-3.12. Both
 * report whether the interpreter is inside Py_FinalizeEx(). */
#if PY_VERSION_HEX >= 0x030d0000
#define LVPY_IS_FINALIZING() Py_IsFinalizing()
#else
#define LVPY_IS_FINALIZING() _Py_IsFinalizing()
#endif

/* Registry of the per-registration callback dicts THIS runtime created.
 *
 * py_lv_delete_cb sweeps every event descriptor on a dying object --
 * including registrations made by LVGL internals or other C code, whose
 * user_data is an arbitrary C pointer. Probing such a pointer with
 * PyDict_Check() dereferences ob_type on non-PyObject memory and can
 * segfault (observed under lv_deinit(): a foreign dsc's user_data pointed
 * into an LVGL heap block). Never type-guess: a pointer is releasable iff
 * we recorded it at creation. All access happens with the GIL held
 * (mp_lv_callback runs from Python; py_lv_delete_cb takes the GIL). */
/* Each entry is one reference we own on a callback dict, on behalf of one
 * holder. An event registration's holder is NULL: lv_obj_add_event_cb and
 * friends take one reference per call and release it by dict pointer. A
 * struct's holder is the struct itself (the containing_struct that the
 * generated setters pass): every callback set on that struct shares one
 * reference, released when the struct's owner lets go of it -- the Python
 * wrapper's dealloc for a struct it owns, LVGL's ext_data free_cb for a
 * timer or a running animation. */
typedef struct {
    PyObject *dict;
    void *holder;
} lvpy_dict_entry_t;

static lvpy_dict_entry_t *lvpy_dict_registry = NULL;
static size_t lvpy_dict_registry_len = 0;
static size_t lvpy_dict_registry_cap = 0;

static void lvpy_registry_add(void *user_data, void *holder)
{
    if (!user_data) return;
    if (lvpy_dict_registry_len == lvpy_dict_registry_cap) {
        size_t cap = lvpy_dict_registry_cap ? lvpy_dict_registry_cap * 2 : 32;
        lvpy_dict_entry_t *grown = (lvpy_dict_entry_t *)realloc(
            lvpy_dict_registry, cap * sizeof(lvpy_dict_entry_t));
        if (!grown) return; /* untracked dict leaks at release time; safe */
        lvpy_dict_registry = grown;
        lvpy_dict_registry_cap = cap;
    }
    lvpy_dict_registry[lvpy_dict_registry_len].dict = (PyObject *)user_data;
    lvpy_dict_registry[lvpy_dict_registry_len].holder = holder;
    lvpy_dict_registry_len++;
}

void lvpy_register_callback_dict(void *user_data)
{
    lvpy_registry_add(user_data, NULL);
}

static void lvpy_registry_drop(size_t i)
{
    lvpy_dict_registry[i] = lvpy_dict_registry[--lvpy_dict_registry_len];
}

static int lvpy_registry_has(void *user_data, void *holder)
{
    for (size_t i = 0; i < lvpy_dict_registry_len; i++) {
        if (lvpy_dict_registry[i].dict == (PyObject *)user_data &&
            lvpy_dict_registry[i].holder == holder) return 1;
    }
    return 0;
}

/* Remove one entry for the dict: an event registration's (holder NULL) if
 * there is one, else any. Returns 1 if an entry was removed. */
static int lvpy_registry_remove(void *user_data)
{
    size_t found = lvpy_dict_registry_len;
    for (size_t i = 0; i < lvpy_dict_registry_len; i++) {
        if (lvpy_dict_registry[i].dict != (PyObject *)user_data) continue;
        if (lvpy_dict_registry[i].holder == NULL) { found = i; break; }
        if (found == lvpy_dict_registry_len) found = i;
    }
    if (found == lvpy_dict_registry_len) return 0;
    lvpy_registry_drop(found);
    return 1;
}

int lvpy_is_per_registration_callback_dict(void *user_data)
{
    if (!user_data) return 0;
    for (size_t i = 0; i < lvpy_dict_registry_len; i++) {
        if (lvpy_dict_registry[i].dict == (PyObject *)user_data) return 1;
    }
    return 0;
}

/* Dicts whose registration has ended but whose reference cannot be dropped
 * yet. LVGL sends LV_EVENT_DELETE to every descriptor in order, and the
 * runtime's own hook is the first one on the object, so a user DELETE
 * callback on the same object still reads its dict after py_lv_delete_cb
 * has run. A callback may also delete its own widget or remove its own
 * event while the trampoline holds a borrowed reference into the dict. So
 * the DECREF waits until no LVGL call and no Python callback is in flight:
 * the outermost wrapper's unlock, or a release made at top level. */
static PyObject **lvpy_pending_releases = NULL;
static size_t lvpy_pending_len = 0;
static size_t lvpy_pending_cap = 0;

static void lvpy_drain_pending_releases_if_idle(void)
{
    if (lvgl_lock_depth != 0 || lvpy_nesting_count != 0) return;
    if (lvpy_pending_len == 0) return;
    if (LVPY_IS_FINALIZING()) return;
    /* Take the batch first: a __del__ run by a DECREF may call back into
     * LVGL and reach here again. */
    PyObject **batch = lvpy_pending_releases;
    size_t count = lvpy_pending_len;
    lvpy_pending_releases = NULL;
    lvpy_pending_len = 0;
    lvpy_pending_cap = 0;
    for (size_t i = 0; i < count; i++) {
        Py_DECREF(batch[i]);
    }
    free(batch);
}

static void lvpy_defer_release(PyObject *obj)
{
    if (lvpy_pending_len == lvpy_pending_cap) {
        size_t cap = lvpy_pending_cap ? lvpy_pending_cap * 2 : 32;
        PyObject **grown = (PyObject **)realloc(lvpy_pending_releases, cap * sizeof(PyObject *));
        if (!grown) return; /* leak this one rather than crash */
        lvpy_pending_releases = grown;
        lvpy_pending_cap = cap;
    }
    lvpy_pending_releases[lvpy_pending_len++] = obj;
}

void lvpy_release_callback_user_data(void *user_data)
{
    /* Belt on top of the registry: once Py_FinalizeEx() is tearing the
     * interpreter down, skip the DECREF and leak; the OS reclaims it. */
    if (LVPY_IS_FINALIZING()) return;
    if (user_data && lvpy_registry_remove(user_data)) {
        lvpy_defer_release((PyObject *)user_data);
        lvpy_drain_pending_releases_if_idle();
    }
}

void lvpy_release_struct_holder(void *holder)
{
    if (!holder || LVPY_IS_FINALIZING()) return;
    int released = 0;
    for (size_t i = 0; i < lvpy_dict_registry_len;) {
        if (lvpy_dict_registry[i].holder == holder) {
            lvpy_defer_release(lvpy_dict_registry[i].dict);
            lvpy_registry_drop(i);
            released = 1;
        } else {
            i++;
        }
    }
    if (released) lvpy_drain_pending_releases_if_idle();
}

/* A timer created with a Python callback: lv_timer_create registered the
 * dict as an event-style entry (holder NULL) before the timer existed. Make
 * the timer its holder, and let LVGL release it on every path that frees
 * the timer. Also the hook for lv_timer_set_cb on a timer LVGL created. */
#if LV_USE_EXT_DATA
static void lvpy_timer_ext_free(void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    lvpy_release_struct_holder(data);
    PyGILState_Release(gstate);
}

static void lvpy_anim_ext_free(void *data)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    lvpy_release_struct_holder(data);
    PyGILState_Release(gstate);
}
#endif

void lvpy_timer_bind(lv_timer_t *timer)
{
#if LV_USE_EXT_DATA
    if (!timer || !timer->user_data) return;
    void *dict = timer->user_data;
    if (!lvpy_registry_has(dict, timer)) {
        size_t i;
        for (i = 0; i < lvpy_dict_registry_len; i++) {
            if (lvpy_dict_registry[i].dict == (PyObject *)dict &&
                lvpy_dict_registry[i].holder == NULL) break;
        }
        if (i == lvpy_dict_registry_len) return; /* not our dict */
        lvpy_dict_registry[i].holder = timer;
    }
    lv_timer_set_external_data(timer, timer, lvpy_timer_ext_free);
#else
    (void)timer;
#endif
}

/* lv_anim_start copied the Python-owned struct, dict pointer included, into
 * LVGL's list. The running copy takes its own reference, released by LVGL's
 * free_cb when the animation completes or is deleted; the Python struct keeps
 * its reference so the animation can be started again from it. */
void lvpy_anim_bind(lv_anim_t *anim)
{
#if LV_USE_EXT_DATA
    if (!anim) return;
    void *dict = anim->user_data;
    if (dict && lvpy_is_per_registration_callback_dict(dict)) {
        if (!lvpy_registry_has(dict, anim)) {
            Py_INCREF((PyObject *)dict);
            lvpy_registry_add(dict, anim);
        }
        lv_anim_set_external_data(anim, anim, lvpy_anim_ext_free);
    } else {
        /* Whatever ext_data the copy inherited belongs to another holder. */
        lv_anim_set_external_data(anim, NULL, NULL);
    }
#else
    (void)anim;
#endif
}

static void *lvpy_peek_event_dsc_list_cb_user_data(
    uint32_t count,
    lv_event_dsc_t *(*get_dsc)(uint32_t index, void *ctx),
    void *ctx,
    lv_event_cb_t cb,
    void *specific_user_data)
{
    for (uint32_t i = 0; i < count; i++) {
        lv_event_dsc_t *dsc = get_dsc(i, ctx);
        if (!dsc) continue;
        if (lv_event_dsc_get_cb(dsc) != cb) continue;
        void *ud = lv_event_dsc_get_user_data(dsc);
        if (specific_user_data != NULL && ud != specific_user_data) continue;
        return ud;
    }
    return NULL;
}

typedef struct {
    lv_obj_t *obj;
} lvpy_obj_peek_ctx;

static lv_event_dsc_t *lvpy_obj_peek_get_dsc(uint32_t index, void *ctx)
{
    lvpy_obj_peek_ctx *c = (lvpy_obj_peek_ctx *)ctx;
    return lv_obj_get_event_dsc(c->obj, index);
}

void *lvpy_peek_obj_event_cb_user_data(lv_obj_t *obj, lv_event_cb_t cb, void *specific_user_data)
{
    if (!obj) return NULL;
    lvpy_obj_peek_ctx ctx = {obj};
    return lvpy_peek_event_dsc_list_cb_user_data(
        lv_obj_get_event_count(obj), lvpy_obj_peek_get_dsc, &ctx, cb, specific_user_data);
}

typedef struct {
    lv_display_t *disp;
} lvpy_display_peek_ctx;

static lv_event_dsc_t *lvpy_display_peek_get_dsc(uint32_t index, void *ctx)
{
    lvpy_display_peek_ctx *c = (lvpy_display_peek_ctx *)ctx;
    return lv_display_get_event_dsc(c->disp, index);
}

void *lvpy_peek_display_event_cb_user_data(lv_display_t *disp, lv_event_cb_t cb, void *specific_user_data)
{
    if (!disp) return NULL;
    lvpy_display_peek_ctx ctx = {disp};
    return lvpy_peek_event_dsc_list_cb_user_data(
        lv_display_get_event_count(disp), lvpy_display_peek_get_dsc, &ctx, cb, specific_user_data);
}

typedef struct {
    lv_indev_t *indev;
} lvpy_indev_peek_ctx;

static lv_event_dsc_t *lvpy_indev_peek_get_dsc(uint32_t index, void *ctx)
{
    lvpy_indev_peek_ctx *c = (lvpy_indev_peek_ctx *)ctx;
    return lv_indev_get_event_dsc(c->indev, index);
}

void *lvpy_peek_indev_event_cb_user_data(lv_indev_t *indev, lv_event_cb_t cb, void *specific_user_data)
{
    if (!indev) return NULL;
    lvpy_indev_peek_ctx ctx = {indev};
    return lvpy_peek_event_dsc_list_cb_user_data(
        lv_indev_get_event_count(indev), lvpy_indev_peek_get_dsc, &ctx, cb, specific_user_data);
}

static void py_lv_delete_cb(lv_event_t *e)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    lv_obj_t *lv_obj = lv_event_get_target(e);
    if (lv_obj) {
        uint32_t count = lv_obj_get_event_count(lv_obj);
        for (uint32_t i = 0; i < count; i++) {
            lv_event_dsc_t *dsc = lv_obj_get_event_dsc(lv_obj, i);
            if (dsc) {
                lvpy_release_callback_user_data(lv_event_dsc_get_user_data(dsc));
            }
        }
        py_lv_obj_t *self = (py_lv_obj_t *)lv_obj->user_data;
        if (self) self->lv_obj = NULL;
    }
    PyGILState_Release(gstate);
}

void *mp_lv_callback(PyObject *py_callback, void *lv_callback, const char *callback_name,
    void **user_data_ptr, void *containing_struct,
    void *(*get_user_data)(void *), void (*set_user_data)(void *, void *))
{
    if (lv_callback && py_callback && PyCallable_Check(py_callback)) {
        void *user_data = NULL;
        if (user_data_ptr) {
            /* The holder owns one reference to its dict. For an event
             * registration (containing_struct NULL) that is the registration
             * itself, released by lvpy_release_callback_user_data when the
             * event is removed or the object deleted; each call is a new
             * holder. For a struct field it is the struct: its callbacks
             * share one reference, released with the struct. A fresh dict is
             * born with that reference; a dict already there gets one taken,
             * unless this struct holds it already. */
            if (!*user_data_ptr) {
                *user_data_ptr = PyDict_New();
                if (!*user_data_ptr) return NULL;
                lvpy_registry_add(*user_data_ptr, containing_struct);
            } else if (PyDict_Check((PyObject *)*user_data_ptr) &&
                       !(containing_struct && lvpy_registry_has(*user_data_ptr, containing_struct))) {
                Py_INCREF((PyObject *)*user_data_ptr);
                lvpy_registry_add(*user_data_ptr, containing_struct);
            }
            user_data = *user_data_ptr;
        } else if (get_user_data && set_user_data) {
            user_data = get_user_data(containing_struct);
            if (!user_data) {
                user_data = PyDict_New();
                lvpy_registry_add(user_data, containing_struct);
                set_user_data(containing_struct, user_data);
            }
        }
        if (user_data) {
            PyObject *callbacks = get_callback_dict_from_user_data(user_data);
            if (callbacks) {
                /* The dict's own reference is the only one the callback
                 * needs: it lives exactly as long as the registration. */
                PyDict_SetItemString(callbacks, callback_name, py_callback);
            }
        }
        return lv_callback;
    }
    return mp_to_ptr(py_callback);
}

PyObject *mp_lv_funcptr(PyObject *wrapper, void *lv_fun, void *lv_callback,
    const char *func_name, void *user_data)
{
    (void)wrapper;
    if (!lv_fun) Py_RETURN_NONE;
    if (lv_fun == lv_callback) {
        PyObject *callbacks = get_callback_dict_from_user_data(user_data);
        if (callbacks) {
            /* The dict owns its value: return a reference of our own. */
            PyObject *cb = PyDict_GetItemString(callbacks, func_name);
            if (cb) return Py_NewRef(cb);
        }
    }
    Py_RETURN_NONE;
}

void py_lv_runtime_init_types(void)
{
    if (!lvgl_lock) {
        lvgl_lock = PyThread_allocate_lock();
    }
    if (lvpy_lock_save_key < 0) {
        lvpy_lock_save_key = PyThread_create_key();
    }
    if (!PyLvReferenceError) {
        PyLvReferenceError = PyErr_NewException("lvgl.LvReferenceError", NULL, NULL);
    }
    if (!mp_lv_global_user_data) {
        mp_lv_global_user_data = PyDict_New();
    }
    if (!lvpy_nesting_obj) {
        lvpy_nesting_obj = lvpy_create_nesting_obj();
    }
    if (PyType_Ready(&py_lv_base_struct_type) < 0) return;
    if (PyType_Ready(&py_blob_type) < 0) return;
    if (PyType_Ready(&py_C_Pointer_type) < 0) return;
}

PyTypeObject py_lv_base_struct_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "lvgl.Struct",
    .tp_basicsize = sizeof(py_lv_struct_t),
    .tp_dealloc = (destructor)py_lv_struct_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_as_mapping = &py_lv_struct_as_mapping,
    .tp_methods = py_base_struct_methods,
};

PyTypeObject py_blob_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "lvgl.Blob",
    .tp_basicsize = sizeof(py_lv_struct_t),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_base = &py_lv_base_struct_type,
    .tp_methods = py_blob_methods,
};

PyTypeObject py_C_Pointer_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "lvgl.C_Pointer",
    .tp_basicsize = sizeof(py_lv_struct_t),
    .tp_dealloc = (destructor)py_lv_struct_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_base = &py_lv_base_struct_type,
    .tp_new = py_C_Pointer_new,
};
