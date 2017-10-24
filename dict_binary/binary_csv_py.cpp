#include <Python.h>
#include "rtt_binary.h"

typedef struct {
    PyObject_HEAD
    void * reader;
    //bool header_readed;
    int col_num;
    int row_num;
} BinaryCSVReader;

typedef struct {
    PyObject_HEAD
    void * writer;
} BinaryCSVWriter;

static PyObject* BinaryCSVReader_iter(PyObject* self) {
    Py_INCREF(self);
    return self;
}

static void close_reader(BinaryCSVReader* binary_reader) {
    if (binary_reader && binary_reader->reader) {
        delete (RTTBinaryDict::RTTBinaryRowReader*)(binary_reader->reader);
        binary_reader->reader = NULL;
    }
}

static void BinaryCSVReader_dealloc(PyObject* self) {
    BinaryCSVReader *binary_reader = (BinaryCSVReader *)self;
    close_reader(binary_reader);
    Py_TYPE(self)->tp_free(self);
}

PyObject* BinaryCSVReader_close(PyObject* self) {
    BinaryCSVReader* binary_reader = (BinaryCSVReader *)self;
    close_reader(binary_reader);
    return Py_BuildValue("i", 0);
}


static PyObject* BinaryCSVReader_iternext(PyObject* self) {
    BinaryCSVReader *binary_reader = (BinaryCSVReader *)self;
    RTTBinaryDict::RTTBinaryRowReader * reader = (RTTBinaryDict::RTTBinaryRowReader*)(binary_reader->reader);
    //if (!binary_reader->header_readed) {
    //    reader->read_header();
    //    binary_reader->header_readed = true;
    //    binary_reader->col_num = reader->get_col_size();
    //}

    std::vector<std::string> row_vals;
    row_vals.reserve(binary_reader->col_num);
    if (reader->read_row(row_vals) == RTTBinaryDict::RET_OK) {
        PyObject* row = PyList_New(binary_reader->col_num);
        for (unsigned int i = 0; i < row_vals.size(); ++i) {
            if (row_vals[i].size() == 0) {
                PyList_SetItem(row, i, Py_BuildValue(""));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_INT16) {
                int16_t val = 0;
                reader->get_value<int16_t>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("h", val));

            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_INT32) {
                int32_t val = 0;
                reader->get_value<int32_t>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("i", val));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_INT64) {
                int64_t val = 0;
                reader->get_value<int64_t>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("l", val));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_UINT16) {
                uint16_t val = 0;
                reader->get_value<uint16_t>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("H", val));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_UINT32) {
                uint32_t val = 0;
                reader->get_value<uint32_t>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("I", val));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_UINT64) {
                uint64_t val = 0;
                reader->get_value<uint64_t>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("k", val));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_FLOAT) {
                float val = 0;
                reader->get_value<float>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("d", val));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_DOUBLE) {
                double val = 0;
                reader->get_value<double>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("d", val));
            } else if (reader->get_col_datatype(i) == RTTBinaryDict::Type_STRING) {
                std::string val;
                reader->get_value<std::string>(row_vals[i], &val);
                PyList_SetItem(row, i, Py_BuildValue("s", val.c_str()));
            } else {
                PyList_SetItem(row, i, Py_BuildValue("s", "unknown"));
            }
        }
        return row;

    } else {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
}

PyObject* BinaryCSVReader_get_col_num(PyObject* self) {
    BinaryCSVReader* csv_reader = (BinaryCSVReader *)self;
    return Py_BuildValue("i", csv_reader->col_num);
}

PyObject* BinaryCSVReader_get_row_num(PyObject* self) {
    BinaryCSVReader* csv_reader = (BinaryCSVReader *)self;
    return Py_BuildValue("i", csv_reader->row_num);
}

PyObject* BinaryCSVReader_get_index(PyObject* self) {
    BinaryCSVReader* csv_reader = (BinaryCSVReader *)self;
    RTTBinaryDict::RTTBinaryRowReader* reader = (RTTBinaryDict::RTTBinaryRowReader*)(csv_reader->reader);

    const std::vector<RTTBinaryDict::RowBinaryColMeta>& col_metas = reader->get_col_metas();
    PyObject* index = PyList_New(col_metas.size());
    for (unsigned int i = 0; i < col_metas.size(); ++i) {
        PyList_SetItem(index, i, Py_BuildValue("s", (col_metas[i]._col_name).c_str()));
    }

    return index;
}

PyObject* BinaryCSVReader_get_dtype(PyObject* self) {
    BinaryCSVReader* csv_reader = (BinaryCSVReader *)self;
    RTTBinaryDict::RTTBinaryRowReader* reader = (RTTBinaryDict::RTTBinaryRowReader*)(csv_reader->reader);

    const std::vector<RTTBinaryDict::RowBinaryColMeta>& col_metas = reader->get_col_metas();
    PyObject* dtype = PyList_New(col_metas.size());
    for (unsigned int i = 0; i < col_metas.size(); ++i) {
        PyList_SetItem(dtype, i, Py_BuildValue("i", (col_metas[i]._type)));
    }

    return dtype;
}

static PyMethodDef ReaderSelfMethods[] = {
    {"col_num", (PyCFunction)BinaryCSVReader_get_col_num, METH_NOARGS, ""},
    {"row_num", (PyCFunction)BinaryCSVReader_get_row_num, METH_NOARGS, ""},
    {"index", (PyCFunction)BinaryCSVReader_get_index, METH_NOARGS, ""},
    {"dtype", (PyCFunction)BinaryCSVReader_get_dtype, METH_NOARGS, ""},
    {"close", (PyCFunction)BinaryCSVReader_close, METH_NOARGS, ""},
    {NULL, NULL, 0, NULL}

};

static PyTypeObject CSVBinaryReader_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "binary_csv._reader",      /*tp_name*/
    sizeof(BinaryCSVReader),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    BinaryCSVReader_dealloc,   /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
      /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
         use tp_iter and tp_iternext fields. */
    "Internal myiter iterator object.",           /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    BinaryCSVReader_iter,  /* tp_iter: __iter__() method */
    BinaryCSVReader_iternext, /* tp_iternext: next() method */
    ReaderSelfMethods /* methods */
};


static PyObject * csv_binary_reader(PyObject* self, PyObject* args) {
    const char* s;
    if (!PyArg_ParseTuple(args, "s", &s)) {
        return NULL;
    }

    BinaryCSVReader* binary_reader;
    binary_reader = PyObject_New(BinaryCSVReader, &CSVBinaryReader_Type);
    if (binary_reader == NULL) {
        return NULL;
    }

    if (!PyObject_Init((PyObject*)binary_reader, &CSVBinaryReader_Type)) {
        Py_DECREF(binary_reader);
        return NULL;
    }

    RTTBinaryDict::RTTBinaryRowReader* reader = NULL;
    try {
        reader = new RTTBinaryDict::RTTBinaryRowReader(s);
        if (reader == NULL) {
            Py_DECREF(binary_reader);
            return NULL;
        }
        if (reader->init() != RTTBinaryDict::RET_OK) {
            delete reader;
            Py_DECREF(binary_reader);
            return NULL;
        }
    } catch (RTTBinaryDict::RTTException& e) {
        std::cout << e.info() << std::endl;
        delete reader;
        Py_DECREF(binary_reader);
        return NULL;
    }

    binary_reader->reader = (void *)reader;
    binary_reader->col_num = reader->get_col_size();
    binary_reader->row_num = reader->get_row_size();;

    return (PyObject *)binary_reader;
}

/////   writer

static void close_writer(BinaryCSVWriter* binary_writer) {
    if (binary_writer != NULL && binary_writer->writer != NULL) {
        delete (RTTBinaryDict::RTTBinaryRowWriter*)(binary_writer->writer);
        binary_writer->writer = NULL;
    }
}

static void BinaryCSVWriter_dealloc(PyObject* self) {
    BinaryCSVWriter *binary_writer = (BinaryCSVWriter *)self;
    close_writer(binary_writer);
    Py_TYPE(self)->tp_free(self);
}

static int push_row(RTTBinaryDict::RTTBinaryRowWriter* writer, int index, PyObject* item,
        std::vector<std::string>& row) {
    int type = writer->get_data_type(index);
    if (type == -1) {
        return -1;
    }
    if ((PyInt_Check(item) || PyLong_Check(item)) && (type >= RTTBinaryDict::Type_INT16 && type <= RTTBinaryDict::Type_UINT64)) {
        long val_l = 0;
        unsigned long val_ul = 0;
        if (PyInt_Check(item)) {
            val_l = PyInt_AsLong(item);
            val_ul = PyInt_AsUnsignedLongMask(item);
        } else {
            val_l = PyLong_AsLong(item);
            val_ul = PyLong_AsUnsignedLong(item);
        }

        if (type == RTTBinaryDict::Type_INT16) {
            writer->push_row<int16_t>((int16_t)val_l, row);
        } else if (type == RTTBinaryDict::Type_INT32) {
            writer->push_row<int32_t>((int32_t)val_l, row);
        } else if (type == RTTBinaryDict::Type_INT64) {
            writer->push_row<int64_t>((int64_t)val_l, row);
        } else if (type == RTTBinaryDict::Type_UINT16) {
            writer->push_row<uint16_t>((uint16_t)val_ul, row);
        } else if (type == RTTBinaryDict::Type_UINT32) {
            writer->push_row<uint32_t>((uint32_t)val_ul, row);
        } else if (type == RTTBinaryDict::Type_UINT64) {
            writer->push_row<uint64_t>((uint64_t)val_ul, row);
        } else {
            std::cout << "index=" << index << " int unknown type:" << type << std::endl;
            return -1;
        }
    } else if (PyFloat_Check(item) && (type == RTTBinaryDict::Type_FLOAT || type == RTTBinaryDict::Type_DOUBLE)) {
        double val = PyFloat_AsDouble(item);
        if (type == RTTBinaryDict::Type_FLOAT) {
            writer->push_row<float>((float)val, row);
        } else if (type == RTTBinaryDict::Type_DOUBLE) {
            writer->push_row<double>(val, row);
        } else {
            std::cout << "index=" << index << " float unknown type:" << type << std::endl;
            return -1;
        }
    } else if (PyString_Check(item) && type == RTTBinaryDict::Type_STRING) {
        const char* str = PyString_AsString(item);
        writer->push_row<std::string>(str, row);
    } else if (item == Py_None) {
        RTTBinaryDict::EmptyValue empty_value;
        writer->push_row<RTTBinaryDict::EmptyValue>(empty_value, row);
    } else {
        std::cout << "index=" << index << " unsupported python type " << type << std::endl;
        return -1;
    }

    return 0;
}

static PyObject* BinaryCSVWriter_write_row(PyObject* self, PyObject* args) {
    PyObject* list;
    if (!PyArg_ParseTuple(args, "O", &list)) {
        std::cout << "parse failed" << std::endl;
        return NULL;
    }

    if (!PyList_Check(list)) {
        std::cout << "param is not list type" << std::endl;
        return Py_BuildValue("i", -1);;
    }

    RTTBinaryDict::RTTBinaryRowWriter * writer = (RTTBinaryDict::RTTBinaryRowWriter*)(((BinaryCSVWriter *)self)->writer);

    try {
        int size = PyList_Size(list);
        std::vector<std::string> row;
        row.reserve(writer->get_col_size());
        for (int i = 0; i < size; ++i) {
            PyObject* item = PyList_GetItem(list, i);
            if (0 != push_row(writer, i, item, row)) {
                return Py_BuildValue("i", -1);
            }
        }
        if (RTTBinaryDict::RET_OK != writer->write_row(row)) {
            std::cout << "writer row error" << std::endl;
            return Py_BuildValue("i", -1);
        }
    } catch (RTTBinaryDict::RTTException& e) {
        std::cout << e.info() << std::endl;
        return Py_BuildValue("i", -1);
    }

    return Py_BuildValue("i", 0);
}

static PyObject* BinaryCSVWriter_flush(PyObject* self) {
    RTTBinaryDict::RTTBinaryRowWriter * writer = (RTTBinaryDict::RTTBinaryRowWriter*)(((BinaryCSVWriter *)self)->writer);
    writer->flush();
    return Py_BuildValue("i", 0);
}

static PyObject* BinaryCSVWriter_close(PyObject* self) {
    close_writer((BinaryCSVWriter *)self);
    return Py_BuildValue("i", 0);
}


static PyObject* BinaryCSVWriter_write_header(PyObject* self, PyObject* args) {
    PyObject* list;
    if (!PyArg_ParseTuple(args, "O", &list)) {
        std::cout << "parse failed" << std::endl;
        return NULL;
    }
    if (!PyList_Check(list)) {
        std::cout << "param is not list type" << std::endl;
        return Py_BuildValue("i", -1);;
    }

    RTTBinaryDict::RTTBinaryRowWriter * writer = (RTTBinaryDict::RTTBinaryRowWriter*)(((BinaryCSVWriter *)self)->writer);

    try {
        int size = PyList_Size(list);
        for (int i = 0; i < size; ++i) {
            PyObject* item = PyList_GetItem(list, i);
            PyObject* name_py = PyTuple_GetItem(item, 0);
            PyObject* type_py = PyTuple_GetItem(item, 1);
            const char* name = PyString_AsString(name_py);
            int type = PyInt_AsLong(type_py);
            writer->push_col_meta(name, type);
        }
        writer->write_header();
    } catch (RTTBinaryDict::RTTException& e) {
        std::cout << e.info() << std::endl;
        return Py_BuildValue("i", -1);
    }

    return Py_BuildValue("i", 0);
}

static PyMethodDef WriterSelfMethods[] = {
    {"write_header", (PyCFunction)BinaryCSVWriter_write_header, METH_VARARGS, ""},
    {"write_row", (PyCFunction)BinaryCSVWriter_write_row, METH_VARARGS, ""},
    {"flush", (PyCFunction)BinaryCSVWriter_flush, METH_NOARGS, ""},
    {"close", (PyCFunction)BinaryCSVWriter_close, METH_NOARGS, ""},
    {NULL, NULL, 0, NULL}
};


static PyTypeObject CSVBinaryWriter_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "binary_csv._writer",      /*tp_name*/
    sizeof(BinaryCSVWriter),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    BinaryCSVWriter_dealloc,   /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
      /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
         use tp_iter and tp_iternext fields. */
    "Internal myiter iterator object.",           /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare naryCSVWriter_write_header*/
    0,  /* tp_weaklistoffset */
    0,  /* tp_iter: __iter__() method */
    0, /* tp_iternext: next() method */
    WriterSelfMethods /* methods */
};

static PyObject * csv_binary_writer(PyObject* self, PyObject* args) {
    const char* file;
    if (!PyArg_ParseTuple(args, "s", &file)) {
        return NULL;
    }

    BinaryCSVWriter* binary_writer;
    binary_writer = PyObject_New(BinaryCSVWriter, &CSVBinaryWriter_Type);
    if (binary_writer == NULL) {
        return NULL;
    }

    if (!PyObject_Init((PyObject*)binary_writer, &CSVBinaryWriter_Type)) {
        Py_DECREF(binary_writer);
        return NULL;
    }

    RTTBinaryDict::RTTBinaryRowWriter* writer = new RTTBinaryDict::RTTBinaryRowWriter(file);
    if (writer == NULL) {
        Py_DECREF(binary_writer);
        return NULL;
    }

    binary_writer->writer = (void *)writer;

    return (PyObject *)binary_writer;
}



static PyMethodDef CSVBinaryMethods[] = {
    {"reader", csv_binary_reader, METH_VARARGS, ""},
    {"writer", csv_binary_writer, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initcsv_binary(void) {
    PyObject* m;
    CSVBinaryReader_Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&CSVBinaryReader_Type) < 0) {
        return;
    }
    CSVBinaryWriter_Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&CSVBinaryWriter_Type) < 0) {
        return;
    }
    m = Py_InitModule("csv_binary", CSVBinaryMethods);

    Py_INCREF(&CSVBinaryReader_Type);
    Py_INCREF(&CSVBinaryWriter_Type);
    PyModule_AddObject(m, "_reader", (PyObject *)&CSVBinaryReader_Type);
    PyModule_AddObject(m, "_writer", (PyObject *)&CSVBinaryWriter_Type);
}


