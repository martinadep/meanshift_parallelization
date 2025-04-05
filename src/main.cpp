#include <fstream>
#include <iostream>
#include "include/point.hpp"
#include "include/cluster.hpp"
#include "include/mean_shift.hpp"
using namespace std;

string input_csv_path = "../data/original.csv";
string output_csv_path = "../data/modified.csv";

#define BANDWIDTH 10.0

int main() {
    cout << endl;
    ifstream filein(input_csv_path);
    if (!filein) {
        cerr << "Error opening CSV file\n";
        return 1;
    }

    string line;

    // get width, height and pixel_count
    getline(filein, line); // skip first line "width, height"
    getline(filein, line); // get dimensions values
    stringstream ss(line);
    string width_str, height_str;
    getline(ss, width_str, ',');
    getline(ss, height_str, ',');

    int width = stoi(width_str);
    int height = stoi(height_str);
    int pixel_count = width * height;

    getline(filein, line); // skip the third line "R,G,B"
    vector<Point<double>> dataset;
    unsigned int index = 0;

    // read each row (pixel) and convert in doubles
    while (getline(filein, line) && index < pixel_count) {
        stringstream ss(line);
        string r, g, b;

        getline(ss, r, ',');
        getline(ss, g, ',');
        getline(ss, b, ',');

        // append each pixel in the dataset
        vector pixel = {double(stoi(r)), double(stoi(g)), double(stoi(b))};
        Point<double> point = Point(pixel);
        dataset.push_back(point);
        index++;
    }
    filein.close();

    // -------- MEAN-SHIFT ----------
    int num_of_dimensions = dataset[0].coords.size();
    // initialize mean shift with dataset and bandwidth
    MeanShift<double> ms = MeanShift(dataset, BANDWIDTH, num_of_dimensions);

    ms.mean_shift();

    // write to csv file
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
    cout <<"\"data/modified.csv"<< "\" successfully created\n";

    return 0;
}
