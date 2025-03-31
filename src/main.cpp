#include <fstream>
#include <iostream>
#include "include/point.h"
#include "include/cluster.h"
#include "include/mean_shift.h"
using namespace std;

string input_csv_path = "../data/original.csv";
string output_csv_path = "../data/modified.csv";

#define BANDWIDTH 40.0

int main() {
    cout << endl;

    ifstream filein(input_csv_path);
    if (!filein) {
        cerr << "Error opening CSV file\n";
        return 1;
    }

    string line;

    // get width and heigth
    getline(filein, line); // skip first line "width, height"
    getline(filein, line); // get dimensions values
    stringstream ss(line);
    string width_str, height_str;
    getline(ss, width_str, ',');
    getline(ss, height_str, ',');
    //cout << "width,height" << endl << width_str<<","<<height_str;
    int width = stoi(width_str);
    int height = stoi(height_str);

    // get pixel count
    int pixel_count = width * height;
    getline(filein, line); // skip the third line "R,G,B"
    Point<double>* dataset = new Point<double>[pixel_count];
    vector<Point<double>> points;
    unsigned int index = 0;
    // read each row and converts in number
    while (getline(filein, line) && index < pixel_count) {
        stringstream ss(line);
        string r, g, b;

        getline(ss, r, ',');
        getline(ss, g, ',');
        getline(ss, b, ',');

        // append each pixel in the dataset
        vector pixel = {double(stoi(r)), double(stoi(g)), double(stoi(b))};
        Point<double> point = Point(pixel);
        points.push_back(point);
        dataset[index] = point;
        index++;
    }
    filein.close();

    MeanShift<double> ms = MeanShift(points, BANDWIDTH, 3);
    ms.mean_shift();

    ofstream fileout(output_csv_path);
    if (!fileout) {
        cerr << "Error opening " << output_csv_path;
        exit(-1);
    }
    fileout << "width,height,\n";
    fileout << width << "," << height << ",\n";
    fileout << "R,G,B\n";

    for (int i = 0; i < pixel_count; i++) {
        ms.shifted_dataset[i].writeToFile(fileout);
    }

    fileout.close();
    cout << output_csv_path << " successfully created\n";

    return 0;
}
