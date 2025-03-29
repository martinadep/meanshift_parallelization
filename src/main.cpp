#include <iostream>
#include "include/point.h"

using namespace std;

int main() {
    cout << "Hello world!";
    double c[3] = {1, 2, 3};
    Point<double> point(c, 2);
    Point p1 = point;
    cout <<endl << point << p1;
    return 0;
}
