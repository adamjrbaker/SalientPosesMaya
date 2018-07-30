//
//  MayaUtils.cpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

#include <sstream>

#include <maya/MGlobal.h>

#include "MayaUtils.hpp"

/* Logging
 *
 * 0 - Maya global output only
 * 1 - Maya global output and standard output
 */
#define LOGGING 0

std::string mStringForErrorType(MStatus status) {
    if (status == MS::kSuccess) {
        return "Success";
    } else if (status == MS::kFailure) {
        return "Generic";
    } else if (status == MS::kInsufficientMemory) {
        return "InsufficientMemory";
    } else if (status == MS::kInvalidParameter) {
        return "InvalidParameter";
    } else if (status == MS::kLicenseFailure) {
        return "LicenseFailure";
    } else if (status == MS::kUnknownParameter) {
        return "UnknownParameter";
    } else if (status == MS::kNotImplemented) {
        return "NotImplemented";
    } else if (status == MS::kNotFound) {
        return "NotFound";
    } else if (status == MS::kEndOfFile) {
        return "endOfFile";
    } else {
        std::ostringstream os;
        os << status.statusCode();
        throw std::runtime_error("Status not understood (code=" + os.str() + ")");
    }
}

void Log::print(MString message) {
    if (LOGGING==1) std::cout << message << std::endl;
    MGlobal::displayInfo(message);
}

void Log::warning(MString message) {
    if (LOGGING == 1) std::cout << "WARNING: " << message << std::endl;
    MGlobal::displayWarning(message);
}

void Log::error(MString message) {
    if (LOGGING == 1) std::cerr << "ERROR: " << message << std::endl;
    MGlobal::displayError(message);
}

void Log::showStatus(MStatus status, std::string message) {
    std::string messageStr = message;
    
    if (status == MS::kSuccess) {
        print(MString(("Success: " + messageStr).c_str()));
        return;
    }
    
    std::string errorPart = status.errorString().asChar();
    std::string suffix = "[" + errorPart + "]";
    std::string errorString = mStringForErrorType(status) + ": " + messageStr + " " + suffix;
    error(MString(errorString.c_str()));
}

void Log::showStatus(MStatus status) {
    if (status == MS::kSuccess) {
        print(MString("Success"));
        return;
    }
    std::string errorString = mStringForErrorType(status) + status.errorString().asChar();
    error(MString(errorString.c_str()));
}

void Log::showStatusWhenError(MStatus status, std::string message) {
    if (status == MS::kSuccess) { return; }
    showStatus(status, message);
}

void Log::showStatusWhenError(MStatus status) {
    if (status == MS::kSuccess) { return; }
    showStatus(status);
}

void MayaCheck::objectIsPointArray(MObject obj) {
    MFn::Type type = obj.apiType();
    if (type != MFn::kPointArrayData) {
        std::ostringstream os; os << "Element was not of type MPointArray";
        throw std::runtime_error(os.str());
    }
}

void MayaCheck::objectIsFloatArray(MObject obj) {
    MFn::Type type = obj.apiType();
    if (type != MFn::kFloatArrayData) {
        std::ostringstream os; os << "Element was not of type MFloatArray";
        throw std::runtime_error(os.str());
    }
}

MTime::Unit MayaConfig::getCurrentFPS() {
    MString ret = MGlobal::optionVarStringValue(MString("workingUnitTime"));
         if (ret == MString("games"))     { return MTime::k15FPS; }
    else if (ret == MString("15fps"))     { return MTime::k15FPS; }
    else if (ret == MString("film"))      { return MTime::k24FPS; }
    else if (ret == MString("24fps"))     { return MTime::k24FPS; }
    else if (ret == MString("pal"))       { return MTime::k25FPS; }
    else if (ret == MString("25fps"))     { return MTime::k25FPS; }
    else if (ret == MString("ntsc"))      { return MTime::k30FPS; }
    else if (ret == MString("30fps"))     { return MTime::k30FPS; }
    // else if (ret == MString("ShowScan"))  { return MTime::k48FPS; }
    else if (ret == MString("48fps"))     { return MTime::k48FPS; }
    else if (ret == MString("palf"))      {  return MTime::k50FPS; }
    else if (ret == MString("50fps"))     { return MTime::k50FPS; }
    else if (ret == MString("ntscf"))     { return MTime::k60FPS; }
    else if (ret == MString("60fps"))     { return MTime::k60FPS; }
    else if (ret == MString("2fps")) { return MTime::k2FPS; }
    else if (ret == MString("3fps")) { return MTime::k3FPS; }
    else if (ret == MString("4fps")) { return MTime::k4FPS; }
    else if (ret == MString("5fps")) { return MTime::k5FPS; }
    else if (ret == MString("6fps")) { return MTime::k6FPS; }
    else if (ret == MString("8fps")) { return MTime::k8FPS; }
    else if (ret == MString("10fps")) { return MTime::k10FPS; }
    else if (ret == MString("12fps")) { return MTime::k12FPS; }
    else if (ret == MString("16fps")) { return MTime::k16FPS; }
    else if (ret == MString("20fps")) { return MTime::k20FPS; }
    else if (ret == MString("40fps")) { return MTime::k40FPS; }
    else if (ret == MString("75fps")) { return MTime::k75FPS; }
    else if (ret == MString("80fps")) { return MTime::k80FPS; }
    else if (ret == MString("100fps")) { return MTime::k100FPS; }
    else if (ret == MString("120fps")) { return MTime::k120FPS; }
    else if (ret == MString("125fps")) { return MTime::k125FPS; }
    else if (ret == MString("150fps")) { return MTime::k150FPS; }
    else if (ret == MString("200fps")) { return MTime::k200FPS; }
    else if (ret == MString("240fps")) { return MTime::k240FPS; }
    else if (ret == MString("250fps")) { return MTime::k250FPS; }
    else if (ret == MString("300fps")) { return MTime::k300FPS; }
    else if (ret == MString("375fps")) { return MTime::k375FPS; }
    else if (ret == MString("400fps")) { return MTime::k400FPS; }
    else if (ret == MString("500fps")) { return MTime::k500FPS; }
    else if (ret == MString("600fps")) { return MTime::k600FPS; }
    else if (ret == MString("750fps")) { return MTime::k750FPS; }
    else if (ret == MString("1200fps")) { return MTime::k1200FPS; }
    else if (ret == MString("1500fps")) { return MTime::k1500FPS; }
    else if (ret == MString("2000fps")) { return MTime::k2000FPS; }
    else if (ret == MString("3000fps")) { return MTime::k3000FPS; }
    else if (ret == MString("6000fps")) { return MTime::k6000FPS; }
    else if (ret == MString("44100fps")) { return MTime::k44100FPS; }
    else if (ret == MString("48000fps")) { return MTime::k48000FPS; }
    else if (ret == MString("23.97fps")) { return MTime::k23_976FPS; }
    else if (ret == MString("29.97df")) { return MTime::k29_97DF; }
    else if (ret == MString("29.97fps")) { return MTime::k29_97FPS; }
    else if (ret == MString("47.952fps")) { return MTime::k47_952FPS; }
    else if (ret == MString("59.94fps")) { return MTime::k59_94FPS; }
    
    else {
        Log::error("FPS setting not understood: " + ret);
        return MTime::kFilm;
    }
}
