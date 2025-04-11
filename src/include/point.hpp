//
// Created by marti on 28/03/2025.
//

#ifndef __POINT_H__
#define __POINT_H__

#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

using namespace std;
template<typename T>

class Point {
private: vector<T> coords;
public:
    //vector<T> coords;

    /// default constructor
    Point() = default;
    Point(int dim) {
        coords.resize(dim);
        for (int i = 0; i < dim; i++) {
            coords[i] = 0;
        }
    }

    /// constructor given coordinates
    Point(vector<T> _coords) {
        coords.resize(_coords.size());
        for (unsigned int i = 0; i < _coords.size(); i++) {
            coords[i] = _coords[i];
        }
    }

    /// distructor
    ~Point() = default;

    // PER RIDURRE OVERHEAD: 
    // + INLINE e il compilatore sostituirà il codice direttamente
    // ++ PUBLIC su vettore delle coordinate 

    T getSingleCoord(int i) const {
        if (i >= coords.size()) {
            printf("getSingleCoord: Coordinate index is out of range");
            exit(-1); // TODO: implement errors
        }
        return coords[i];
    }
    void setSingleCoord(int i, T value) {
        if (i >= coords.size()) {
            printf("setSingleCoord: Coordinate index is out of range");
            exit(-1);
        }
        coords[i] = value;
    }
    unsigned int size() const {
        return coords.size();
    }
    void resize(unsigned int new_size) {
        coords.resize(new_size);
    }

    // operators
    // copy
    Point& operator=(const Point &p) {
        if (this != &p) {
            coords = p.coords;
        }
        return *this;
    }
    // comparison
    bool operator==(const Point &p) const {
        if (coords.size() != p.coords.size()) return false;
        for (unsigned int i = 0; i < coords.size(); i++) {
            if (fabs(coords[i] - p.coords[i]) > 0.001) return false;
        }
        return true;
    }

    void operator/=(T scalar) {
        if (scalar == 0) {
            throw std::invalid_argument("Division by zero");
        }
        for (unsigned int i = 0; i < coords.size(); i++) {
             coords[i] /= scalar;
        }
    }

    // first parameter is not Point itself, hence it's an external function that requires 'friend'
    friend ostream &operator<<(ostream &os, Point const &p) {
        for (unsigned int i = 0; i < p.coords.size(); i++) {
            os << setw(9) << setprecision(5) << p.coords[i];
        }
        return os << endl;
    }

    void writeToFile(std::ofstream &file) const {
        for (unsigned int i = 0; i < coords.size(); i++) {
            file << int(coords[i]);
            if (i < coords.size() - 1) {
                file << ",";
            }
        }
        file << "\n";
    }
};

#endif //__POINT_H__
