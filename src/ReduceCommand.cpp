//
//  ReduceCommand.cpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

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

#include <Eigen/Dense>

#include "../SalientPosesPerformance/src/Interpolator.hpp"
#include "MayaUtils.hpp"
#include "ReduceCommand.hpp"


// Set name and flags
const char* ReduceCommand::kName = "vuwReduceCommand";
const char* ReduceCommand::kStartFlagShort = "-s";
const char* ReduceCommand::kStartFlagLong = "-start";
const char* ReduceCommand::kFinishFlagShort = "-f";
const char* ReduceCommand::kFinishFlagLong = "-finish";
const char* ReduceCommand::kSelectionFlagShort = "-sel";
const char* ReduceCommand::kSelectionFlagLong = "-selection";
const char* ReduceCommand::kHelpFlagShort = "-h";
const char* ReduceCommand::kHelpFlagLong = "-help";

void DisplayHelp() {
    MString help;
    help += "Flags:\n";
    help += "-inputs (-i)         N/A        Inputs to the command.\n";
    help += "-help   (-h)         N/A        Display this text.\n";
    MGlobal::displayInfo(help);
}

MStatus ReduceCommand::doIt(const MArgList& args) {
    MStatus status;
    Log::print("COMPUTING INTERPOLATION");
    
    // Process arguments
    status = GatherCommandArguments(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    
    // Get current selection
    MSelectionList slist;
    MGlobal::getActiveSelectionList(slist);
    MItSelectionList iter(slist, MFn::kInvalid, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    
    // Ensure at least 1 thing is selected
    int n = slist.length();
    if (n == 0) {
        Log::error("Please select objects for reduction");
        return MS::kFailure;
    }
    
    // Ensure the start and end frames are given as argumetns
    if (_start == -1 || _finish == -1) {
        Log::error("The start and end flags have not been set (they cannot be set to -1).");
        return MS::kFailure;
    }
    
    // Ensure the selection contains at least two keyframes
    if (_selection.size() < 2) {
        Log::error("At least two keyframes must be selected.");
        return MS::kFailure;
    }
    
    int nFrames = _finish - _start + 1;
    
    MTime::Unit timeUnit = MayaConfig::getCurrentFPS();
    
    while (!iter.isDone()) {
        MObject mobj;
        iter.getDependNode(mobj);
        iter.next();
        
        // Find animated plugs connected to this node
        MFnDependencyNode dependNode(mobj);
        MPlugArray plugs;
        MAnimUtil::findAnimatedPlugs(mobj, plugs);
        
        // Iterate through each curve
        for (int k = 0; k < plugs.length(); k++) {
            MFnAnimCurve curve(plugs[k]);
            
            // Cache the curve data
            std::vector<float> data;
            for (int i = _start; i < _finish + 1; i++) {
                MTime time((double) (i), timeUnit);
                float v = curve.evaluate(time);
                data.push_back(v);
            }
            
            Interpolator interpolator = Interpolator::fromData(data, _selection, nFrames, _start);
            std::vector<Cubic> cubics = interpolator.getCubics();
            
            // Remove non-keyframes
            for (int j = _start; j < _finish + 1; j++) {
                bool j_in_sel = std::find(_selection.begin(), _selection.end(), j) != _selection.end();
                if (!j_in_sel) {
                    MTime t((double) j, timeUnit);
                    unsigned int ix = curve.findClosest(t);
                    curve.remove(ix);
                }
            }
            
            // Update tangents based on fitting
            for (int i = 0; i < _selection.size() - 1; i++) {
                Cubic cubic = cubics.at(i);
                int s = _selection[i];
                int e = _selection[i + 1];
                
                // Set outgoing for left keyframe
                uint ixLeft;
                MTime timeLeft((double) s, timeUnit);
                curve.find(timeLeft, ixLeft);
                curve.setWeightsLocked(ixLeft, false);
                curve.setTangentsLocked(ixLeft, false);
                curve.setAngle(ixLeft, MAngle(cubic.angleLeft()), false);
                curve.setWeight(ixLeft, cubic.weightLeft(), false);
                
                // Set incoming for right keyframe
                uint ixRight;
                MTime timeRight((double) e, timeUnit);
                curve.find(timeRight, ixRight);
                curve.setWeightsLocked(ixRight, false);
                curve.setTangentsLocked(ixRight, false);
                curve.setAngle(ixRight, MAngle(cubic.angleRight()), true);
                curve.setWeight(ixRight, cubic.weightRight(), true);
            }
        }
    }
    
    return MS::kSuccess;
}

MSyntax ReduceCommand::newSyntax() {
    MSyntax syntax;
    syntax.addFlag(kHelpFlagShort, kHelpFlagLong);
    syntax.addFlag(kStartFlagShort, kStartFlagLong, MSyntax::kLong);
    syntax.addFlag(kFinishFlagShort, kFinishFlagLong, MSyntax::kLong);
    syntax.addFlag(kSelectionFlagShort, kSelectionFlagLong, MSyntax::kLong);
    syntax.makeFlagMultiUse(kSelectionFlagShort);
    syntax.setObjectType(MSyntax::kSelectionList, 0, 255);
    syntax.useSelectionAsDefault(false);
    return syntax;
}

MStatus ReduceCommand::GatherCommandArguments(const MArgList& args) {
    MStatus status;
    MArgDatabase argData(syntax(), args);
    
    if (argData.isFlagSet(kHelpFlagShort)) {
        DisplayHelp();
        return MS::kSuccess;
    }
    
    if (argData.isFlagSet(kStartFlagShort)) {
        _start = argData.flagArgumentInt(kStartFlagShort, 0, &status);
    }
    
    if (argData.isFlagSet(kFinishFlagShort)) {
        _finish = argData.flagArgumentInt(kFinishFlagShort, 0, &status);
    }
    
    if (argData.isFlagSet(kSelectionFlagShort)) {
        
        uint numUses = argData.numberOfFlagUses(kSelectionFlagShort);
        for (uint i = 0; i < numUses; i++) {
            MArgList argList;
            status = argData.getFlagArgumentList(kSelectionFlagShort, i, argList);
            if (!status) {
                std::ostringstream os; os << "Failed to read " << kSelectionFlagLong << " at index=" << i;
                Log::print(os.str());
                return status;
            }
            int s = argList.asInt(0, &status);
            _selection.push_back(s);
        }
    }
    
    return MS::kSuccess;
}

