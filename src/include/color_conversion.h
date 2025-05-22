#ifndef COLOR_CONVERSION_H
#define COLOR_CONVERSION_H

#include <cmath>
#include "point.h"

// RGB to LAB conversion
inline void rgb_to_lab(const Point& rgb, Point& lab) {
    // Step 1: RGB to XYZ
    // Normalize RGB values to range [0, 1]
    double r = rgb[0] / 255.0;
    double g = rgb[1] / 255.0;
    double b = rgb[2] / 255.0;
    
    // Apply gamma correction (sRGB)
    r = (r > 0.04045) ? pow((r + 0.055) / 1.055, 2.4) : (r / 12.92);
    g = (g > 0.04045) ? pow((g + 0.055) / 1.055, 2.4) : (g / 12.92);
    b = (b > 0.04045) ? pow((b + 0.055) / 1.055, 2.4) : (b / 12.92);
    
    // Convert to XYZ color space
    double x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375;
    double y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750;
    double z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041;
    
    // Step 2: XYZ to LAB
    // Using D65 white point reference
    const double xn = 0.95047;
    const double yn = 1.0;
    const double zn = 1.08883;
    
    // Normalize XYZ values
    x /= xn;
    y /= yn;
    z /= zn;
    
    // Apply cube root transformation
    x = (x > 0.008856) ? pow(x, 1.0/3.0) : (7.787 * x + 16.0/116.0);
    y = (y > 0.008856) ? pow(y, 1.0/3.0) : (7.787 * y + 16.0/116.0);
    z = (z > 0.008856) ? pow(z, 1.0/3.0) : (7.787 * z + 16.0/116.0);
    
    // Calculate LAB values
    lab[0] = 116.0 * y - 16.0;    // L [0, 100]
    lab[1] = 500.0 * (x - y);     // a [-128, 127]
    lab[2] = 200.0 * (y - z);     // b [-128, 127]
}

// LAB to RGB conversion
inline void lab_to_rgb(const Point& lab, Point& rgb) {
    // Step 1: LAB to XYZ
    double y = (lab[0] + 16.0) / 116.0;
    double x = lab[1] / 500.0 + y;
    double z = y - lab[2] / 200.0;
    
    // Undo cube root transformation
    const double delta = 6.0/29.0;
    
    double x3 = pow(x, 3);
    double y3 = pow(y, 3);
    double z3 = pow(z, 3);
    
    x = (x > delta) ? x3 : (x - 16.0/116.0) / 7.787;
    y = (y > delta) ? y3 : (y - 16.0/116.0) / 7.787;
    z = (z > delta) ? z3 : (z - 16.0/116.0) / 7.787;
    
    // Using D65 white point reference
    const double xn = 0.95047;
    const double yn = 1.0;
    const double zn = 1.08883;
    
    // Scale back by white point
    x *= xn;
    y *= yn;
    z *= zn;
    
    // Step 2: XYZ to RGB
    double r = x *  3.2404542 + y * -1.5371385 + z * -0.4985314;
    double g = x * -0.9692660 + y *  1.8760108 + z *  0.0415560;
    double b = x *  0.0556434 + y * -0.2040259 + z *  1.0572252;
    
    // Apply inverse gamma correction (sRGB)
    r = (r > 0.0031308) ? (1.055 * pow(r, 1/2.4) - 0.055) : (12.92 * r);
    g = (g > 0.0031308) ? (1.055 * pow(g, 1/2.4) - 0.055) : (12.92 * g);
    b = (b > 0.0031308) ? (1.055 * pow(b, 1/2.4) - 0.055) : (12.92 * b);
    
    // Convert to RGB [0, 255] range and ensure values are in valid range
    rgb[0] = round(std::max(0.0, std::min(255.0, r * 255.0)));
    rgb[1] = round(std::max(0.0, std::min(255.0, g * 255.0)));
    rgb[2] = round(std::max(0.0, std::min(255.0, b * 255.0)));
}

#endif // COLOR_CONVERSION_H