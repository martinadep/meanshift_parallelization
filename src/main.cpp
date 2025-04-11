#include <fstream>
#include <filesystem>
#include <iostream>
#include <sys/time.h>
#include "include/point.hpp"
#include "include/mean_shift.hpp"
#include "include/utils.hpp"
#include <unordered_map>
#include <map>

int main(int argc, char *argv[]) {
    // Set the working directory to the project root
    std::filesystem::current_path(std::filesystem::path(argv[0]).parent_path().parent_path());

    // Default values
    const char *kernel = KERNEL;
    unsigned int bandwidth = BANDWIDTH;
    const char *input_csv_path = CSV_IN;
    const char *output_csv_path = CSV_OUT;

    cout << "Usage: main.exe [--kernel | -k kernel_name] [--bandwidth | -b bandwidth] [--input | -i input_csv] [--output | -o output_csv]" << endl;

    // Parse command-line arguments
    map<string, string> args;
    map<string, string> short_to_long = {
        {"-k", "--kernel"},
        {"-b", "--bandwidth"},
        {"-i", "--input"},
        {"-o", "--output"}
    };
    for (int i = 1; i < argc; i += 2) {
        string key = argv[i];
        if (short_to_long.find(key) != short_to_long.end()) {
            key = short_to_long[key]; // Convert short option to long option
        }
        if (i + 1 < argc) {
            args[key] = argv[i + 1];
        } else {
            cerr << "Error: Missing value for argument " << argv[i] << endl;
            return 1;
        }
    }

    // Aggiorna i valori in base agli argomenti forniti
    if (args.find("--kernel") != args.end()) {
        kernel = args["--kernel"].c_str();
    }
    if (args.find("--bandwidth") != args.end()) {
        bandwidth = stoi(args["--bandwidth"]);
    }
    if (args.find("--input") != args.end()) {
        input_csv_path = args["--input"].c_str();
    }
    if (args.find("--output") != args.end()) {
        output_csv_path = args["--output"].c_str();
    }

    // Map kernel names to functions
    unordered_map<string, double (*)(double, unsigned int)> kernel_map = {
        {"gaussian", gaussian_kernel},
        {"uniform", uniform_kernel},
        {"epanechnikov", epanechnikov_kernel}
    };

    // Validate kernel name
    if (kernel_map.find(kernel) == kernel_map.end()) {
        cerr << "Invalid kernel name. Available options: gaussian, uniform, epanechnikov" << endl;
        return 1;
    }

    // Open input file
    ifstream filein(input_csv_path);
    if (!filein) {
        cerr << "Error opening CSV file\n";
        cout << "Current working directory: " << filesystem::current_path() << endl;
        cout << "Input_csv_path: " << input_csv_path << endl;
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
    vector<Point<double> > dataset;
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

    // ------------------ MEAN-SHIFT ----------------------
    cout << endl << "==================== Mean-Shift ==================" << endl;
    cout << "Input: \"" << input_csv_path << "\"" << endl;
    cout << "Output: \"" << output_csv_path << "\"" << endl;
    cout << "Bandwidth: " << bandwidth << endl;
    cout << "Kernel: " << kernel << endl;
    cout << "Dataset size: " << dataset.size() << " elements" << endl << endl;

    // initialize mean shift
    MeanShift<double> ms = MeanShift<double>(dataset, bandwidth);
    ms.set_kernel(kernel_map[kernel]);

#ifdef TIMING
    START_TIME(mean_shift)
#endif

    ms.mean_shift();

#ifdef TIMING
    END_TIME(mean_shift)
#endif

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
    cout << "=================================================" << endl << endl;
    cout << "All data successfully saved inside " << "\"data/modified.csv" << "\"";

    return 0;
}
