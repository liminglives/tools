#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <string>
#include <fstream>
#include <vector>
#include <chrono>

std::time_t getTimeStamp2() {
    std::chrono::time_point<std::chrono::system_clock,std::chrono::milliseconds> tp =
        std::chrono::time_point_cast<std::chrono::milliseconds>(std::chrono::system_clock::now());
    auto tmp=std::chrono::duration_cast<std::chrono::milliseconds>(tp.time_since_epoch());
    std::time_t timestamp=tmp.count();
    //std::time_t timestamp=std::chrono::system_clock::to_time_t(tp);
    return timestamp;
}
std::time_t getTimeStamp() {
    std::chrono::time_point<std::chrono::system_clock,std::chrono::nanoseconds> tp =
        std::chrono::time_point_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now());
    auto tmp=std::chrono::duration_cast<std::chrono::nanoseconds>(tp.time_since_epoch());
    std::time_t timestamp=tmp.count();
    //std::time_t timestamp=std::chrono::system_clock::to_time_t(tp);
    return timestamp;
}
//double** matrix_multiply(double** a_matrix, int a_row_num, int a_col_num, 
//        double** b_matrix, int b_row_num, int b_col_num) {
//    double(* res) [b_col_num] = (double(*)[b_col_num])malloc(a_row_num * b_col_num * sizeof(double));
//    memset((char*)res, 0, a_row_num * b_col_num * sizeof(double));
//
//    for (int i = 0; i < a_row_num; ++i) {
//        for (int j = 0; j < a_col_num; ++j) {
//        }
//    }
//}
//
//
double** matrix_multiply(double **a_matrix1, double **b_matrix1, int num) {
    double(* res) [num] = (double(*)[num])malloc(num * num * sizeof(double));
    memset((char*)res, 0, num * num * sizeof(double));

    double (*a_matrix)[num] = (double(*)[num])a_matrix1;
    double (*b_matrix)[num] = (double(*)[num])b_matrix1;

    for (int i = 0; i < num; ++i) {
        for (int j = 0; j < i; ++j) {
            double tmp = b_matrix[i][j];
            b_matrix[i][j] = b_matrix[j][i];
            b_matrix[j][i] = tmp;
        }
    }
    double sum = 0.0;

    //auto start = getTimeStamp(); 
    #pragma omp parallel for
    for (int i = 0; i < num; ++i) {
        for (int j = 0; j < num; ++j) {
            sum = 0.0;
            for (int k = 0; k < num; ++k) {
                sum += a_matrix[i][k] * b_matrix[j][k];
            }
            res[i][j] = sum;
        }
    }
    //printf("%d ", getTimeStamp() - start);
    return (double**)res;
}

double vector_multiply(double* a_vec, double* b_vec, int num) {
    double sum = 0.0;
    for (int i = 0; i < num; ++i) {
        sum += a_vec[num] * b_vec[num];
    }
    return sum;
}

double* matrix_vector_multiply(double** matrix, double* vec, int num) {
    double* res = (double*)malloc(sizeof(double) * num);

    double (*mtr)[num] = (double(*)[num])matrix;
    double sum = 0.0;

    for (int i = 0; i < num; ++i) {
        sum = 0.0;
        for (int j = 0; j < num; ++j) {
            sum += mtr[i][j] * vec[j];
        }
        res[i] = sum;
    }

    return res;
}

void print(double **a_matrix1, int num) {

    double (*a_matrix)[num] = (double(*)[num])a_matrix1;
    printf("--------------\n");
    for (int i = 0; i < num; ++i) {
        for (int j = 0; j < num; ++j) {
            printf("%f ", a_matrix[i][j]);
        }
        printf("\n");
    }
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




double* load_vector(const std::string& file, int num) {
    std::fstream fs;
    fs.open(file.c_str(), std::fstream::in);
    std::string line;
    int nrow = 0;
    double* ret = (double*)malloc(sizeof(double) * num);
    while (std::getline(fs, line)) {
        trim(line);
        ret[nrow] = std::stod(line);
        ++nrow;
    } 
    if (nrow != num) {
        printf("error vector nrow:%d, num:%d", nrow, num);
        return NULL;
    }
    return ret;
}

double** load_matrix(const std::string& file, int& num) {
    std::fstream fs;
    fs.open(file.c_str(), std::fstream::in);
    std::string line;
    int nrow = 0;
    int ncol = -1;

    double** ret = NULL;
    while (std::getline(fs, line)) {
        //printf("line:%s\n", line.c_str());
        std::vector<std::string> vec;
        split(line, ",", vec);
        if (ncol == -1) {
            ncol = vec.size();
            num = ncol;
            double(* am) [num] = (double(*)[num])malloc(num * num * sizeof(double));
            ret = (double**)am;
        }
        double(* am) [num] = (double(*)[num])ret;
        if (ncol != vec.size()) {
            printf("error line, %s\n", line.c_str());
            return NULL;
        }
        for (int k = 0; k < ncol; ++k) {
            am[nrow][k] = std::stod(vec[k]);
            //printf("item (%d %d):%f  :  %s\n", nrow, k, am[nrow][k], vec[k].c_str());
        }
        ++nrow;
    } 
    if (nrow != ncol) {
        printf("error matrix nrow:%d, ncol:%d", nrow, ncol);
        return NULL;
    }
    return ret;
}

void test_matrix_matrix() {
    int a_num = 0;
    double** a = load_matrix("a.csv", a_num);
    if (a == NULL) {
        return;
    }
    //print(a, a_num);

    int b_num = 0;
    double** b = load_matrix("b.csv", b_num);
    if (b == NULL) {
        return;
    }
    //print(b, b_num);

    if (a_num != b_num) {
        printf("error a b matrix, %d:%d", a_num, b_num);
        return;
    }
    auto start = getTimeStamp(); 
    double** res = matrix_multiply(a, b, a_num);
    printf("matrix*matrix %d\n", getTimeStamp() - start);
    //print(res, a_num);
}

void test_matrix_vector() {
    int a_num = 0;
    double** a = load_matrix("a.csv", a_num);
    if (a == NULL) {
        return;
    }
    //print(a, a_num);

    int b_num = 3000;
    double* b = load_vector("c.csv", b_num);
    if (b == NULL) {
        return;
    }
    //print(b, b_num);

    if (a_num != b_num) {
        printf("error a b matrix, %d:%d", a_num, b_num);
        return;
    }
    auto start = getTimeStamp(); 
    double* res = matrix_vector_multiply(a, b, a_num);
    printf("matrix*vector %d\n", getTimeStamp() - start);
    //print(res, a_num);
}

void test_vector_vector() {
    int a_num = 3000;
    double* a = load_vector("d.csv", a_num);
    if (a == NULL) {
        return;
    }
    //print(a, a_num);

    int b_num = 3000;
    double* b = load_vector("c.csv", b_num);
    if (b == NULL) {
        return;
    }
    //print(b, b_num);

    if (a_num != b_num) {
        printf("error a b matrix, %d:%d", a_num, b_num);
        return;
    }
    auto start = getTimeStamp(); 
    double res = vector_multiply(a, b, a_num);
    printf("vector*vector %d\n", getTimeStamp() - start);
    //print(res, a_num);
}

int main() {
    test_matrix_matrix();
    test_matrix_vector();
    test_vector_vector();

    // int num = 2;
    // double(* am) [num] = (double(*)[num])malloc(num * num * sizeof(double));
    // double(* bm) [num] = (double(*)[num])malloc(num * num * sizeof(double));
    // int s = 0;
    // for (int i = 0; i < num; ++i) {
    //     for (int j = 0; j < num; ++j) {
    //         am[i][j] = i + j;
    //         bm[i][j] = s;
    //         s +=1;
    //     }
    // }
    // print((double**)am, num);
    // print((double**)bm, num);
    // double** res = matrix_multiply((double**)am, (double**)bm, num);
    // print(res, num);

    return 0;
}
