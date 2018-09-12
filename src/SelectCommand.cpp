//
//  SelectCommand.cpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 12/09/18.
//

#include <iomanip>
#include <sstream>
#include <vector>

#include <maya/MGlobal.h>
#include <maya/MArgDatabase.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnDagNode.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MItSelectionList.h>
#include <maya/MAnimUtil.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MTime.h>
#include <maya/MFnIntArrayData.h>
#include <maya/MDataHandle.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MAngle.h>

#include "../SalientPosesPerformance/src/OpenCLProcess.hpp"
#include "SelectCommand.hpp"
#include "MayaUtils.hpp"
#include "../SalientPosesPerformance/src/ErrorTable.hpp"
#include "../SalientPosesPerformance/src/SelectionManager.hpp"

#define RAD_TO_DEG 57.2958279088

MString SelectCommand::openCLDirectory;

// Set name and flags
const char* SelectCommand::kName = "salientSelect";
const char* SelectCommand::kOpenCLPlatformFlagShort = "-clp";
const char* SelectCommand::kOpenCLPlatformFlagLong = "-clplatform";
const char* SelectCommand::kOpenCLDeviceFlagShort = "-cld";
const char* SelectCommand::kOpenCLDeviceFlagLong = "-cldevice";
const char* SelectCommand::kStartFlagShort = "-s";
const char* SelectCommand::kStartFlagLong = "-start";
const char* SelectCommand::kFinishFlagShort = "-f";
const char* SelectCommand::kFinishFlagLong = "-finish";
const char* SelectCommand::kAnimFlagShort = "-a";
const char* SelectCommand::kAnimFlagLong = "-anim";
const char* SelectCommand::kDimensionsFlagShort = "-d";
const char* SelectCommand::kDimensionsFlagLong = "-dimensions";
const char* SelectCommand::kHelpFlagShort = "-h";
const char* SelectCommand::kHelpFlagLong = "-help";


MStatus SelectCommand::doIt(const MArgList& args) {
    MStatus status;
    
    // Process arguments
    status = GatherCommandArguments(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    
    // Set OpenCL platform and device
    OpenCLProcessManager::setPlatformIdToPlatformAtIndex(openCLPlatformIndex - 1);
    OpenCLProcessManager::setDeviceIdToDeviceAtIndex(openCLDeviceIndex - 1);
    
    // Ensure the start and end frames are given as argumetns
    if (_start == -1 || _finish == -1) {
		std::ostringstream os;
		os << "The start and end flags have not been set (start=" << _start << " end=" << _finish << ")";
        Log::error(os.str());
        return MS::kFailure;
    }
    
    // Perform the selection
    std::string openclProgramPath = openCLDirectory.asChar() + std::string("/kernel.cl");
    std::string openclProgramName = "max_distance_to_polyline";
	AnimationProxy anim = AnimationProxy::fromData(_animData, _dimensions, _start, _finish);
    SelectionManager manager = SelectionManager(anim, _fixedKeyframes.data(), _fixedKeyframes.size(),
                                                openclProgramPath, openclProgramName);
    manager.incrementUntilNKeyframes(anim.nFrames);
    SelectionProxy * selectionProxy = manager.asProxy();

    // Build string containing result (precise to four decimal places)
    std::ostringstream ret;
    ret << std::setprecision(4) << std::fixed;

    // Pipe in pairs of error and selection in the form:
    //   e|a,b,c
    //     where e is error, | is a delimiter, and a,b,c are the selection (wthout spaces).
    // Each error-selection pair is delimited by a new line.
    for (int i = 0; i < selectionProxy->numberOfSelections(); i++) {
        std::vector<int> selection = selectionProxy->getSelectionByIndex(i);
        ret << selectionProxy->getErrorByIndex(i) << "|";
        ret << selection[0];
        for (int j = 1; j < selection.size(); j++) {
            ret << "," << selection[j];
        }
        ret << "\n";
    }

	setResult(MString(ret.str().c_str()));

	delete selectionProxy;
    return MS::kSuccess;
}

MSyntax SelectCommand::newSyntax() {
    MSyntax syntax;
    syntax.addFlag(kHelpFlagShort, kHelpFlagLong);
    syntax.addFlag(kOpenCLPlatformFlagShort, kOpenCLPlatformFlagLong, MSyntax::kLong);
    syntax.addFlag(kOpenCLDeviceFlagShort, kOpenCLDeviceFlagLong, MSyntax::kLong);
    syntax.addFlag(kStartFlagShort, kStartFlagLong, MSyntax::kLong);
    syntax.addFlag(kFinishFlagShort, kFinishFlagLong, MSyntax::kLong);
	syntax.addFlag(kAnimFlagShort, kAnimFlagLong, MSyntax::kDouble);
	syntax.makeFlagMultiUse(kAnimFlagShort);
	syntax.addFlag(kDimensionsFlagShort, kDimensionsFlagLong, MSyntax::kLong);
	syntax.makeFlagMultiUse(kDimensionsFlagShort);
    syntax.addFlag(kDimensionsFlagShort, kDimensionsFlagLong, MSyntax::kLong);
    syntax.setObjectType(MSyntax::kSelectionList, 0, 255);
    syntax.useSelectionAsDefault(false);
    return syntax;
}

MStatus SelectCommand::GatherCommandArguments(const MArgList& args) {
	MStatus status;

	unsigned int ix = 0;
    
    openCLPlatformIndex = args.asInt(ix, &status);
    ix += 1;
    openCLDeviceIndex = args.asInt(ix, &status);
    ix += 1;

	_start = args.asInt(ix,&status);
	ix += 1;
	_finish = args.asInt(ix, &status);
	ix += 1;
	MDoubleArray mAnimData = args.asDoubleArray(ix, &status);
	ix += 1;
	MStringArray mDimensions = args.asStringArray(ix, &status);
    ix += 1;
    MIntArray mFixedKeyframes = args.asIntArray(ix, &status);
    ix += 1;
    
	for (uint i = 0; i < mAnimData.length(); i++) {
		_animData.push_back(mAnimData[i]);
	}

	for (uint i = 0; i < mDimensions.length(); i++) {
		_dimensions.push_back(mDimensions[i].asChar());
	}
    
    for (uint i = 0; i < mFixedKeyframes.length(); i++) {
        _fixedKeyframes.push_back(mFixedKeyframes[i]);
    }
    
    return MS::kSuccess;
}

