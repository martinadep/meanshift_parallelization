#include <fstream>
#include <filesystem>
#include <iostream>
#include <sys/time.h>
#include "include/point.h"
#include "include/mean_shift.h"
#include "include/utils.h"
#include <unordered_map>
#include <map>

#ifdef PREPROCESSING
#include "preprocessing/preprocessing.h"
#endif

#ifdef TOTAL_TIMING
#include "metrics/timing.h"
#endif

using namespace std;  

int main(int argc, char *argv[]) {
    // Set the working directory to the project root
    std::filesystem::current_path(std::filesystem::path(argv[0]).parent_path().parent_path());

    // Default values
    const char *kernel = KERNEL;
    unsigned int bandwidth = BANDWIDTH;
    const char *input_csv_path = CSV_IN;
    const char *output_csv_path = CSV_OUT;

    if (argc < 2) {
        cout << "No arguments provided. Using default values." << endl;
        cout << "Usage: main.exe [--kernel | -k kernel_name] [--bandwidth | -b bandwidth] [--input | -i input_csv] [--output | -o output_csv]" << endl;
    }
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
    unordered_map<string, T (*)(T, unsigned int)> kernel_map = {
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

    Point dataset[pixel_count]; // allocate memory for dataset
    
    unsigned int index = 0;

    // read each row (pixel) and convert in doubles
    while (getline(filein, line) && index < pixel_count) {
        stringstream ss(line);
        string r, g, b;

        getline(ss, r, ',');
        getline(ss, g, ',');
        getline(ss, b, ',');

        // append each pixel in the dataset
        Point point;
        point[0] = T(stoi(r));
        point[1] = T(stoi(g));
        point[2] = T(stoi(b));
        
        copy_point(&point, &dataset[index]); // copy to dataset
        index++;
    }
    filein.close();

    // ------------------------- MEAN-SHIFT ----------------------------
    cout << endl << "==================== Mean-Shift ==================" << endl;
    cout << "Input: \"" << input_csv_path << "\"" << endl;
    cout << "Output: \"" << output_csv_path << "\"" << endl;
    cout << "Bandwidth: " << bandwidth << endl;
    cout << "Kernel: " << kernel << endl;
    cout << "Dataset size: " << width << "x" << height << " - " << pixel_count << " elements" << endl << endl;
    cout << "Type precision: " << sizeof(T) * 8 << " bits - " << TYPENAME << endl;

#ifdef PREPROCESSING
     // SLIC parameters
    int num_superpixels = 50;
    double m = 10.0; // compactness parameter
    cout << endl << "Superpixels: " << num_superpixels << endl;
    cout << "Compactness: " << m << endl;
    cout << "Preprocessing dataset..." << endl;
    Point processed_dataset[pixel_count];
    preprocess_dataset(pixel_count, dataset, processed_dataset, width, height, num_superpixels, m);
#endif

    Point shifted_dataset[pixel_count]; // allocate memory for shifted dataset 
    Point cluster_modes[1000]; // allocate memory for cluster modes 
    unsigned int clusters_count = 0; // number of clusters 

#ifdef TOTAL_TIMING
    TOTAL_TIMER_START(mean_shift)
#endif

#ifdef PREPROCESSING
    preprocess_dataset(pixel_count, dataset, processed_dataset, width, height, num_superpixels, m);
    mean_shift(pixel_count, processed_dataset, shifted_dataset, bandwidth, kernel_map[kernel], cluster_modes, &clusters_count);
#else
    mean_shift(pixel_count, dataset, shifted_dataset, bandwidth, kernel_map[kernel], cluster_modes, &clusters_count);
#endif

#ifdef TOTAL_TIMING
    TOTAL_TIMER_STOP(mean_shift)
#endif
    cout << "Mean-Shift completed." << endl;
    cout << "Clusters found: " << clusters_count << endl << endl;

    // ------------------------------------------------------------------

    cout << "Saving data to CSV file..." << endl;
    // write to csv file
    FILE *fileout_prep = fopen("./data/modified.csv", "w");
    if (!fileout_prep) {
        cerr << "Error opening " << output_csv_path;
        exit(-1);
    }
    fprintf(fileout_prep, "width,height,\n");
    fprintf(fileout_prep, "%d,%d,\n", width, height);
    fprintf(fileout_prep, "R,G,B\n");
    for (int i = 0; i < pixel_count; i++) {
        write_point_to_file(&shifted_dataset[i], fileout_prep);
    }

    fclose(fileout_prep);
    cout << "All data successfully saved inside " << "\"data/modified.csv" << "\"." << endl;
    cout << "=================================================" << endl;

#ifdef PREPROCESSING
    cout << "Saving processed dataset to CSV file..." << endl;
    FILE *fileout = fopen("./data/preprocessed.csv", "w");
    if (!fileout) {
        cerr << "Error opening " << output_csv_path;
        exit(-1);
    }
    fprintf(fileout, "width,height,\n");
    fprintf(fileout, "%d,%d,\n", width, height);
    fprintf(fileout, "R,G,B\n");
    for (int i = 0; i < pixel_count; i++) {
        write_point_to_file(&processed_dataset[i], fileout);
    }

    fclose(fileout);
    cout << "All data successfully saved inside " << "\"data/preprocessed.csv" << "\"." << endl;
    cout << "=================================================" << endl;
#endif
    return 0;
}

