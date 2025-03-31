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

template<typename T> // like java's generics

class Point {

public:
    vector<T> coords;

    /// default constructor
    Point() {}

    /// parametric constructor, given coordinates and dimensions number
    Point(vector<T> _coords) {
        for (unsigned int i = 0; i < _coords.size(); i++) {
            coords.push_back(_coords[i]);
        }
    }
    /// copy constructor
    Point(const Point &p)  {
        coords = p.coords;
    }

    /// distructor
    ~Point() {
    }

    // operators
    Point& operator=(const Point &p) {
        if (this == &p) {
            coords = p.coords;
        }
        return *this;
    }

    bool operator==(const Point<T> &p) const {
        if (coords.size() != p.coords.size()) return false;
        for (unsigned int i = 0; i < coords.size(); i++) {
            if (coords[i] != p.coords[i]) return false;
        }
        return true;
    }

    Point operator+(const Point<T> &p) const {
        if (coords.size() != p.coords.size()) {
            throw invalid_argument("Points must have the same dimension");
        }
        vector<T> newCoords;
        for (unsigned int i = 0; i < coords.size(); i++) {
            newCoords[i] = coords[i] + p.coords[i];
        }
        return Point(newCoords, coords.size());
    }
    Point operator/(T scalar) const {
        if (scalar == 0) {
            throw std::invalid_argument("Division by zero");
        }
        vector<T> newCoords;
        for (unsigned int i = 0; i < coords.size(); i++) {
            newCoords[i] = coords[i] / scalar;
        }
        return Point(newCoords, coords.size());
    }

    // first parameter is not Point itself, hence it's an external function that requires 'friend'
    friend ostream &operator<<(ostream &os, Point const &p) {
        //os << setw(9) << "cluster:" << p.cluster << " | ";
        for (unsigned int i = 0; i < p.coords.size(); i++) {
            os << setw(9) << setprecision(5) << p.coords[i];
        }
        return os << endl;
    }

    T getSingleCoord(int i) const {
        if (i >= coords.size()) {
            printf("Coordinate index is out of range");
            exit(-1); // TODO: implement errors
        }
        return coords[i];
    }
    unsigned int getDimension() const {
        return coords.size();
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

    T euclidean_distance(const Point<T> &p) const {
        if (coords.size() != p.getDimension()) {
            cout << "couldn't compute distance between different dimensions points" << endl;
            cout << "p1:" << coords.size() << ", p2:" << p.getDimension() << endl;
            exit(-1);
        }
        T sum = 0;
        for (unsigned int i = 0; i < coords.size(); i++) {
            sum += pow(p.coords[i] - coords[i], 2);
        }
        return sqrt(sum);
    }
};

#endif //__POINT_H__
