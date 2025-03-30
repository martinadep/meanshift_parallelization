//
// Created by marti on 28/03/2025.
//

#ifndef __POINT_H__
#define __POINT_H__

#include <iomanip>
#include <iostream>

using namespace std;
template <typename T> // like java's generics

class Point {
    private:
      T *coords;
      unsigned int dim;
      unsigned int cluster;

      public:
    /// default constructor
        Point(){
          this->coords = NULL;
          this->dim = 0;
          this->cluster = 0;
        }

    /// parametric constructor, given coordinates and dimensions number
        Point(T *_coords, unsigned int _dim) : dim(_dim), cluster(0) {
          this->coords = new T[_dim];
          for (unsigned int i = 0; i < _dim; i++) {
            coords[i] = _coords[i];
          }
        }
    /// copy constructor
        Point(const Point &p) : cluster(p.cluster), dim(p.dim) {
            coords = new T[dim];
            for (unsigned int i = 0; i < dim; i++) {
                coords[i] = p.coords[i];
            }
        }
    /// distructor
        ~Point() {
            delete[] coords;
        }
    // methods
        int getCluster() {
            return cluster;
        }
        int setCluster(int _cluster) {
            cluster = _cluster;
        }
        T getSingleCoord(int i) {
            if (i >= dim) {
                printf("Coordinate index is out of range");
                exit(-1); // TODO: implement errors
            }
            return coords[i];
        }
    // operators
        Point& operator=(const Point& p) {
            if (coords) {
                delete[] coords;
            }
            dim = p.dim;
            cluster = p.cluster;
            coords = new T[p.dim];
            for (unsigned int i = 0; i < p.dim; i++) {
                coords[i] = p.coords[i];
            }
            return *this;
        }
        bool operator==(const Point<T> &p) const {
            if (dim != p.dim) return false;
            for (unsigned int i = 0; i < dim; i++) {
                if (coords[i] != p.coords[i]) return false;
            }
            return true;
        }
    // first parameter is not Point itself, hence it's an external function that requires 'friend'
        friend ostream& operator<< (ostream &os, Point const &p) {
            os << setw(9) << "c:" << p.cluster;
            for (unsigned int i = 0; i < p.dim; i++) {
                os << setw(9) << setprecision(5) << p.coords[i];
            }
            return os << endl;
        }
        void writeToFile(std::ofstream& file) const {
            for (unsigned int i = 0; i < dim; i++) {
                file << coords[i];
                if (i < dim - 1) {
                    file << ",";
                }
            }
            file << "\n";
        }
};

#endif //__POINT_H__
