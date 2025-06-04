#include <fstream>
#include <filesystem>
#include <iostream>
#include <sys/time.h>
#include <unordered_map>
#include <map>
#include "include/point.h"
#include "include/mean_shift.h"
#include "include/utils.h"

#define MAX_PIXEL_COUNT 4000000 // = 400MB (96MB + 96MB for dataset and shifted_dataset)
                                // each Point is 3 doubles (3 * 8 bytes (double) = 24 bytes)
                                // 2048 x 2048 image has 4'194'304 pixels
                                // dataset = pixel_count * sizeof(Point) = 4'000'000 * 24 bytes = 96MB
                                // allocated in data segment

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
    T bandwidth = BANDWIDTH;
    const char *input_csv_path = CSV_IN;
    const char *output_csv_path = CSV_OUT;
    const char *output_slic_path = "./data/slic_output.csv";
    #ifdef PREPROCESSING
    unsigned int superpixels = NUM_SUPERPIXELS;
    #endif

    if (argc < 2) {
        std::cout << "No arguments provided. Using default values." << endl;
        std::cout << "Usage: main.exe [--kernel | -k kernel_name] [--bandwidth | -b bandwidth] [--input | -i input_csv] [--output | -o output_csv]" << endl;
    }

    // Parse command-line arguments
    map<string, string> args;
    map<string, string> short_to_long = {
        {"-k", "--kernel"},
        {"-b", "--bandwidth"},
        {"-i", "--input"},
        {"-o", "--output"},
        {"-s", "--superpixels"}
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
    #ifdef PREPROCESSING
    if (args.find("--superpixels") != args.end()) {
        superpixels = stoi(args["--superpixels"]);
        if (superpixels > MAX_SUPERPIXELS){
            std::cout << "### Maximum number of superpixels is set to "<<< MAX_SUPERPIXELS << " ! ###" << endl;
            superpixels = MAX_SUPERPIXELS;
        }
    }
    #endif

    // Map kernel names to functions
    #ifdef MEAN_SHIFT_SQRD
    unordered_map<string, T (*)(T, T)> kernel_map = {
        {"gaussian", gaussian_kernel_sqrd},
        {"uniform", uniform_kernel_sqrd},
        {"epanechnikov", epanechnikov_kernel_sqrd}
    };
    #else
    unordered_map<string, T (*)(T, T)> kernel_map = {
        {"gaussian", gaussian_kernel},
        {"uniform", uniform_kernel},
        {"epanechnikov", epanechnikov_kernel}
    };
    #endif

    // Validate kernel name
    if (kernel_map.find(kernel) == kernel_map.end()) {
        cerr << "Invalid kernel name. Available options: gaussian, uniform, epanechnikov" << endl;
        return 1;
    }

    // Open input file
    ifstream filein(input_csv_path);
    if (!filein) {
        cerr << "Error opening CSV file\n";
        std::cout << "Current working directory: " << filesystem::current_path() << endl;
        std::cout << "Input_csv_path: " << input_csv_path << endl;
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

    if (pixel_count > MAX_PIXEL_COUNT) {
        cerr << "Error: The image has too many pixels (" << pixel_count << "). Maximum allowed is " << MAX_PIXEL_COUNT << "." << endl;
        return 1;
    }

    getline(filein, line); // skip the third line "R,G,B"

    static Point dataset [MAX_PIXEL_COUNT]; // dataset to store LAB values
    
    unsigned int index = 0;

    Point lab_point;
    // read each row (pixel) and convert in doubles
    while (getline(filein, line) && index < pixel_count) {
        stringstream ss(line);
        string r, g, b;

        getline(ss, r, ',');
        getline(ss, g, ',');
        getline(ss, b, ',');

        // append each pixel in the dataset
        lab_point[0] = T(stoi(r));
        lab_point[1] = T(stoi(g));
        lab_point[2] = T(stoi(b));
        
        // Store LAB values in the dataset
        copy_point(&lab_point, &dataset[index]);
        index++;
    }
    filein.close();

    // ------------------------- MEAN-SHIFT ----------------------------
    std::cout << endl << "==================== Mean-Shift ==================" << endl;
    std::cout << "Dataset: [" << input_csv_path  << "]\t "<< width << "x" << height << " (" << pixel_count << " elements)" << endl << endl;
    std::cout << "Type precision: " << sizeof(T) * 8 << " bits - " << TYPENAME << endl;
    std::cout << "\t- Bandwidth: " << bandwidth << endl;
    std::cout << "\t- Kernel: " << kernel << endl;
    
    static Point shifted_dataset [MAX_PIXEL_COUNT]; // dataset to store shifted LAB values
    static Point cluster_modes[1000]; 
    unsigned int clusters_count = 0; // number of clusters 

#ifdef PREPROCESSING
    double m = 10.0; // compactness parameter
    std::cout <<"Preprocessing (SLIC)"<< endl << "\t- Superpixels: " << superpixels << endl;
    std::cout << "\t- Compactness: " << m << endl <<endl;
        
    static Point superpixel_dataset [MAX_SUPERPIXELS];
    static Point shifted_superpixels [MAX_SUPERPIXELS];
    static int dataset_labels [MAX_PIXEL_COUNT]; // labels for each pixel in the dataset

    // ----------------------- SLIC PREPROCESSING ----------------------------
#ifdef TOTAL_TIMING
    TOTAL_TIMER_START(slic)
#endif
    preprocess_dataset(pixel_count, dataset, dataset_labels, superpixel_dataset, width, height, superpixels, m);
#ifdef TOTAL_TIMING
    TOTAL_TIMER_STOP(slic)
#endif

    FILE *fileout_slic = fopen(output_slic_path, "w");
    if (!fileout_slic) {
        cerr << "Error opening " << output_slic_path;
        exit(-1);
    }
    fprintf(fileout_slic, "width,height,\n");
    fprintf(fileout_slic, "%d,%d,\n", width, height);
    fprintf(fileout_slic, "L,A,B\n");
    
    for (int i = 0; i < pixel_count; i++) {
        int label = dataset_labels[i];
        copy_point(&superpixel_dataset[label], &lab_point);
        write_point_to_file(&lab_point, fileout_slic);
    }
    fclose(fileout_slic);
    std::cout << ">>>> SLIC results saved in: [" << output_slic_path << "] <<<<" << endl;
    std::cout << "=============================================================" << endl;
    // ----------------------- END PREPROCESSING ----------------------------
#endif

#ifdef TOTAL_TIMING
    TOTAL_TIMER_START(mean_shift)
#endif

#ifdef PREPROCESSING
    mean_shift(superpixels, superpixel_dataset, shifted_superpixels, bandwidth, kernel_map[kernel], cluster_modes, &clusters_count);
    for(unsigned int i = 0; i < pixel_count; i++) {
        int label = dataset_labels[i]; 
        copy_point(&shifted_superpixels[label], &shifted_dataset[i]);
    }
#else

    // standard Mean-Shift
    mean_shift(pixel_count, dataset, shifted_dataset, bandwidth, kernel_map[kernel], cluster_modes, &clusters_count);


#endif
#ifdef TOTAL_TIMING
    TOTAL_TIMER_STOP(mean_shift)
#endif

    if (clusters_count > 1000) {
        std::cout << "--- Warning: More than 1000 clusters found. Some clusters may be lost." << endl;
    } else if (clusters_count == 1) {
        std::cout << "--- Warning: Only one cluster found. No segmentation possible." << endl<< "Try to select a smaller bandwidth." << endl;
    } else{
        std::cout << "--- Clusters found: " << clusters_count << endl;
    }
    
    // write to csv file
    FILE *fileout = fopen(output_csv_path, "w");
    if (!fileout) {
        cerr << "Error opening " << output_csv_path;
        exit(-1);
    }
    fprintf(fileout, "width,height,\n");
    fprintf(fileout, "%d,%d,\n", width, height);
    fprintf(fileout, "L,A,B\n");

    for (int i = 0; i < pixel_count; i++) {
        copy_point(&shifted_dataset[i], &lab_point);
        write_point_to_file(&lab_point, fileout);
    }
    fclose(fileout);

    std::cout << ">>>> Mean-Shift results saved in: [" << output_csv_path << "] <<<<" << endl;
    std::cout << "=============================================================" << endl;
    return 0;
}
