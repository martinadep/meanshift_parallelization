#include <fstream>
#include <iostream>
#include "include/point.h"

using namespace std;

string input_csv_path = "../data/original.csv";
string output_csv_path = "../data/modified.csv";

int main() {
    ifstream filein(input_csv_path);
    if (!filein) {
        cerr << "Error opening CSV file\n";
        return 1;
    }
    string line;
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
    Point<int>* dataset = new Point<int>[pixel_count];

    unsigned int index = 0;
    // read each row and converts in number
    while (getline(filein, line) && index < pixel_count) {
        stringstream ss(line);
        string r, g, b;

        getline(ss, r, ',');
        getline(ss, g, ',');
        getline(ss, b, ',');

        // append each pixel in the dataset
        int * pixel = new int [3] {stoi(r), stoi(g), stoi(b)};
        dataset[index] = Point(pixel,3);
        delete[] pixel;
        index++;
    }
    filein.close();

    // modifica i primi 10k pixel per verifica
    for (int i = 0; i < 10000; i++) {
        //cout << dataset[i];
        int * pixel = new int [3] {100, 50, 70};
        dataset[i] = Point(pixel,3);
        delete[] pixel;
    }

    ofstream fileout(output_csv_path);
    if (!fileout) {
        cerr << "Error opening " << output_csv_path;
        exit(-1);
    }
    fileout << "width,height,\n";
    fileout << width << "," << height << ",\n";
    fileout << "R,G,B\n";
    for (int i = 0; i < pixel_count; i++) {
        dataset[i].writeToFile(fileout);
    }
    fileout.close();
    cout << output_csv_path << " successfully created\n";

    return 0;
}
