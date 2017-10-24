 #include "rtt_binary.h"
 #include <sys/mman.h>
 #include <fcntl.h>
 #include <sys/stat.h>
 #include <openssl/rsa.h>
 #include <openssl/err.h>
 #include <openssl/pem.h>
 #include <cstring>

 namespace RTTBinaryDict {

 char prikey_pem[] = "-----BEGIN RSA PRIVATE KEY-----\n"
 "MIICXQIBAAKBgQDco3haZDZCxhFGqdpJuyajpXbqON8R5U8yAm7Qvv03bDb/S84A\n"
 "WTQVfI1aliJKel6MllYyDuoSxpKi/CLdLXebGpiSgcE8X+eUinc5GCN9FXAbKnBb\n"
 "L4BaYyS5tvw0Ai/j8TfFmVUo6xC1rQ0zpWd2MuPfwsEfeOTB27zt+cRm9QIDAQAB\n"
 "AoGAEtbyg+VirLj06K/AL+OHHRoX2VAZ3BFUfdSvWau1O3JGD+6NHIKBbARCnaWM\n"
 "MAfa4u5DVeroGcpS4w/cej5TpAY5y9srMFsMiJFnS8u1U4LQDsVL1vGeRzIZoXlB\n"
 "oVFYI/U1HKpTIt3jTHMurHZl3Q5OEykRITsEm+tJf1xMY4ECQQD1VV3pjYk/rxXg\n"
 "mlEAkfMiWRx7Ff0cjoO9OI2KT3WwVVoFlwbZ3E14ajOnCWHZI2bCOVMIYlV9QBRt\n"
 "LwZUaCk5AkEA5js94f1fw5aRbDPFXrMPtROg7unRp9dEm0V9eNa2f4ivAVrCEUbY\n"
 "1tQl3fsNZyZw9wTg8RIDEYSFLeURpqcXnQJBANrL14WDhPQW4hv9hGBNydjIQG5F\n"
 "ngbp0vPei9zeIMeyVybFGocRwsWxcX93DpzoxaxSE4tWp4ecrprxZWPBwYECQQCa\n"
 "RRQAPBFRM7EZ+c7E1+MsiIyLym1Ls/kqufOLZwQ+jM4HcFMd1IUz3k/JYJHojl+f\n"
 "hctcfZ9Eu7GpwRaEvu4ZAkAAvvz9U2DyDppmff2nf1KuQsQWuvsg/KyoV5eKREzw\n"
 "FV593oGRxug0Gc8+v82JuipKnKMbWt8s1p8ZyIPSYf2P\n"
 "-----END RSA PRIVATE KEY-----\n";

 char pubkey_pem[] = "-----BEGIN PUBLIC KEY-----\n"
 "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDco3haZDZCxhFGqdpJuyajpXbq\n"
 "ON8R5U8yAm7Qvv03bDb/S84AWTQVfI1aliJKel6MllYyDuoSxpKi/CLdLXebGpiS\n"
 "gcE8X+eUinc5GCN9FXAbKnBbL4BaYyS5tvw0Ai/j8TfFmVUo6xC1rQ0zpWd2MuPf\n"
 "wsEfeOTB27zt+cRm9QIDAQAB\n"
 "-----END PUBLIC KEY-----\n";

 GZFileReader::GZFileReader(const std::string& fname) {
     _gf = gzopen(fname.c_str(), "rb");
     if (_gf == NULL) {
         std::cout << "reader gz open error" << std::endl;
         Throw("reader gz open failed");
     }
 }

 GZFileReader::~GZFileReader() {
     gzclose(_gf);
 }

 int GZFileReader::readline(std::string& line) {
     char c;
     while (read_char(c) && c != '\n') {
         line.push_back(c);
     }
     if (!line.empty() && line[line.size() - 1] == '\r') {
         line.pop_back();
     }
     //std::cout << line<<std::endl;

     return RET_OK;
 }

 int GZFileReader::read(std::string& buf, int size, bool is_scan) {
     char c;
     int len = 0;
     while (len < size && read_char(c)) {
         if (!is_scan) {
             buf.push_back(c);
         }
         ++len;
     }

     return len;
 }

 int GZFileReader::read_col(std::string& col, bool is_scan) {
     char mark;
     if (!read_char(mark)) {
         return RET_READERROR;
     }
     if (mark == '\0') {
         char c;
         while (read_char(c) && c != '\0') {
             if (!is_scan) {
                 col.push_back(c);
             }
         }
         //std::cout << "read col,  real:"<< col<< std::endl;
     } else {
         int readn = mark - '0';
         int ret = read(col, readn, is_scan);
         //std::cout << "read col,  real:"<<ret<<" exp:"<< readn << std::endl;
         if (ret != readn) {
             Throw("read col failed");
         }
     }

     return RET_OK;
 }

 int GZFileReader::gz_read(int start, int size) {
     int readn = gzread(_gf, _buf + start, size);
     if (readn > 0) {
         _end += readn;
     }
     return readn;
 }

 bool GZFileReader::read_char(char& c) {
     if (_cur == _end) {
         int pos = _cur % GZREAD_BUF_SIZE;
         int readn = GZREAD_BUF_SIZE - pos;

         int real_readn = gz_read(pos, readn);
         if (real_readn <= 0) {
             //std::cout << "read end" << std::endl;
             return false;
         }
     } else if (_cur > _end) {
         std::cout << "read char error" << std::endl;
         Throw("read char error");
     }

    c = _buf[_cur++ % GZREAD_BUF_SIZE];

     return true;
 }



 BinaryMMapReader::~BinaryMMapReader() {
     munmap(_buf, _file_size);
     close(fd);
 }

 BinaryMMapReader::BinaryMMapReader(const std::string& file) {
     struct stat st;
     if (stat(file.c_str(), &st) == -1) {
         Throw("failed to get file stat, " + file);
     }
     fd = open(file.c_str(), O_RDONLY);
     if (fd == -1) {
         Throw("failed to open file " + file);
     }
     _file_size = st.st_size;
     _buf = static_cast<char *>(mmap(NULL, _file_size, PROT_READ, MAP_PRIVATE, fd, 0));
     if (_buf == MAP_FAILED || _buf == NULL) {
         Throw("failed to mmap");
     }
 }

 int BinaryMMapReader::readline(std::string& line) {
     char* buf = NULL;
     int len = 0;
     int ret = readline(buf, len);
     if (ret == RET_OK) {
         line.assign(buf, len);
     }
     return ret;
 }

 int BinaryMMapReader::readline(char* &buf, int& len) {
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

 int BinaryMMapReader::read(char*& buf, int size) {
     unsigned long long pos = _cur;
     buf = _buf + _cur;
     int len = 0;
     while (pos < _file_size && pos - _cur < size) {
         ++pos;
     }
     len = pos - _cur;
     _cur = pos;

     return len;
 }

 int BinaryMMapReader::read_col(std::string& val, bool is_scan) {
     char * buf = 0;
     int len = 0;
     int ret = read_col(buf, len);
     if (ret == RET_OK && !is_scan) {
         val.assign(buf, len);
     }
     return ret;
 }

 int BinaryMMapReader::read_col(char*& buf, int& len) {
     if (_cur >= _file_size) {
         return RET_READERROR;
     }
     unsigned int read_len = 0;
     char mark = _buf[_cur++];
     unsigned long long pos = _cur;
     if (mark == '\0') {
         while (pos < _file_size && _buf[pos] != '\0') {
             ++pos;
         }
         read_len = pos - _cur;

         ++pos;
     } else {
         read_len = mark - '0';
         pos += read_len;
     }
     if (read_len + _cur > _file_size) {
         std::cout << read_len + _cur << std::endl;
         Throw("read overflow");
     }
     buf = _buf + _cur;
     len = read_len;
     //val.assign(_buf + _cur, read_len);
     _cur = pos;
     //std::cout << "read_len:" << read_len << " mark:" << mark  << std::endl;
     return RET_OK;
 }


 void Util::encode_str(const std::string& str, const std::string& outfile) {
     FileWriter writer(outfile);
     std::string en_str = encode_with_rsa_pubkey("", str);
     writer.write(en_str.c_str(), en_str.size());
 }

 std::string Util::decode_str(const std::string& file) {
     BinaryMMapReader reader(file);
     char* buf = reader.get_buf();
     std::string ret;
     ret.assign(buf, reader.get_file_size());
     return decode_with_rsa_prikey("", ret);
 }

 std::string Util::encode_with_rsa_pubkey( const std::string& strPemFileName, const std::string& strData )
 {
     if (strData.empty())
     {
         return "";
     }

     std::string strRet;
     RSA* pRSAPublicKey = NULL;

     if (!strPemFileName.empty()) {
         FILE* hPubKeyFile = fopen(strPemFileName.c_str(), "rb");
         if( hPubKeyFile == NULL )
         {
             return "";
         }

         pRSAPublicKey = RSA_new();
         if(PEM_read_RSA_PUBKEY(hPubKeyFile, &pRSAPublicKey, 0, 0) == NULL)
         {
             fclose(hPubKeyFile);
             return "";
         }
         fclose(hPubKeyFile);
     } else {
         BIO *mem = NULL;
         mem = BIO_new_mem_buf(pubkey_pem, strlen(pubkey_pem));
         if (mem == NULL) {
             char buffer[120];
             ERR_error_string(ERR_get_error(), buffer);
             fprintf(stderr, "openssl error:", buffer);
             return "";
         }
         pRSAPublicKey = PEM_read_bio_RSA_PUBKEY(mem, NULL, NULL, NULL);
         BIO_free(mem);

     }
     if (pRSAPublicKey == NULL) {
         char buffer[120];
         ERR_error_string(ERR_get_error(), buffer);
         fprintf(stderr, "openssl error:", buffer);
         return "";
     }
     int nLen = RSA_size(pRSAPublicKey);
     char* pEncode = new char[nLen + 1];
     int ret = RSA_public_encrypt(strData.length(), (const unsigned char*)strData.c_str(), (unsigned char*)pEncode, pRSAPublicKey, RSA_PKCS1_PADDING);
     if (ret >= 0)
     {
         strRet = std::string(pEncode, ret);
     }
     delete[] pEncode;
     RSA_free(pRSAPublicKey);
     CRYPTO_cleanup_all_ex_data();
     return strRet;
 }


 //解密
 std::string Util::decode_with_rsa_prikey( const std::string& strPemFileName, const std::string& strData )
 {
     if (strData.empty())
     {
         return "";
     }
     RSA* pRSAPriKey = NULL;
     std::string strRet;

     if (!strPemFileName.empty()) {
         pRSAPriKey = RSA_new();
         FILE* hPriKeyFile = fopen(strPemFileName.c_str(),"rb");
         if( hPriKeyFile == NULL )
         {
                 return "";
         }
         if(PEM_read_RSAPrivateKey(hPriKeyFile, &pRSAPriKey, 0, 0) == NULL)
         {
                 fclose(hPriKeyFile);
                 return "";
         }
         fclose(hPriKeyFile);
     } else {
         BIO *mem = NULL;
         mem = BIO_new_mem_buf(prikey_pem, strlen(prikey_pem));
         if (mem == NULL) {
             char buffer[120];
             ERR_error_string(ERR_get_error(), buffer);
             fprintf(stderr, "openssl error:", buffer);
             return "";
         }
         pRSAPriKey = PEM_read_bio_RSAPrivateKey(mem, NULL, NULL, NULL);
         BIO_free(mem);
     }
     if (pRSAPriKey == NULL) {
         char buffer[120];
         ERR_error_string(ERR_get_error(), buffer);
         fprintf(stderr, "openssl error:", buffer);
         return "";
     }

     int nLen = RSA_size(pRSAPriKey);
     char* pDecode = new char[nLen+1];

     int ret = RSA_private_decrypt(strData.length(), (const unsigned char*)strData.c_str(), (unsigned char*)pDecode, pRSAPriKey, RSA_PKCS1_PADDING);
     if(ret >= 0)
     {
         strRet = std::string((char*)pDecode, ret);
     }
     delete [] pDecode;
     RSA_free(pRSAPriKey);
     CRYPTO_cleanup_all_ex_data();
     return strRet;
 }

 void Util::split(const std::string& src, const std::string& separator, std::vector<std::string>& dest) {
     //dest.clear();
     using namespace std;
     if (src.empty()) {
         return;
     }
     string str = src;
     string substring;
     string::size_type start = 0, index;

     do {
         index = str.find_first_of(separator,start);
         if (index != string::npos) {
             substring = str.substr(start,index-start);
             dest.push_back(trim(substring));
             start = index + separator.size();
             //start = str.find_first_not_of(separator,index);
             if (start == string::npos) return;
         }
     } while (index != string::npos);

     //the last token
     substring = str.substr(start);
     dest.push_back(trim(substring));
 }

 std::string& Util::trim(std::string &s) {
     if (s.empty()) {
         return s;
     }
     s.erase(0,s.find_first_not_of(" "));
     s.erase(s.find_last_not_of(" ") + 1);
     return s;
 }

 DataType Util::get_datatype(const std::string& in) {
     if (in.empty()) {
         return Type_END;
     }
     bool has_dot = false;
     bool has_number = false;
     bool has_other = false;
     for (unsigned int i = 0; i < in.size(); ++i) {
         //if ((in[i] >= 'a' && in[i] =< "z") || (in[i] >= 'A' && in[i] =< 'Z')) {
         //  has_char = true;
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
         return Type_INT32;
     }
 }

 void Util::parse_val_from_str(const std::string& str, const int type, std::string& val) {
     if (str.empty()) {
         return;
     }
     switch (type) {
         case Type_INT16:
         {
             int16_t v = static_cast<int16_t>(std::stoi(str));
             val.assign((char*)&v, sizeof(int16_t));
             break;
         }
         case Type_INT32:
         {
             int32_t v = (std::stoi(str));
             val.assign((char*)&v, sizeof(int32_t));
             break;
         }
         case Type_INT64:
         {
             int64_t v = std::stol(str);
             val.assign((char*)&v, sizeof(int64_t));
             break;
         }
         case Type_UINT16:
         {
             uint16_t v = static_cast<uint16_t>(std::stoul(str));
             val.assign((char*)&v, sizeof(uint16_t));
             break;
         }
         case Type_UINT32:
         {
             uint32_t v = static_cast<uint32_t>(std::stoul(str));
             val.assign((char*)&v, sizeof(uint32_t));
             break;
         }
         case Type_UINT64:
         {
             uint64_t v = static_cast<uint64_t>(std::stoul(str));
             val.assign((char*)&v, sizeof(uint64_t));
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

 std::time_t Util::getTimeStamp()
 {
     std::chrono::time_point<std::chrono::system_clock,std::chrono::milliseconds> tp =
         std::chrono::time_point_cast<std::chrono::milliseconds>(std::chrono::system_clock::now());
     auto tmp=std::chrono::duration_cast<std::chrono::milliseconds>(tp.time_since_epoch());
     std::time_t timestamp=tmp.count();
     //std::time_t timestamp=std::chrono::system_clock::to_time_t(tp);
     return timestamp;
 }

 bool Util::is_gzfile(const std::string& fname) {
     if ((fname.size() > 3) &&
             (fname.substr(fname.size() - 3) == ".gz")) {
         return true;
     } else {
         return false;
     }
 }

 // writer

 void RTTBinaryRowWriter::build_cols_dict(FileReader& reader) {
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
         if (data_type <= Type_START || data_type >= Type_END) {
             Throw( "unkonw type for [" + line + "]");
         }
         if (_col_datatype_map.find(val[0]) != _col_datatype_map.end()) {
             Throw( "repeated col:" + val[0]);
         }
         _col_datatype_map[val[0]] = data_type;
     }
 }

 void RTTBinaryRowWriter::convert(const std::string& csv_file, const std::string& dict_file, const std::string split) {
     FileReader dict_reader(dict_file);
     build_cols_dict(dict_reader);

     FileReader csv_reader(csv_file);
     //FileWriter binary_writer(binary_file);

     parse_csv_header(csv_reader, split);

     write_header(_writer);

     std::vector<std::string> vals;
     vals.reserve(_col_metas.size());
     std::string line;
     while (csv_reader.readline(line) == RET_OK) {
         parse_line(line, vals, split);
         if (RET_OK != write_binary_line(_writer, vals)) {
             std::cout << "write error line:" << line << std::endl;
         }
         vals.clear();
         line.clear();
     }
 }


 void RTTBinaryRowWriter::parse_csv_header(FileReader& reader, const std::string& split) {
     std::string line;
     std::vector<std::string> str_vals;

     // parse header
     int ret = reader.readline(line);
     if (ret != RET_OK) {
         Throw( "read csv header error");
     }
     //std::cout << "header:" << line << std::endl;
     Util::split(line, split, str_vals);
     if (str_vals.empty()) {
         Throw( "empty header");
     }
     if (str_vals.size() != _col_datatype_map.size()) {
         Throw( "csv header col size is not equal to dict col size");
     }
     RowBinaryColMeta col_meta;
     for (unsigned int i = 0; i < str_vals.size(); ++i) {
         //std::cout << str_vals[i] << std::endl;
         if (_col_datatype_map.find(str_vals[i]) == _col_datatype_map.end()) {
             Throw( "csv col[" + str_vals[i] + "] cannot be found in dict col");
         }

         push_col_meta(str_vals[i], _col_datatype_map[str_vals[i]]);
     }
 }

 void RTTBinaryRowWriter::parse_line(const std::string& line, std::vector<std::string>& vals, const std::string& split) {
     std::vector<std::string> cols;
     Util::split(line, split, cols);
     if (cols.size() != _col_metas.size()) {
         std::cout << "cols size=" << cols.size() << ", " << _col_metas.size() << std::endl;
         std::cout << line << std::endl;
         Throw("col size is not equal to header col size");
     }
    for (unsigned int i = 0; i < cols.size(); ++i) {
         std::string val;
         Util::parse_val_from_str(cols[i], _col_metas[i]._type, val);
         vals.push_back(val);
     }
 }

 int RTTBinaryRowWriter::write_binary_line(IRTTFileWriter* writer, const std::vector<std::string>& vals) {
     if (vals.size() != _col_metas.size()) {
         //Throw("col val size is not equal to header col size");
         std::cout << "col val size is not equal to header col size" << std::endl;
         return RET_ERROR;

     }
     for (unsigned int i = 0; i < vals.size(); ++i) {
         char mark = '\0';
         if (_col_metas[i]._type >= Type_INT16 && _col_metas[i]._type <= Type_LD) {
             mark = '0' + vals[i].size();
         }
         writer->write_char(mark);
         writer->write(vals[i].c_str(), vals[i].size());
         if (_col_metas[i]._type == Type_STRING) {
             writer->write_char('\0');
         }
     }
     return RET_OK;
 }

 void RTTBinaryRowWriter::write_header(IRTTFileWriter* writer) {
     std::string type_line;
     std::string name_line;
     for (auto it = _col_metas.begin(); it != _col_metas.end(); ++it) {
         type_line.append(std::to_string(it->_type));
         type_line.append(",");
         name_line.append(it->_col_name);
         name_line.append(",");
     }
     type_line.pop_back();
     name_line.pop_back();

     writer->writeline(name_line);
     writer->writeline(type_line);
 }

 template <> int RTTBinaryRowWriter::get_str_from_val(const std::string& val, std::string& str) {
     str = val;
     return RET_OK;
 }
 template <> int RTTBinaryRowWriter::get_str_from_val(const EmptyValue& val, std::string& str) {
     str.clear();
     return RET_OK;
 }

 // reader

 int RTTBinaryRowReader::init() {
     int all_col_num = 0;
     try {
         read_header();
         std::string col;
         // scan col
         while(_reader->read_col(col, true) == RET_OK) {
             ++all_col_num;
         }
     } catch (RTTException& e) {
         std::cout << e.info() << std::endl;
         return RET_ERROR;
     }
     int col_num = get_col_size();
     if (all_col_num % col_num != 0) {
         std::cout << "data error" << std::endl;
         return RET_ERROR;
     }
     _row_size = all_col_num / col_num;
     _reader->set_cur(_reader->get_data_start());
     return RET_OK;
 }

 void RTTBinaryRowReader::read_header() {
     std::string line;
     char * buf = 0;
     int buf_len = 0;

     // read column name
     //_reader.readline(buf, buf_len);
     //line.assign(buf, buf_len);
     _reader->readline(line);
     //std::cout << line << std::endl;
     std::vector<std::string> arr;
     Util::split(line, _split, arr);
     if (arr.size() == 0) {
         Throw("empty header, line:" + line);
     }
     _col_size = arr.size();
     RowBinaryColMeta col_meta;
     _col_metas.reserve(arr.size());
     //for (auto it = arr.begin(); it != arr.end(); ++it) {
     for (unsigned int i = 0; i < arr.size(); ++i) {
          if (_filter_cols.empty() || _filter_cols.find(arr[i]) != _filter_cols.end()) {
             col_meta._col_name = arr[i];
             _col_metas.push_back(col_meta);

             //std::cout << arr[i] << std::endl;
             _filter_col_ids.insert(i);
         }
     }

     // read column data type
     //_reader.readline(buf, buf_len);
     //line.assign(buf, buf_len);
     line.clear();
     _reader->readline(line);
     //std::cout << line << std::endl;
     arr.clear();
     Util::split(line, _split, arr);
     if (arr.size() != _col_size) {
         Throw("meta size is not equal");
     }
     int j = 0;
     for (unsigned int i = 0; i < arr.size(); ++i) {
         if (arr[i].size() == 0) {
             Throw("data type is empty");
         }
         if (_filter_col_ids.find(i) != _filter_col_ids.end()) {
             int type = std::stoi(arr[i]);
             if (type <= Type_START || type >= Type_END) {
                 Throw("illegal data type " + arr[i]);
             }
             _col_metas[j++]._type = std::stoi(arr[i]);
         }
     }

     _reader->set_data_start(_reader->get_cur());
 }

 int RTTBinaryRowReader::read_row(std::vector<std::string>& vals) {
     int read_col_num = 0;
     std::string val;
     while (read_col_num < _col_size) {

         val.clear();
         if (_reader->read_col(val) != RET_OK) {
             break;
         }
         if (_filter_col_ids.empty() ||  _filter_col_ids.find(read_col_num) != _filter_col_ids.end()) {
             //std::cout << read_col_num << std::endl;
             vals.push_back(val);
         }
         ++read_col_num;
     }
     if (read_col_num == 0) {
         //std::cout << "no read" << std::endl;
         return RET_READEND;
     }
     if (read_col_num != _col_size) {
         Throw("read col num not enough");
     }
     return RET_OK;
 }

 template <>
 void RTTBinaryRowReader::get_value(std::string& bin_str, std::string* val) {
     *val = bin_str;
     //std::cout << "[" << bin_str << "]" << std::endl;
 }

 } // namespace RTTBinaryDict


