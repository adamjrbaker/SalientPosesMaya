//
//  OpenCLInfoCommand.cpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 12/10/18.
//

#include <sstream>
#include <vector>

#include <maya/MGlobal.h>

#include "../SalientPosesPerformance/src/OpenCLProcess.hpp"
#include "OpenCLInfoCommand.hpp"

// Set name and flags
const char* OpenCLInfoCommand::kName = "salientOpenCLInfo";

MStatus OpenCLInfoCommand::doIt(const MArgList& args) {
    MStatus status;
    std::vector<std::string> info = OpenCLProcessManager::getInfo();
    std::string ret = "";
    for (int i = 0; i < info.size(); i++) {
        ret += info[i] + "\n";
    }
    setResult(MString(ret.c_str()));
    return MS::kSuccess;
}

MSyntax OpenCLInfoCommand::newSyntax() {
    MSyntax syntax;
    return syntax;
}
