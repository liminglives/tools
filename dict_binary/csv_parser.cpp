#include <string>
#include <map>
#include <vector>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <exception>
#include <chrono>
#include <sys/mman.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <stdio.h>
#include <unistd.h>

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

using int16 = short;
using int32 = int;
using int64 = long long;

enum DataType {
    Type_SHORT = 0,	 // size 2
    Type_INT = 1,	// size 4
    Type_LONG = 2,	// size 8 
    Type_UL = 3,  // unsigned long, size 8
    Type_LL = 4,  // long long, size 8
    Type_ULL = 5, // unsigned long long, size 8
    Type_FLOAT = 6, //  size 4
    Type_DOUBLE = 7, // size 8
    Type_LD = 8, // long double, size 16

    Type_STRING = 100,

	Type_UNKNOWN // must be the last one
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
		ret.append(_func);
		ret.append(" info:");
		ret.append(_info);
		return ret;
	}
private:
    std::string _file;
    int _line;
    std::string _func;
    std::string _info;
};


template <class T>
int get_datatype_size() {
    return sizeof(T);
}

class BinaryMMapReader {
public:
    BinaryMMapReader() {}
    int init(const std::string& file) {
        _file = file;
        struct stat st;
        if (stat(_file.c_str(), &st) == -1) {
            Throw("failed to get file stat, " + _file);
        }
        fd = open(_file.c_str(), O_RDONLY);
        if (fd == -1) {
            Throw("failed to open file " + _file);
        }
        _file_size = st.st_size;
        _buf = static_cast<char *>(mmap(NULL, _file_size, PROT_READ, MAP_PRIVATE, fd, 0));
        if (_buf == MAP_FAILED || _buf == NULL) {
            Throw("failed to map");
        }
    }

    char * get_buf() {
        return _buf;
    }
    
    int readline(char* &buf, int& len) {
        unsigned long long pos = _cur;
        buf = _buf + _cur;
        len = 0;
        while (pos < _file_size) {
            if (_buf[pos] == '\n') {
                break;
            }
            ++pos;
        }
        len = pos - _cur;
        if (len > 0 && buf[pos - 1] == '\r') {
            --len;
        }

        _cur = pos + 1;
        if (len == 0 && pos >= _file_size) {
            return RET_READERROR;
        }
        return RET_OK;
    }

    int read_col(std::string& val) {
        unsigned long long pos = _cur;
        if (pos >= _file_size) {
            return RET_READERROR;
        }
        unsigned int read_len = 0;
        if (_buf[pos] == '\0') {
            ++pos;
            while (pos < _file_size) {
                if (_buf[pos] == '\0') {
                    break;
                }
                ++pos;
            }
            read_len = pos - _cur - 1;

            //val.assign(_buf + _cur + 1, pos - _cur);
            _cur = pos + 1;
        } else {
            read_len = _buf[pos] - '0';
            _cur += read_len + 1;
        }
        if (read_len + 1 + _cur >= _file_size) {
            Throw("read overflow");
        }
        val.assign(_buf + _cur + 1, read_len);
        return RET_OK;
    }
    ~BinaryMMapReader() {
        munmap(_buf, _file_size);
        close(fd);
    }
private:
    std::string _file;
    int fd = 0;
    char * _buf = 0;
    unsigned long long _file_size = 0;
    unsigned long long _cur = 0;
};


const unsigned int BINARY_LINE_MAX_LEN = 512;
class FileReader {
public:
	FileReader(const std::string& file) : _file(file) {
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

class FileWriter {
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

	~FileWriter() {
		_out.flush();
		_out.close();
	}
private:
	std::string _file;
	std::ofstream _out;
};

class Util {
public:

static void split(const std::string& src, const std::string& separator, std::vector<std::string>& dest)
{
	//dest.clear();
    using namespace std;
    string str = src;
    string substring;
    string::size_type start = 0, index;

    do
    {
        index = str.find_first_of(separator,start);
        if (index != string::npos)
        {    
            substring = str.substr(start,index-start);
            dest.push_back(trim(substring));
			start = index + separator.size();
            //start = str.find_first_not_of(separator,index);
            if (start == string::npos) return;
        }
    }while(index != string::npos);
    
    //the last token
    substring = str.substr(start);
    dest.push_back(trim(substring));
}

static std::string& trim(std::string &s)   
{  
    if (s.empty())   
    {  
        return s;  
    }  
    s.erase(0,s.find_first_not_of(" "));  
    s.erase(s.find_last_not_of(" ") + 1);  
    return s;  
} 

static DataType get_datatype(const std::string& in) {
	if (in.empty()) {
		return Type_UNKNOWN;
	}
    bool has_dot = false;
    bool has_number = false;
	bool has_other = false;
    for (unsigned int i = 0; i < in.size(); ++i) {
		//if ((in[i] >= 'a' && in[i] =< "z") || (in[i] >= 'A' && in[i] =< 'Z')) {
		//	has_char = true;
		if (in[i] == '.') {
			has_dot = true;
		} else if (in[i] >= '0' && in[i] <= '9') {
			has_number = true;
		} else {
			has_other = true;
		}
    }
	if (has_other || !has_number) {
		return Type_STRING;
	} else if (has_dot && has_number) {
		return Type_FLOAT;
	} else {
		return Type_INT;
	}
}

static void parse_val_from_str(const std::string& str, const DataType type, std::string& val) {
	if (str.empty()) {
		return;
	}
	switch (type) {
		case Type_SHORT:
		{
		    short v = static_cast<short>(std::stoi(str));
		    val.assign((char*)&v, sizeof(short));
			break;
		}
		case Type_INT:
		{
		    int v = (std::stoi(str));
		    val.assign((char*)&v, sizeof(int));
			break;
		}
		case Type_LONG:
		{
		    long v = std::stol(str);
		    val.assign((char*)&v, sizeof(long));
			break;
		}
		case Type_UL:
		{
		    unsigned long v = std::stoul(str);
		    val.assign((char*)&v, sizeof(unsigned long));
			break;
		}
		case Type_LL:
		{
		    long long v = std::stoll(str);
		    val.assign((char*)&v, sizeof(long long));
			break;
		}
		case Type_ULL:
		{
		    unsigned long long v = std::stoull(str);
		    val.assign((char*)&v, sizeof(unsigned long long));
			break;
		}
		case Type_FLOAT:
		{
		    float v = std::stof(str);
		    val.assign((char*)&v, sizeof(float));
			break;
		}
		case Type_DOUBLE:
		{
		    double v = std::stod(str);
		    val.assign((char*)&v, sizeof(double));
			break;
		}
		case Type_LD:
		{
		    long double v = std::stold(str);
		    val.assign((char*)&v, sizeof(long double));
			break;
		}
		case Type_STRING:
		{
		    val = str;
			break;
		}
		default:
		    Throw( "unkonw type");
	}
}

static std::time_t getTimeStamp()
{
    std::chrono::time_point<std::chrono::system_clock,std::chrono::milliseconds> tp = std::chrono::time_point_cast<std::chrono::milliseconds>(std::chrono::system_clock::now());
    auto tmp=std::chrono::duration_cast<std::chrono::milliseconds>(tp.time_since_epoch());
    std::time_t timestamp=tmp.count();
    //std::time_t timestamp=std::chrono::system_clock::to_time_t(tp);
    return timestamp;
}


};

//template <class T>
//class Column {
//public:	
//    Column(const std::string& name) : _name(name), _type(Type_UNKNOWN) {}
//    int parse_value(std::string& in, T& ret) {
//		if (in.empty()) {
//			return RET_EMPTY;
//		}
//	    try {
//		    ret = boost::lexical_cast<T>(in);	
//		} catch (...) {
//			printf("lexical_cast error, in[%s]", in.c_str());
//			return RET_ERROR;
//		}
//		return RET_OK;
//	}
//    void push(const std::string& in) {
//		T val;
//		int ret = parse_value(in, val);
//		if (ret == RET_ERROR) {
//			Throw( "parse value[" + in + "] failed";
//		} else if (ret == RET_EMPTY) {
//			_empty_value_set.insert(_values.size());
//		}
//		_values.push_back(val);
//	}
//private:
//    std::string _name;
//    DataType _type;
//    std::vector<T> _values;
//    std::set<int> _empty_value_index_set;
//};

struct ColumnMeta {
    std::string name;
    DataType type;
	unsigned long long start;
	unsigned long long len;
};

class Column {
public:	
    Column(const std::string& name, const DataType& type) : 
	        _name(name), _type(type), _start(0), _len(0), _data_size(0) {}
    Column(const std::string& name, const DataType& type, unsigned long long start, unsigned long long len) : 
	        _name(name), _type(type), _start(start), _len(len), _data_size(0) {}
    Column(ColumnMeta& meta) : 
	        _name(meta.name), _type(meta.type), _start(meta.start), _len(meta.len), _data_size(0), _meta(meta) {}

	void set_datatype(DataType type) {
		_type = type;
	}
	DataType get_datatype() {
		return _type;
	}
    void parse_value(const std::string& in, std::string& val) {
		Util::parse_val_from_str(in, _type, val);
	}
    void push(const std::string& in) {
		std::string val;
	    parse_value(in, val);
		_values.push_back(val);
		_data_size += val.size();
	}
    void push_binary(const std::string& in) {
		_values.push_back(in);
		_data_size += in.size();
	}
	unsigned long long get_data_size() {
		return _data_size;
	}

	unsigned long long get_write_data_size() {
		// values split by '\0'
		if (_values.empty()) {
			return 0;
		}
		return get_data_size() + _values.size();
	}
	const std::string& get_col_name() {
		return _name;
	}

	const std::vector<std::string>& get_values() {
		return _values;
	}
	void set_start(unsigned long long start) {
		_start = start;
	}
	unsigned long long get_start() {
		return _start;
	}
	void set_len(unsigned long long len) {
		_len = len;
	}
	unsigned long long get_len() {
		return _len;
    }
	const ColumnMeta& get_meta() {
		return _meta;
	}
private:
    std::string _name;
    DataType _type;
	unsigned long long _start; // for binary parse
	unsigned long long _len; // for binary parse
	unsigned long long _data_size;
	ColumnMeta _meta;
    std::vector<std::string> _values;
};

class ColumnGroup {
public:
    void add_column(const std::string& col_name, const DataType& type) {
		add_column(col_name, type, 0, 0);
	}
    void add_column(const std::string& col_name, const DataType& type, unsigned long long start, unsigned long long len) {
        if (_cols.find(col_name) != _cols.end()) {
			Throw( "repeated col name:" + col_name);
		}
		Column* col = new Column(col_name, type, start, len);
		//_cols.push_back(col);
		_cols[col_name] = col;
	}
	void add_column(ColumnMeta& meta) {
        if (_cols.find(meta.name) != _cols.end()) {
			for (auto m : _cols) {
				std::cout << m.first << " ";
			}
			std::cout << std::endl;
			Throw("repeated col name:" + meta.name);
		}
	    Column* col = new Column(meta);
		_cols[meta.name] = col;
	
	}
	const std::map<std::string/*column name*/, Column*>& get_cols() {
		return _cols;
	}
	void print() {
		for (auto col : _cols) {
			std::cout << col.first << " : ";
			std::string line = col.first;
			line.append(" : ");
			for (auto val : col.second->get_values()) {
				if (!val.empty()) {
				switch (col.second->get_datatype()) {
					case Type_INT:
					    std::cout << (*(static_cast<int *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<int *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_FLOAT:
					    std::cout << (*(static_cast<float *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<float *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_SHORT:
					    std::cout << (*(static_cast<short *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<short *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_LONG:
					    std::cout << (*(static_cast<long *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<long *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_UL:
					    std::cout << (*(static_cast<unsigned long *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<unsigned long *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_LL:
					    std::cout << (*(static_cast<long long *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<long long *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_ULL:
					    std::cout << (*(static_cast<unsigned long long *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<unsigned long long *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_DOUBLE:
					    std::cout << (*(static_cast<double *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<double *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;
					case Type_LD:
					    std::cout << (*(static_cast<long double *>(static_cast<void *>(const_cast<char *>(val.c_str())))));
					    line.append(std::to_string(*(static_cast<long double *>(static_cast<void *>(const_cast<char *>(val.c_str()))))));
						break;

					case Type_STRING:
					    std::cout << val;
					    line.append(val);
						break;
				}
				}
				std::cout << ",";
				line.append(",");

			}
			std::cout << std::endl;
			//std::cout << line << std::endl;
		}
	}
private:
	std::map<std::string/*column name*/, Column*> _cols; 
	//std::vector<Column*> _cols;
};

class RTTBinary {
public:
    RTTBinary() {}
	void read_header(FileReader& reader) {
		std::string line;
		reader.readline(line);
		//std::cout << line << std::endl;
	}

	void add_column(const std::string& line) {
	    std::vector<std::string> items;
		Util::split(line, " ", items);
		if (items.size() < 4) {
			Throw( "illegal column meta line:" + line);
		}
		std::vector<std::string> pairs;
		pairs.reserve(2);
		ColumnMeta col_meta;
		for (auto item : items) {
			pairs.clear();
			Util::split(item, "=", pairs);
			if (pairs.size() != 2) {
				std::cout << "error:";
				std::cout << " line:" << line;
				std::cout << " item:" << item;
				std::cout << ":";
				for (auto i : pairs) {
					std::cout << i << " ";
				}
				std::cout << std::endl;
				Throw( "illegal column meta item, line:" + line + ", item:" + item);
			}
		    if (pairs[0] == "name") {
				col_meta.name = pairs[1];
			} else if (pairs[0] == "type") {
				DataType type = static_cast<DataType>(std::stoi(pairs[1]));
				if (type >= Type_UNKNOWN) {
					Throw( "parsing bianry meta: unknown type=" + pairs[1]);
				}
				col_meta.type = type;
			} else if (pairs[0] == "start") {
				col_meta.start = std::stoull(pairs[1]);
			} else if (pairs[0] == "len") {
				col_meta.len = std::stoull(pairs[1]);
			}
		}
	    _col_group.add_column(col_meta);
	}

	void read_meta(FileReader& reader) {
		std::string line;
		while (reader.readline(line) == RET_OK) {
			if (line.empty()) {
				//std::cout << "read meta line end" << std::endl;
				break;
			}
			//std::cout << line << std::endl;
			add_column(line);
		}
	}

	void parse_fixed_val_len(FileReader& reader, Column* col, unsigned long long data_zone_start, unsigned int val_size) {
        const ColumnMeta& meta = col->get_meta();
		if (meta.len == 0) {
			return;
		}
		if (RET_OK != reader.seekg(data_zone_start + meta.start)) {
			Throw( "read column " + meta.name + " seek error zonestart:" + std::to_string(data_zone_start)+",metastart:"+std::to_string(meta.start));
		}
		unsigned long long readed_len = 0;
		char buf[128] = {0};
		std::string val;
		while (readed_len < meta.len) {
			val.clear();
			if (RET_OK != reader.read(buf, 1)) {
				Throw( "read column " + meta.name + " error");
			}
			readed_len += 1;
			char NaN_mark = buf[0];
			if (NaN_mark == '0') {
				col->push_binary(val);
				continue;
			}
			if (readed_len + val_size > meta.len) {
				Throw( "read column " + meta.name + " overflow");
			}
			if (RET_OK != reader.read(buf, val_size)) {
				Throw( "read column " + meta.name + " error");
			}
			readed_len += val_size;

			val.assign(buf, val_size);
			col->push_binary(val);
		}
		if (readed_len != meta.len) {
			Throw( "read column " + meta.name + " read error, readed_len:" + 
			        std::to_string(readed_len) + ",meta_len=" + std::to_string(meta.len));
		}
	}

	void parse_str(FileReader& reader, Column* col, unsigned long long data_zone_start) {
        const ColumnMeta& meta = col->get_meta();
		if (meta.len == 0) {
			return;
		}
		if (RET_OK != reader.seekg(data_zone_start + meta.start)) {
			Throw( "read column " + meta.name + " seek error");
		}
		unsigned long long readed_len = 0;
		const unsigned int block_len = 1024;
		char buf[block_len + 1] = {0};
		buf[block_len] = '\0';
		std::string val;
		unsigned int real_readsize = 0;
		reader.read(buf, 1);
		readed_len++;
		while (readed_len < meta.len) {
			unsigned int remainsize = meta.len - readed_len;
			unsigned int need_readsize = remainsize > block_len ? block_len : remainsize;
			real_readsize = reader.read(buf, need_readsize) == RET_OK ? need_readsize : reader.gcount();
			readed_len += real_readsize;
			unsigned int start = 0;
			for (unsigned int i = 0; i < real_readsize; ++i) {
			    if (buf[i] == '\0') {
					val.append(buf + start, i - start);
					col->push(val);
					val.clear();
					start = i + 1;
				} 
			}
			if (start < real_readsize) {
				val.append(buf + start, real_readsize - start);
			}
		}
		col->push(val);
	}

    void read_column_data(FileReader& reader, Column* col, unsigned long long data_zone_start) {
        const ColumnMeta& meta = col->get_meta();
        //std::cout << "col_name:" << meta.name << ",type:" << meta.type << ",start:" << meta.start << ",len:" << meta.len << std::endl;
		switch(meta.type) {
			case Type_INT:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(int));
				break;
			case Type_FLOAT:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(float));
				break;
			case Type_SHORT:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(short));
				break;
			case Type_LONG:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(long));
				break;
			case Type_UL:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(unsigned long));
				break;
			case Type_LL:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(long long));
				break;
			case Type_ULL:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(unsigned long long));
				break;
			case Type_DOUBLE:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(double));
				break;
			case Type_LD:
			    parse_fixed_val_len(reader, col, data_zone_start, sizeof(long double));
				break;
			case Type_STRING:
			    parse_str(reader, col, data_zone_start);
				break;
			default:
			    Throw( "unknown type:" + std::to_string(meta.type));
		}
	}
	void read_data(FileReader& reader) {
        const std::map<std::string/*column name*/, Column*>& cols = _col_group.get_cols();
		unsigned long long data_zone_start = reader.tellg();
		//std::cout << "data_zone_start:" << data_zone_start << std::endl;
		for (auto col : cols) {
			read_column_data(reader, col.second, data_zone_start);
		}
	}
	void read(const std::string& binary_file) {
        FileReader reader(binary_file);
		read_header(reader);
		read_meta(reader);
		read_data(reader);
	}

    void print() {
		_col_group.print();
	}
private:
	ColumnGroup _col_group;
};

class CSV2BinaryConvertor{
public:
	CSV2BinaryConvertor(const std::string& csv_file, const std::string& col_des_file, const std::string& binary_file) : 
	        _csv_reader(csv_file),_col_des_reader(col_des_file),_binary_file(binary_file) {}

	void build_cols_dict() {
		std::string line;
		//std::cout << "create column" << std::endl;
		while (_col_des_reader.readline(line) == RET_OK) {
			//std::cout << "line:" << line << std::endl;
			if (line.empty() || line[0] == '#') {
				continue;
			}
			std::vector<std::string> val;
			Util::split(line, ":", val);
			if (val.size() != 2 || val[0].empty() || val[1].empty()) {
				printf("error line:%s", line.c_str());
				Throw( "error line in dict:" + line);
			}
			DataType data_type = static_cast<DataType>(std::stoi(val[1], nullptr));
			if (data_type >= Type_UNKNOWN) {
				Throw( "unkonw type for [" + line + "]");
			}
			if (_col_datatype_map.find(val[0]) != _col_datatype_map.end()) {
			    Throw( "repeated col:" + val[0]);	
			}
			_col_datatype_map[val[0]] = data_type;
		}
	}

	void parse_header() {
		std::string line;
	    std::vector<std::string> str_vals;

        // parse header
		int ret = _csv_reader.readline(line); 
		if (ret != RET_OK) {
			Throw( "read csv header error");
		}
		//std::cout << "header:" << line << std::endl;
		Util::split(line, ",", str_vals);
		if (str_vals.empty()) {
			Throw( "empty header");
		}
		if (str_vals.size() != _col_datatype_map.size()) {
			Throw( "csv header col size is not equal to dict col size");
		}
		for (unsigned int i = 0; i < str_vals.size(); ++i) {
			//std::cout << str_vals[i] << std::endl;
			if (_col_datatype_map.find(str_vals[i]) == _col_datatype_map.end()) {
				std::cout <<  "csv col[" + str_vals[i] + "] cannot be found in dict col" << std::endl;
				Throw( "csv col[" + str_vals[i] + "] cannot be found in dict col");
			}
			Column* col =  new Column(str_vals[i], _col_datatype_map[str_vals[i]]);
			_cols.push_back(col);
		}
	}

	void parse() {
		parse_header();

		std::string line;
	    std::vector<std::string> str_vals;
		//std::cout << "parse" << std::endl;
		while (_csv_reader.readline(line) == RET_OK) {
			//std::cout << line << std::endl;
			str_vals.clear();
			str_vals.reserve(_cols.size());
			Util::split(line, ",", str_vals);
			if (str_vals.size() != _cols.size()) {
				Throw( "col size error line: " + line);
			}
	        for (unsigned int i = 0; i < str_vals.size(); ++i) {
				_cols[i]->push(str_vals[i]);
			}	
		}
		
	}
    ~CSV2BinaryConvertor() {
		for (unsigned int i = 0; i < _cols.size(); ++i) {
	        delete _cols[i];		
		}
	}

    void write_binaryfile_header(FileWriter& fwriter) {
		const std::string header = "RTT_BINARY HEADER";
		fwriter.writeline(header);
	}
	void write_binaryfile_meta(FileWriter& fwriter) {
		unsigned long long start = 0;
		for (unsigned int i = 0; i < _cols.size(); ++i) {
			std::string line;
			line.append("name=");
			line.append(_cols[i]->get_col_name());

			line.append(" type=");
			line.append(std::to_string(_cols[i]->get_datatype()));

			line.append(" start=");
			line.append(std::to_string(start));

			unsigned long long data_size = _cols[i]->get_write_data_size();
			line.append(" len=");
			line.append(std::to_string(data_size));

			start += data_size;
			fwriter.writeline(line);
		}
		fwriter.write_char('\n');
	}
	void write_binaryfile_data_with_fixed_val_len(FileWriter& fwriter, Column* col) {
		auto vals = col->get_values();
		for (unsigned int j = 0; j < vals.size(); ++j) {
			char NaN_mark = vals[j].empty() ? '0' : '1';
			fwriter.write_char(NaN_mark);
			fwriter.write(vals[j].c_str(), vals[j].size());
		}

	}
	void write_binaryfile_data_with_string(FileWriter& fwriter, Column* col) {
		auto vals = col->get_values();
		for (unsigned int j = 0; j < vals.size(); ++j) {
			// value splitted by '\0'
			if (j != 0) {
			    fwriter.write_char('\0');
			}
			fwriter.write(vals[j].c_str(), vals[j].size());
		}

	}

	void write_binaryfile_data(FileWriter& fwriter) {
        for (unsigned int i = 0; i < _cols.size(); ++i) {
			auto vals = _cols[i]->get_values();
			for (unsigned int j = 0; j < vals.size(); ++j) {
                char NaN_mark = '\0';
				if (_cols[i]->get_datatype() >= Type_SHORT &&  _cols[i]->get_datatype() <= Type_LD) {
				    NaN_mark = vals[j].empty() ? '0' : '1';
				}
				fwriter.write_char(NaN_mark);
				fwriter.write(vals[j].c_str(), vals[j].size());
				//std::cout << vals[j] << std::endl;
			}
		}
	}

	void to_binary() {
        FileWriter fwriter(_binary_file);
        write_binaryfile_header(fwriter);
		write_binaryfile_meta(fwriter);
		write_binaryfile_data(fwriter);
	}
	void convert() {
		build_cols_dict();
        parse();
		to_binary();
	}

private:
	FileReader _csv_reader;
	FileReader _col_des_reader;
	std::string _binary_file;
	std::vector<Column*> _cols;
	std::map<std::string, DataType> _col_datatype_map;
	//std::map<int, std::vector<Column<std::string> > > _str_values;
	//std::map<int, std::vector<Column<float> > > _float_values;
	//std::map<int, std::vector<Column<int> > > _int_values;
};

class CSV2BinaryRowConvertor {
public:
    void build_cols_dict(FileReader& reader) {
		std::string line;
		//std::cout << "create column" << std::endl;
		while (reader.readline(line) == RET_OK) {
			//std::cout << "line:" << line << std::endl;
			if (line.empty() || line[0] == '#') {
				continue;
			}
			std::vector<std::string> val;
			Util::split(line, ":", val);
			if (val.size() != 2 || val[0].empty() || val[1].empty()) {
				printf("error line:%s", line.c_str());
				Throw( "error line in dict:" + line);
			}
			DataType data_type = static_cast<DataType>(std::stoi(val[1], nullptr));
			if (data_type >= Type_UNKNOWN) {
				Throw( "unkonw type for [" + line + "]");
			}
			if (_col_datatype_map.find(val[0]) != _col_datatype_map.end()) {
			    Throw( "repeated col:" + val[0]);	
			}
			_col_datatype_map[val[0]] = data_type;
		}
	}
    void parse_header(FileReader& reader) {
		std::string line;
	    std::vector<std::string> str_vals;

        // parse header
		int ret = reader.readline(line); 
		if (ret != RET_OK) {
			Throw( "read csv header error");
		}
		//std::cout << "header:" << line << std::endl;
		Util::split(line, ",", str_vals);
		if (str_vals.empty()) {
			Throw( "empty header");
		}
		if (str_vals.size() != _col_datatype_map.size()) {
			Throw( "csv header col size is not equal to dict col size");
		}
		for (unsigned int i = 0; i < str_vals.size(); ++i) {
			//std::cout << str_vals[i] << std::endl;
			if (_col_datatype_map.find(str_vals[i]) == _col_datatype_map.end()) {
				std::cout <<  "csv col[" + str_vals[i] + "] cannot be found in dict col" << std::endl;
				Throw( "csv col[" + str_vals[i] + "] cannot be found in dict col");
			}
			_datatype_seq.push_back(_col_datatype_map[str_vals[i]]);
		}
        _header_col_name = line;
	}

    void parse_line(const std::string& line, std::vector<std::string>& vals) {
        std::vector<std::string> cols;
        Util::split(line, ",", cols);
        if (cols.size() != _datatype_seq.size()) {
            std::cout << "cols size=" << cols.size() << ", " << _datatype_seq.size() << std::endl;
            std::cout << line << std::endl;
            Throw("col size is not equal to header col size");
        }
        for (unsigned int i = 0; i < cols.size(); ++i) {
            std::string val;
            Util::parse_val_from_str(cols[i], _datatype_seq[i], val);
            vals.push_back(val);
        }
    }

    int readline(FileReader& reader) {
        std::string line;
        while (reader.readline(line) == RET_OK) {

        }
    }

    void write_binary_line(FileWriter& writer, const std::vector<std::string>& vals) {
        if (vals.size() != _datatype_seq.size()) {
            Throw("col val size is not equal to header col size");
        }
        for (unsigned int i = 0; i < vals.size(); ++i) {
            char mark = '\0';
            if (_datatype_seq[i] >= Type_SHORT && _datatype_seq[i] <= Type_LD) {
                mark = '0' + vals[i].size();
            }
            writer.write_char(mark);
            writer.write(vals[i].c_str(), vals[i].size());
            if (_datatype_seq[i] == Type_STRING) {
                writer.write_char('\0');
            }
        }
    }

    void write_header(FileWriter& writer) {
        writer.writeline(_header_col_name);
        std::string type_line;
        for (auto it = _datatype_seq.begin(); it != _datatype_seq.end(); ++it) {
            type_line.append(std::to_string(_datatype_seq[*it]));
            type_line.append(",");
        }
        type_line.pop_back();
        writer.writeline(type_line);
    }

    void convert(const std::string& csv_file, const std::string& dict_file, const std::string& binary_file) {
        FileReader dict_reader(dict_file);
        build_cols_dict(dict_reader);

        FileReader csv_reader(csv_file);
        FileWriter binary_writer(binary_file);

        parse_header(csv_reader);

        write_header(binary_writer);

        std::vector<std::string> vals;
        vals.reserve(_datatype_seq.size());
        std::string line;
        while (csv_reader.readline(line) == RET_OK) {
            parse_line(line, vals);
            write_binary_line(binary_writer, vals);
            vals.clear();
            line.clear();
        }
    }

private:
	std::map<std::string, DataType> _col_datatype_map;
    std::vector<DataType> _datatype_seq;
    std::string _header_col_name;
};

class ColValue {
public:
    ColValue(DataType type, const std::string& binary_val) : _type(type), _binary_val(binary_val) {}
    template <class T>
    int get_val(T val) {
	    val = (*(static_cast<T *>(static_cast<void *>(const_cast<char *>(_binary_val.c_str())))));
    }
private:
    DataType _type;
    std::string _binary_val;
};

class RowBinaryColMeta {
public:
    std::string _col_name;
    int _type;
};

class RTTRowBianryReader {
public:
    void read_header() {
        std::string line;
        char * buf = 0;
        int buf_len = 0;
        _reader.readline(buf, buf_len);
        line.assign(buf, buf_len);
        std::vector<std::string> arr;
        Util::split(line, ",", arr);
        if (arr.size() == 0) {
            Throw("empty header, line:" + line);
        }
        RowBinaryColMeta col_meta;
        _col_metas.reserve(arr.size());
        for (auto it = arr.begin(); it != arr.end(); ++it) {
            col_meta._col_name = *it;
            _col_metas.push_back(col_meta);
        }
        _reader.readline(buf, buf_len);
        line.assign(buf, buf_len);
        arr.clear();
        Util::split(line, ",", arr);
        if (arr.size() != _col_metas.size()) {
            Throw("meta size is not equal");
        }
        for (unsigned int i = 0; i < arr.size(); ++i) {
            _col_metas[i]._type = std::stoi(arr[i]);
        }
    }

    int init(const std::string& binary_file) {
        return _reader.init(binary_file);
    }

    int read_row(std::vector<std::string>& vals) {
        int read_col_num = 0;
        std::string val;
        while (read_col_num < _col_metas.size()) {
            val.clear();
            if (_reader.read_col(val) != RET_OK) {
                break;
            }
            vals.push_back(val);
            read_col_num++;

        }
        if (read_col_num == 0) {
            return RET_READEND;
        }
        if (read_col_num != _col_metas.size()) {
            Throw("read col num not enough");
        }
        return RET_OK;
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

    template <class T> void get_value(std::string& bin_str, T * val) {
	    val = (static_cast<T *>(static_cast<void *>(const_cast<char *>(bin_str.c_str()))));
    } 

    
private:
    std::vector<RowBinaryColMeta> _col_metas;
    BinaryMMapReader _reader;
};

template <>
void RTTRowBianryReader::get_value(std::string& bin_str, std::string* val) {
    val = &bin_str;
}

} // namespace

void test_csv() {
        std::time_t start = RTTBinaryDict::Util::getTimeStamp();
    RTTBinaryDict::CSV2BinaryConvertor convertor("rtt.large.csv3", "rtt.dict", "rtt.large.binary3");
	convertor.convert();
        std::time_t end = RTTBinaryDict::Util::getTimeStamp();
        std::cout << "timecost:" << end - start << std::endl;
}

void test_binary() {
	RTTBinaryDict::RTTBinary binary;
        std::time_t start = RTTBinaryDict::Util::getTimeStamp();
	binary.read("rtt.large.binary3");
        std::time_t end = RTTBinaryDict::Util::getTimeStamp();
        std::cout << "timecost:" << end - start << std::endl;
    //binary.print();    
}

void test_csv_row() {
    RTTBinaryDict::CSV2BinaryRowConvertor convertor;
    //convertor.convert("rtt.large.csv3", "rtt.dict", "rtt.large.binary3");
    convertor.convert("rtt.csv", "rtt.dict", "rtt.binary");

}

void test_read_row_binary() {
    RTTBinaryDict::RTTRowBianryReader reader;
    reader.init("rtt.binary");
    reader.read_header();
    std::vector<std::string> vals;
    while (reader.read_row(vals) == RTTBinaryDict::RET_OK) {

    }
}
int main() {
	try {
	    //test_csv();
	    //test_binary();
        //test_csv_row();
        test_read_row_binary();
	} catch (RTTBinaryDict::RTTException& e) {
		std::cout << e.info() << std::endl;
	}
}
