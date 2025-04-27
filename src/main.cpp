#include <fstream>
#include <filesystem>
#include <iostream>
#include <sys/time.h>
#include "include/point.hpp"
//#include "include/mean_shift.hpp"
#include "include/utils.hpp"
#include <unordered_map>
#include <map>

#include "include/prova_mean_shift.hpp"

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
    //vector<Point> dataset;

    Point prova_dataset[pixel_count]; // allocate memory for dataset
    
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
        
        //dataset.push_back(point);
        copy_point(point, prova_dataset[index]); // copy to prova_dataset
        index++;
    }
    filein.close();

    // ------------------ MEAN-SHIFT ----------------------
    /*
    cout << endl << "==================== Mean-Shift ==================" << endl;
    cout << "Input: \"" << input_csv_path << "\"" << endl;
    cout << "Output: \"" << output_csv_path << "\"" << endl;
    cout << "Bandwidth: " << bandwidth << endl;
    cout << "Kernel: " << kernel << endl;
    cout << "Dataset size: " << dataset.size() << " elements" << endl << endl;

    // initialize mean shift
    MeanShift ms = MeanShift(dataset, bandwidth);
    ms.set_kernel(kernel_map[kernel]);

#ifdef MS_TIMING
    TOTAL_TIMER_START(mean_shift)
#endif

    ms.mean_shift();

#ifdef MS_TIMING
    TOTAL_TIMER_STOP(mean_shift)
#endif
    cout << "Mean-Shift completed." << endl;
    cout << "Clusters found: " << ms.get_clusters_count() << endl << endl;
    
    cout << "Saving data to CSV file..." << endl;

    // write to csv file
    //ofstream fileout(output_csv_path);
    FILE *fileout = fopen(output_csv_path, "w");
    if (!fileout) {
        cerr << "Error opening " << output_csv_path;
        exit(-1);
    }
    fprintf(fileout, "width,height,\n");
    fprintf(fileout, "%d,%d,\n", width, height);
    fprintf(fileout, "R,G,B\n");
    for (int i = 0; i < pixel_count; i++) {
        //ms.shifted_dataset[i].writeToFile(fileout);
        write_point_to_file(ms.shifted_dataset[i], fileout);
    }

    //fileout.close();
    fclose(fileout);
    cout << "All data successfully saved inside " << "\"data/modified.csv" << "\"." << endl;
    cout << "=================================================" << endl;
    */
// ---------------------------------------------
// ------------------ MEAN-SHIFT ----------------------
cout << endl << "==================== Mean-Shift prova ==================" << endl;
cout << "Input: \"" << input_csv_path << "\"" << endl;
cout << "Output: \"" << output_csv_path << "\"" << endl;
cout << "Bandwidth: " << bandwidth << endl;
cout << "Kernel: " << kernel << endl;
cout << "Dataset size: " << pixel_count << " elements" << endl << endl;


Point prova_shifted_dataset[pixel_count]; // allocate memory for shifted dataset prova
Point cluster_modes[1000]; // allocate memory for cluster modes prova
unsigned int clusters_count = 0; // number of clusters prova

#ifdef MS_TIMING
TOTAL_TIMER_START(prova_mean_shift)
#endif

prova_mean_shift(pixel_count, prova_dataset, prova_shifted_dataset, bandwidth, kernel_map[kernel], cluster_modes, clusters_count);

#ifdef MS_TIMING
TOTAL_TIMER_STOP(prova_mean_shift)
#endif
cout << "Mean-Shift completed." << endl;
cout << "Clusters found: " << clusters_count << endl << endl;

cout << "Saving data to CSV file..." << endl;

// write to csv file
//ofstream fileout(output_csv_path);
FILE *fileout1 = fopen("./data/prova_modified.csv", "w");
if (!fileout1) {
    cerr << "Error opening " << output_csv_path;
    exit(-1);
}
fprintf(fileout1, "width,height,\n");
fprintf(fileout1, "%d,%d,\n", width, height);
fprintf(fileout1, "R,G,B\n");
for (int i = 0; i < pixel_count; i++) {
    //ms.shifted_dataset[i].writeToFile(fileout);
    write_point_to_file(prova_shifted_dataset[i], fileout1);
}

//fileout.close();
fclose(fileout1);
cout << "All data successfully saved inside " << "\"data/prova_modified.csv" << "\"." << endl;
cout << "=================================================" << endl;

return 0;
}

