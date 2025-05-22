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
#include "include/color_conversion.h"
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
        std::cout << "No arguments provided. Using default values." << endl;
        std::cout << "Usage: main.exe [--kernel | -k kernel_name] [--bandwidth | -b bandwidth] [--input | -i input_csv] [--output | -o output_csv]" << endl;
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

    getline(filein, line); // skip the third line "R,G,B"

    Point* dataset = new Point[pixel_count];
    
    unsigned int index = 0;

    #ifdef PREPROCESSING
    Point rgb_point;
    Point lab_point;
    #endif
    // read each row (pixel) and convert in doubles
    while (getline(filein, line) && index < pixel_count) {
        stringstream ss(line);
        string r, g, b;

        getline(ss, r, ',');
        getline(ss, g, ',');
        getline(ss, b, ',');

        // append each pixel in the dataset
#ifdef PREPROCESSING
        rgb_point[0] = T(stoi(r));
        rgb_point[1] = T(stoi(g));
        rgb_point[2] = T(stoi(b));
        
        // Convert to LAB
        rgb_to_lab(rgb_point, lab_point);
        
        // Store LAB values in the dataset
        copy_point(&lab_point, &dataset[index]);
#else
        Point point;
        point[0] = T(stoi(r));
        point[1] = T(stoi(g));
        point[2] = T(stoi(b));
        
        copy_point(&point, &dataset[index]); // copy to dataset
#endif
        index++;
    }
    filein.close();

    // ------------------------- MEAN-SHIFT ----------------------------
    std::cout << endl << "==================== Mean-Shift ==================" << endl;
    std::cout << "Dataset: [" << input_csv_path  << "]\t "<< width << "x" << height << " (" << pixel_count << " elements)" << endl << endl;
    std::cout << "Type precision: " << sizeof(T) * 8 << " bits - " << TYPENAME << endl;
    std::cout << "\t- Bandwidth: " << bandwidth << endl;
    std::cout << "\t- Kernel: " << kernel << endl;
    
    Point* shifted_dataset = new Point[pixel_count];
    Point cluster_modes[1000]; 
    unsigned int clusters_count = 0; // number of clusters 

#ifdef PREPROCESSING
    double m = 10.0; // compactness parameter
    std::cout <<"Preprocessing (SLIC)"<< endl << "\t- Superpixels: " << NUM_SUPERPIXELS << endl;
    std::cout << "\t- Compactness: " << m << endl <<endl;
    
    Point* superpixel_dataset = new Point[NUM_SUPERPIXELS];
    Point* shifted_superpixels = new Point[NUM_SUPERPIXELS];
    int* dataset_labels = new int[pixel_count];
#endif


#ifdef PREPROCESSING
#ifdef TOTAL_TIMING
    TOTAL_TIMER_START(slic)
#endif
    preprocess_dataset(pixel_count, dataset, dataset_labels, superpixel_dataset, width, height, NUM_SUPERPIXELS, m);
#ifdef TOTAL_TIMING
    TOTAL_TIMER_STOP(slic)
#endif

    FILE *fileout_slic = fopen("./data/slic_output.csv", "w");
    if (!fileout_slic) {
        cerr << "Error opening ./data/slic_output.csv";
        exit(-1);
    }
    fprintf(fileout_slic, "width,height,\n");
    fprintf(fileout_slic, "%d,%d,\n", width, height);
    fprintf(fileout_slic, "R,G,B\n");
    
    for (int i = 0; i < pixel_count; i++) {
        int label = dataset_labels[i];
        copy_point(&superpixel_dataset[label], &lab_point);
        lab_to_rgb(lab_point, rgb_point);
        write_point_to_file(&rgb_point, fileout_slic);
    }
    fclose(fileout_slic);
 
#ifdef TOTAL_TIMING
    TOTAL_TIMER_START(mean_shift)
#endif
    mean_shift(NUM_SUPERPIXELS, superpixel_dataset, shifted_superpixels, bandwidth, kernel_map[kernel], cluster_modes, &clusters_count);
    for(unsigned int i = 0; i < pixel_count; i++) {
        int label = dataset_labels[i]; 
        copy_point(&shifted_superpixels[label], &shifted_dataset[i]);
    }
#ifdef TOTAL_TIMING
    TOTAL_TIMER_STOP(mean_shift)
#endif
    // Free heap memory
    delete[] superpixel_dataset;
    delete[] shifted_superpixels;
    delete[] dataset_labels;
#else
#ifdef TOTAL_TIMING
    TOTAL_TIMER_START(mean_shift)
#endif
    mean_shift(pixel_count, dataset, shifted_dataset, bandwidth, kernel_map[kernel], cluster_modes, &clusters_count);

#ifdef TOTAL_TIMING
    TOTAL_TIMER_STOP(mean_shift)
#endif
#endif
    std::cout << "\n\n>>> Clusters found: " << clusters_count << "\n\n";

    // write to csv file
    FILE *fileout_prep = fopen("./data/modified.csv", "w");
    if (!fileout_prep) {
        cerr << "Error opening " << output_csv_path;
        exit(-1);
    }
    fprintf(fileout_prep, "width,height,\n");
    fprintf(fileout_prep, "%d,%d,\n", width, height);
    fprintf(fileout_prep, "R,G,B\n");

#ifdef PREPROCESSING
    for (int i = 0; i < pixel_count; i++) {
        copy_point(&shifted_dataset[i], &lab_point);
        lab_to_rgb(lab_point, rgb_point);
        write_point_to_file(&rgb_point, fileout_prep);
    }
#else
    for (int i = 0; i < pixel_count; i++) {
        write_point_to_file(&shifted_dataset[i], fileout_prep);
    }
#endif
    fclose(fileout_prep);
    
    #ifdef PREPROCESSING
    std::cout << ">>>> SLIC results saved in: [./data/slic_output.csv] <<<<" << endl;
    #endif
    std::cout << ">>>> Mean-Shift results saved in: [./data/modified.csv] <<<<" << endl;
    std::cout << "=================================================" << endl;
    
    delete[] dataset;
    delete[] shifted_dataset;
    return 0;
}

