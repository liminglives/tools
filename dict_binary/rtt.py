import mmap
import struct

import datetime
datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

DataTypeMap = {
        0:{"type":"short", "size":2, "format":"h"},
        1:{"type":"int", "size":4, "format":"i"},
        2:{"type":"long", "size":8, "format":"l"},
        3:{"type":"unsigned long", "size":8, "format":"L"},
        4:{"type":"long long", "size":8, "format":"q"},
        5:{"type":"unsigned long long", "size":8, "format":"Q"},
        6:{"type":"float", "size":4, "format":"f"},
        7:{"type":"double", "size":8, "format":"d"},
        100:{"type":"string", "size":0, "format":""},
        }

class MMapWraper():
    def __init__(self, f):
        self.mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    def readline():
        return self.mmap.readline();

class RTTBinary():
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, 'rb') # file exist ?
	self.mmap = mmap.mmap(self.f.fileno(), 0, access=mmap.ACCESS_READ)
        self.meta = {}
        self.header = ""
        self.rtt_data = {}
        self.col_list = []

    def read_header(self):
        header = self.mmap.readline()

    def read_meta(self):
        line = self.mmap.readline().strip()
        while (len(line) > 0):
            arr = line.split(" ")
            if len(arr) < 4:
                print line
                raise Exception("meta line illegal")
            col_meta = {}
            for item in arr:
                pair = item.split("=")
                if len(pair) != 2:
                    print "pair error, meta line illegal"
                    raise Exception("pair error, meta line illegal")
                col_meta[pair[0]] = pair[1]
            self.meta[col_meta["name"]] = col_meta
            self.col_list.append(col_meta["name"])

            line = self.mmap.readline().strip()

    def parse_fixed_val_len(self, col_meta, data_zone_start):
        start = data_zone_start + int(col_meta["start"])
        data_len = int(col_meta["len"])
        self.mmap.seek(start)
        readed_len = 0
        val_size = DataTypeMap[int(col_meta["type"])]["size"]
        val_list = []
        format_str = DataTypeMap[int(col_meta["type"])]["format"]
        while(readed_len < data_len):
            NaN_mark = self.mmap.read_byte()
            readed_len += 1
            if NaN_mark == '0':
                val_list.append("NaN")
                continue
            if (readed_len + val_size > data_len):
                raise Exception("read col " + col_meta['name'] + " overflow")
            data = self.mmap.read(val_size)
            readed_len += val_size
            val = struct.unpack_from(format_str, data)
            #print type(val), val
            val_list.append(val[0])
        #return val_list
        self.rtt_data[col_meta["name"]] = val_list

    def parse_str(self, col_meta, data_zone_start):
        start = data_zone_start + int(col_meta["start"])
        data_len = int(col_meta["len"])
        self.mmap.seek(start)
        data = self.mmap.read(data_len)
        val_list = data.split("\0")
        val_list.pop(0)
        #return val_list
        self.rtt_data[col_meta["name"]] = val_list


    def read_data(self):
        data_zone_start = self.mmap.tell()
        for name in self.col_list:
        #for name,col_meta in self.meta.items():
            #print col_meta
            col_meta = self.meta[name]
            data_type = int(col_meta["type"])
            #print data_type
            if DataTypeMap[data_type]["type"] == "string":
                self.parse_str(col_meta, data_zone_start)
            else:
                self.parse_fixed_val_len(col_meta, data_zone_start)
        return self.rtt_data

    def read(self):
        self.read_header()
        self.read_meta()
        return self.read_data()

if __name__ == "__main__":
    f = "rtt.large.binary3"
    import time
    start = time.time()
    rtt = RTTBinary(f)
    data = rtt.read()
    end = time.time()
    print end - start
    #for key in data:
    #    print key + " : " + str(data[key])
