//
//  MayaUtils.hpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

#ifndef MayaUtils_hpp
#define MayaUtils_hpp

#include <maya/MString.h>
#include <maya/MObject.h>
#include <maya/MStatus.h>
#include <maya/MTime.h>

class Log {
public:
    static void print(MString message);
    static void warning(MString message);
    static void error(MString message);
    
    static void print(std::string message) { print(MString(message.c_str())); }
    static void warning(std::string message) { warning(MString(message.c_str())); }
    static void error(std::string message) { error(MString(message.c_str())); }
    
    static void print(const char* message) { print(MString(message)); }
    static void warning(const char* message) { warning(MString(message)); }
    static void error(const char* message) { error(MString(message)); }
    
    static void showStatus(MStatus status, std::string message);
    static void showStatusWhenError(MStatus status, std::string message);
    static void showStatus(MStatus status);
    static void showStatusWhenError(MStatus status);
    
    template <typename T>
    static void arrayAsMatrix(T *data, int nCols, int nRows) {
        std::ostringstream os;
        for (int i = 0; i < nCols; i++) {
            os << i << " = [";
            for (int j = 0; j < nRows; j++) {
                int index = i * nRows + j;
                os  << data[index] << ",";
            }
            os << "]\n";
        }
        Log::print(MString(os.str().c_str()));
    }
};

class MayaCheck {
public:
    static void objectIsPointArray(MObject obj);
    static void objectIsFloatArray(MObject obj);
};

class MayaConfig {
public:
    static MTime::Unit getCurrentFPS();
};


#endif /* MayaUtils_hpp */
