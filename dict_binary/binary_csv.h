#ifndef RTT_BINARY_H
 #define RTT_BINARY_H

 #include <string>
 #include <map>
 #include <vector>
 #include <iostream>
 #include <fstream>
 #include <stdio.h>
 #include <exception>
 #include <chrono>
 #include <unistd.h>
 #include <unordered_set>
 #include "zlib.h"

 #define Throw(x) do{throw RTTException(__FILE__,__LINE__,__FUNCTION__,(x));} while (0)

 namespace RTTBinaryDict {

 using std::string;
 enum RETCODE {
     RET_OK = 0,
     RET_ERROR,
     RET_READERROR,
     RET_EMPTY,
     RET_READEND,
 };

 enum DataType {
     Type_START = 0, // must be the first one

     Type_INT16= 1,   // size 2
     Type_INT32 = 2, // size 4
     Type_INT64 = 3, // size 8
     Type_UINT16 = 4,  //
     Type_UINT32 = 5,  //
     Type_UINT64 = 6, //
     Type_FLOAT = 7, //  size 4
     Type_DOUBLE = 8, // size 8
     Type_LD = 9, // long double, size 16. not use
     Type_STRING = 10,
     Type_END // must be the last one
 };


 class RTTException {
 public:
     RTTException(const std::string& file, int line, const std::string& func, const std::string& info="") :
            _file(file), _line(line), _func(func), _info(info) {} std::string info() {
         std::string ret;
         ret.append(_file);
         ret.append(":");
         ret.append(std::to_string(_line));
         ret.append(" ");
         ret.append(_func + "():");
         ret.append(_info);
         return ret;
     }
 private:
     std::string _file;
     int _line;
     std::string _func;
     std::string _info;
 };

 class IRTTFileReader {
 public:
     virtual ~IRTTFileReader() {}

     virtual int readline(std::string& line) = 0;

     virtual int read_col(std::string& val, bool is_scan = false) = 0;

     virtual unsigned long long get_cur() = 0;

     virtual void set_cur(unsigned long long cur) = 0;

     virtual void set_data_start(unsigned long long data_start) = 0;

     virtual unsigned long long get_data_start() = 0;

 };
 const int GZREAD_BUF_SIZE = 1024 * 256;

 class GZFileReader : public IRTTFileReader {
 public:
     GZFileReader(const std::string& fname);

     ~GZFileReader();

     int readline(std::string& line);

     int read(std::string& buf, int size, bool is_scan);

     int read_col(std::string& col, bool is_scan = false);

     unsigned long long get_cur() {
         return _cur;
     }

     void set_cur(unsigned long long cur) {
         _cur = cur;
         _end = cur;
         //std::cout << "set cur:" << cur << std::endl;
         gzseek(_gf, cur, SEEK_SET);
         //std::cout << "tell:" << gztell(_gf) << std::endl;
     }

     void set_data_start(unsigned long long data_start) {
         _data_start = data_start;
     }
     unsigned long long get_data_start() {
         return _data_start;
     }


 private:
     int gz_read(int start, int size);

     bool read_char(char& c);
private:
     gzFile _gf;
     char _buf[GZREAD_BUF_SIZE] = {0};
     unsigned long long _cur = 0;
     unsigned long long _end = 0;
     unsigned long long _data_start = 0;
 };



 class BinaryMMapReader : public IRTTFileReader {
 public:
     BinaryMMapReader(const std::string& file);

     char * get_buf() {
         return _buf;
     }

     unsigned long long get_file_size() {
         return _file_size;
     }

     int readline(std::string& line);

     int readline(char* &buf, int& len);

     int read(char* &buf, int size);

     int read_col(std::string& val, bool is_scan = false);

     int read_col(char*& buf, int& len);

     unsigned long long get_cur() {
         return _cur;
     }
     void set_cur(unsigned long long cur) {
         _cur = cur;
     }

     void set_data_start(unsigned long long data_start) {
         _data_start = data_start;
     }
     unsigned long long get_data_start() {
         return _data_start;
     }

     ~BinaryMMapReader();
 private:
     int fd = 0;
     char * _buf = 0;
     unsigned long long _file_size = 0;
     unsigned long long _cur = 0;
     unsigned long long _data_start = 0;
 };

 class FileReader {
 public:
     FileReader(const std::string& file) : _file(file) {
         if (access(file.c_str(), 0) != 0) {
             Throw(file + " is not existed");
         }
         _in.open(_file, std::ifstream::in);
     }

     int readline(std::string& line) {
         line.clear();
         int ret = getline(_in, line) ? RET_OK : RET_READERROR;
         if (ret == RET_OK && !line.empty() && line[line.size() - 1] == '\r') {
             line.pop_back();
         }
         return ret;
     }
     int read(char* buf, unsigned int size) {
         return _in.read(buf, size) ? RET_OK : RET_READERROR;
     }
     unsigned long long tellg() {
         return _in.tellg();
     }
     int seekg(unsigned long long pos) {
         return _in.seekg(pos) ? RET_OK : RET_ERROR;
     }
     int gcount() {
         return _in.gcount();
     }
     ~FileReader() {
         _in.close();
     }
 private:
     std::string _file;
     std::ifstream _in;
 };

 class IRTTFileWriter {
 public:
     virtual ~IRTTFileWriter() {}

     virtual void writeline(const std::string& line) = 0;
     virtual void write(const char* str, unsigned int size) = 0;
     virtual void write_char(char c) = 0;
     virtual void flush() = 0;
 };

 class GZFileWriter : public IRTTFileWriter {
 public:
     GZFileWriter(const std::string& fname) {
         _gf = gzopen(fname.c_str(), "wb");
         if (_gf == NULL) {
             std::cout << "writer gz open error" << std::endl;
             Throw("gz open " + fname + " failed");
         }
     }

     void write(const char* str, unsigned int size) {
         if (gzwrite(_gf, str, size) != size) {
             std::cout << "gz write error" << std::endl;
             Throw("gz write failed");
         }
     }

     void write_char(char c) {
         gzputc(_gf, c);
     }
    void writeline(const std::string& str) {
         write(str.c_str(), str.size());
         write_char('\n');
     }

     void flush() {
         gzflush(_gf, Z_NO_FLUSH);
     }

     ~GZFileWriter() {
         gzflush(_gf, Z_FINISH);
         gzclose(_gf);
     }


 private:
     gzFile _gf;
 };


 class FileWriter : public IRTTFileWriter {
 public:
     FileWriter(const std::string& file) : _file(file) {
         _out.open(_file, std::ifstream::out);
     }

     void writeline(const std::string& line) {
         _out.write(line.c_str(), line.size());
         write_char('\n');
     }

     void write(const char* str, unsigned int size) {
         _out.write(str, size);
     }
     void write_char(char c) {
         _out.put(c);
     }
     void flush() {
         _out.flush();
     }
     ~FileWriter() {
         flush();
         _out.close();
     }
 private:
     std::string _file;
     std::ofstream _out;
 };

 class Util {
 public:

     static void split(const std::string& src, const std::string& separator, std::vector<std::string>& dest);

     static std::string& trim(std::string &s);

     static DataType get_datatype(const std::string& in);

     static void parse_val_from_str(const std::string& str, const int type, std::string& val);
     static std::time_t getTimeStamp();

     static std::string decode_with_rsa_prikey( const std::string& strPemFileName, const std::string& strData);

     static std::string encode_with_rsa_pubkey( const std::string& strPemFileName, const std::string& strData);

     static void encode_str(const std::string& str, const std::string& outfile);
     static std::string decode_str(const std::string& file);

     static bool is_gzfile(const std::string& fname);
 };


 class RowBinaryColMeta {
 public:
     std::string _col_name;
     int _type;
 };

 class EmptyValue {
 };
 class RTTBinaryRowWriter {
 public:
     RTTBinaryRowWriter(const std::string& out_file) {
         _is_gzfile = Util::is_gzfile(out_file);
         if (_is_gzfile) {
             _writer = new GZFileWriter(out_file);
         } else {
             _writer = new FileWriter(out_file);
         }
         if (_writer == NULL) {
             Throw("new writer failed");
         }
     }

     ~RTTBinaryRowWriter() {
         delete _writer;
     }

     template <class T> int get_str_from_val(const T& val, std::string& str) {
         str.assign(static_cast<char*>(static_cast<void*>(const_cast<T *>(&val))), sizeof(T));
         return RET_OK;
     }

     int load_col_dict(const std::string& dict_file) {
         FileReader dict_reader(dict_file);
         build_cols_dict(dict_reader);
         return RET_OK;
     }

     int write_header() {
         write_header(_writer);
         return RET_OK;
     }

     int get_data_type(int index) {
         if (index < 0 || index >= _col_metas.size()) {
             return -1;
         }
         return _col_metas[index]._type;
     }

     void flush() {
         _writer->flush();
     }

     int write_row(const std::vector<std::string>& row) {
         return write_binary_line(_writer, row);
     }

     template <class T> int push_row(const T& val, std::vector<std::string>& row) {
         std::string str;
         get_str_from_val<T>(val, str);
         row.push_back(str);
         return RET_OK;
     }

     void push_col_meta(const RowBinaryColMeta& col_meta) {
         if (col_meta._type <= Type_START || col_meta._type >= Type_END) {
             Throw("push error, unknown data type " + std::to_string(col_meta._type));
         }
         _col_metas.push_back(col_meta);
     }

     void push_col_meta(const std::string& col_name, int datatype) {
         RowBinaryColMeta col_meta;
         col_meta._col_name = col_name;
         col_meta._type = datatype;
         push_col_meta(col_meta);
     }

     int get_col_size() {
         return _col_metas.size();
     }

     void convert(const std::string& csv_file, const std::string& dict_file, const std::string split = ",");

 private:
     void build_cols_dict(FileReader& reader);
     void parse_csv_header(FileReader& reader, const std::string& split);
     void parse_line(const std::string& line, std::vector<std::string>& vals, const std::string& split);
     int write_binary_line(IRTTFileWriter* writer, const std::vector<std::string>& vals);
     void write_header(IRTTFileWriter* writer);

 private:
     //FileWriter _writer;
     IRTTFileWriter* _writer;
     std::string _split;
     std::map<std::string, DataType> _col_datatype_map;
     std::vector<RowBinaryColMeta> _col_metas;
     bool _is_gzfile = false;
 };


 class RTTBinaryRowReader {
 public:
     RTTBinaryRowReader(const std::string& binary_file, const std::string split = ",") : _split(split) {
         _is_gzfile = Util::is_gzfile(binary_file);
         if (_is_gzfile) {
             _reader = new GZFileReader(binary_file);
         } else {
             _reader = new BinaryMMapReader(binary_file);

         }
         if (_reader == NULL) {
             Throw("new reader failed");
         }
     }

     ~RTTBinaryRowReader() {
         if (_reader) {
             delete _reader;
             _reader = NULL;
         }
     }
     int init();
     void read_header();

     bool is_gzfile() {
         return _is_gzfile;
     }

     int add_filter_col(const std::string& col_name) {
         _filter_cols.insert(col_name);
     }

     int read_row(std::vector<std::string>& vals);

     void get_header_line(std::string& line) {
         for (auto it = _col_metas.begin(); it != _col_metas.end(); ++it) {
             //if (_filter_cols.empty() || _filter_cols.find(it->_col_name) != _filter_cols.end()) {
                 line.append(it->_col_name);
                 line.append(",");
             //}
         }
         line.pop_back();
     }
     const std::vector<RowBinaryColMeta>& get_col_metas() {
         return _col_metas;
     }

     int get_col_datatype(int index) {
         if (index < 0 || index > _col_metas.size()) {
             return RET_ERROR;
         }
         return _col_metas[index]._type;
     }

     int get_col_name(int index, std::string& col_name) {
         if (index < 0 || index > _col_metas.size()) {
             return RET_ERROR;
         }
         col_name = _col_metas[index]._col_name;
         return RET_OK;
     }
     int get_col_size() { // return filtered column size
         return _col_metas.size();
     }

     int get_row_size() {
         return _row_size;
     }

     template <class T> void get_value(std::string& bin_str, T * val) {
         *val = *(static_cast<T *>(static_cast<void *>(const_cast<char *>(bin_str.c_str()))));
         //std::cout << "[" << *(static_cast<T *>(static_cast<void *>(const_cast<char *>(bin_str.c_str())))) << "]";
     }


 private:
     std::vector<RowBinaryColMeta> _col_metas;
     //BinaryMMapReader _reader;
     IRTTFileReader *_reader;
     std::string _split;
     std::unordered_set<std::string> _filter_cols;
     std::unordered_set<int> _filter_col_ids;
     int _row_size = 0; // all row size
     int _col_size = 0; // all column size
     bool _is_gzfile = false;
 };

 } // namespace

 #endif // RTT_BINARY_H

