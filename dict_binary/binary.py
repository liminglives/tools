#!/usr/bin/env python2.7

# author : zlm(Zhengliming)

#from csv_binary import reader
#from csv_binary import writer
import csv_binary
import pandas
import numpy as np
import sys

class RTF(object):
    INT16 = 1
    INT32 = 2
    INT64 = 3
    UINT16 = 4
    UINT32 = 5
    UINT64 = 6
    FLOAT = 7
    DOUBLE = 8
    STRING = 10

    DataTypeDict = {
        INT16:{"np_dtype":np.int16, "type":"int16", "size":2, "format":"h"},
        INT32:{"np_dtype":np.int32, "type":"int32", "size":4, "format":"i"},
        INT64:{"np_dtype":np.int64, "type":"int64", "size":8, "format":"l"},
        UINT16:{"np_dtype":np.uint16, "type":"uint16", "size":2, "format":"L"},
        UINT32:{"np_dtype":np.uint32, "type":"uint32", "size":4, "format":"q"},
        UINT64:{"np_dtype":np.uint64, "type":"uint64", "size":8, "format":"Q"},
        FLOAT:{"np_dtype":np.float32, "type":"float", "size":4, "format":"f"},
        DOUBLE:{"np_dtype":np.float64, "type":"double", "size":8, "format":"d"},
        STRING:{"np_dtype":np.object_, "type":"string", "size":0, "format":""},
    }

    NPTypeDict = {np.int16 : INT16, np.int32 : INT32, np.int64 : INT64,
                  np.uint16 : UINT16, np.uint32 : UINT32, np.uint64 : UINT64,
                  np.float32 : FLOAT, np.float64 : DOUBLE, np.object_ : STRING}

    @staticmethod
    def np_dtype_convert2(dtype):
        if dtype in RTF.NPTypeDict:
            return RTF.NPTypeDict[dtype]
       return None

    @staticmethod
    def np_dtype_convert(dtype):
        if dtype == np.int16:
            return RTF.INT16
        elif dtype == np.int32:
            return RTF.INT32
        elif dtype == np.int64:
            return RTF.INT64
        elif dtype == np.uint16:
            return RTF.UINT16
        elif dtype == np.uint32:
            return RTF.UINT32
        elif dtype == np.uint64:
            return RTF.UINT64
        elif dtype == np.float32:
            return RTF.FLOAT
        elif dtype == np.float64:
            return RTF.DOUBLE
        elif dtype == np.object_:
            return RTF.STRING
        else:
            return None


    @staticmethod
    def isNan(num):
        return num != num

    @staticmethod
    def dump_from_dataframe(file_name, df):
        col_dtype = df.dtypes
        header = []
        for col in col_dtype.iteritems():
            name = col[0]
            t = RTF.np_dtype_convert(col[1])
            if t == None:
                raise ValueError(str(col) + " is not illegal")
            header.append((name, t))

        w = DictWriter(file_name)
        w.write_header(header)

        for row in df.iterrows():
            row_list = []
            for item in row[1].iteritems():
                row_list.append(item)
            d = dict(row_list)
            w.write_row(d)
        w.close()

    @staticmethod
    def to_dataframe(file_name):
        b = csv_binary.reader(file_name)
        row_num = b.row_num();
        dtypes = b.dtype()
        col_list = []
        for i in range(b.col_num()):
            col_list.append(np.empty(row_num, dtype=RTF.DataTypeDict[dtypes[i]]["np_dtype"]))
        line_no = 0
        for row in b:
            if line_no >= row_num:
                print "error"
                break;
            for i,item in enumerate(row):
                col_list[i][line_no] = item
            line_no += 1

        data = {}
        for i,val in enumerate(b.index()):
            data[val] = col_list[i]
        df = pandas.DataFrame(data)
        return df

class DictReader:
    def __init__(self, f):
        self._reader = csv_binary.reader(f)
        if not self._reader:
            raise ValueError("open csv " + f + " failed")
        self._header = self._reader.index()

    def __iter__(self):
        return self

    def header(self):
        return self._header

    def __next__(self):
        row = next(self._reader)
        if len(row) != len(self._header):
            raise ValueError("len of row is not equal to header")
        d = dict(zip(self._header, row))
        return d

    def next(self):
        return self.__next__()

    def close(self):
        self._reader.close()

class DictWriter:
    def __init__(self, f):
        self.__f = f
        self._writer = csv_binary.writer(f)
        self.header = None

    def write_header(self, header):
        self.header = header
        self._writer.write_header(header)

    def write_row(self, row_dict):
        row = []
        for i, val in enumerate(self.header):
            if val[0] not in row_dict:
                row.append(None)
            else:
                row.append(row_dict[val[0]] if not pandas.isnull(row_dict[val[0]]) else None)

        if len(row) != len(self.header):
            raise ValueError("write row failed, short of row item")

        if -1 == self._writer.write_row(row):
            raise IOError("write file failed " + str(self.__f))

    def flush(self):
        self._writer.flush()

    def close(self):
        self._writer.close()





