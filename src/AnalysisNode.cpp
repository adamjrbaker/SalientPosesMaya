//
//  AnalysisNode.cpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

#include "AnalysisNode.hpp"

#include <sstream>
#include <stdexcept>
#include <vector>

#include <maya/MStatus.h>
#include <maya/MDataBlock.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MDataHandle.h>
#include <maya/MFnPointArrayData.h>
#include <maya/MPointArray.h>
#include <maya/MFnFloatArrayData.h>
#include <maya/MFloatArray.h>
#include <maya/MOpenCLInfo.h>

#include "MayaUtils.hpp"
#include "AnalysisNode.hpp"
#include "ErrorTable.hpp"

/* Logging
 *
 * 0 - no output
 * 1 - log animation data
 * 2 - log error table
 */
#define LOGGING 0

MString AnalysisNode::openCLDirectory;

MTypeId AnalysisNode::id( 0x0012c2c0 );
MObject AnalysisNode::iaStart;
MObject AnalysisNode::iaEnd;
MObject AnalysisNode::iaCurveArray;
MObject AnalysisNode::oaErrorTable;

MStatus AnalysisNode::initialize() {
    MFnNumericAttribute nAttr;
    MFnTypedAttribute tAttr;
    
    oaErrorTable = tAttr.create("errorTable", "table", MFnData::kFloatArray);
    tAttr.setWritable(false);
    tAttr.setReadable(true);
    tAttr.setStorable(true);
    addAttribute(oaErrorTable);
    
    iaStart = nAttr.create("start", "s", MFnNumericData::kInt);
    nAttr.setReadable(true);
    nAttr.setWritable(true);
    nAttr.setStorable(true);
    addAttribute(iaStart);
    attributeAffects(iaStart, oaErrorTable);
    
    iaEnd = nAttr.create("end", "e", MFnNumericData::kInt);
    nAttr.setReadable(true);
    nAttr.setWritable(true);
    nAttr.setStorable(true);
    addAttribute(iaEnd);
    attributeAffects(iaEnd, oaErrorTable);
    
    iaCurveArray = tAttr.create("curveArray", "curves", MFnData::kPointArray);
    tAttr.setReadable(true);
    tAttr.setArray(true);
    tAttr.setStorable(true);
    addAttribute(iaCurveArray);
    
    return MS::kSuccess;
}

AnimationProxy AnalysisNode::getAnim(MDataBlock& data, MArrayDataHandle curvesHandle, int start, int nF, int nD) {
    MStatus status;
    MDataHandle curveHandle = curvesHandle.inputValue();
    MObject obj = curveHandle.data();
    
    int end = start + nF - 1;
    
    std::vector<float> anim(nF * nD, 0);
    std::vector<std::string> dimensions;
    dimensions.push_back("time");
    
    // Iterate over curves
    for (int curveIndex = 0; curveIndex < curvesHandle.elementCount(); curveIndex++) {
        
        // Make up names for the dimensions
        std::ostringstream osx; osx << "curve-" << curveIndex << "-x"; dimensions.push_back(osx.str());
        std::ostringstream osy; osy << "curve-" << curveIndex << "-y"; dimensions.push_back(osy.str());
        std::ostringstream osz; osz << "curve-" << curveIndex << "-z"; dimensions.push_back(osz.str());

        // Get data for this element from the iterator.
        curveHandle = curvesHandle.inputValue();
        obj = curveHandle.data();
        
        // Check data is a motion curve (point array)
        MayaCheck::objectIsPointArray(obj);
        
        // Read point array from motion curve
        MFnPointArrayData pointArrayData(obj, &status);
        if (status != MS::kSuccess) {
            std::ostringstream os; os << "Failed to read motion curve at index: " << curveIndex;
            Log::showStatusWhenError(status, os.str());
        }
        
        // Iterate through points (frames) of motion curve
        MPointArray pointArray = pointArrayData.array();
        for (int frameIndex = 0; frameIndex < nF; frameIndex++) {
            
            // Set time dimension
            if (curveIndex == 0) {
                int animDataIndex = frameIndex * nD;
                anim[animDataIndex] = 1.0f * (start + frameIndex); // ensure float
            }
            
            int animDataIndex = frameIndex * nD + 1 + curveIndex * 3;
            MPoint point = pointArray[frameIndex];
            anim[animDataIndex + 0] = point.x;
            anim[animDataIndex + 1] = point.y;
            anim[animDataIndex + 2] = point.z;
        }
        
        curvesHandle.next();
    }
    
    // Log the animation data when required
    if (LOGGING == 1) {
        Log::print(std::string("Animation Data:"));
        Log::arrayAsMatrix(anim.data(), nF, nD);
    }
    
    return AnimationProxy::fromData(anim, dimensions, start, end);
}

MStatus AnalysisNode::computeAnalysis(const MPlug& plug, MDataBlock& data) {
    MStatus status;
    
    // Get array handle for "input" attribute.
    MArrayDataHandle curvesHandle = data.inputArrayValue(iaCurveArray);
    curvesHandle.jumpToArrayElement(0);
    
    int startValue = data.inputValue(iaStart).asInt();
    int endValue = data.inputValue(iaEnd).asInt();
    int nFrames = endValue - startValue + 1;
    int n = curvesHandle.elementCount();
    int nDimensions = 1 + n * 3; // time + 3 positions for each joint
    
    // Get animation data from input
    AnimationProxy anim = getAnim(data, curvesHandle, startValue, nFrames, nDimensions);
    
    // Compute the error table
    std::string openCLPath = openCLDirectory.asChar();
    openCLPath += "/kernel.cl";
    std::ostringstream os; os << "Running OpenCL using " << openCLPath << std::endl;
    ErrorTable anal = ErrorTable::fromAnim(anim, openCLPath, "max_distance_to_polyline");

    // Format error table data as MObject
    MFnFloatArrayData mArrayData;
    MObject mobj = mArrayData.create(MFloatArray(anal.asData().data(), nFrames * nFrames));
    
    // Set output
    MDataHandle outHandle = data.outputValue(oaErrorTable);
    outHandle.set(mobj);
    outHandle.setClean();
    
    return MS::kSuccess;
}

MStatus AnalysisNode::compute(const MPlug& plug, MDataBlock& data) {
    if (plug == oaErrorTable) {
        Log::print("COMPUTING ANALYSIS");
        return computeAnalysis(plug, data);
    } else {
        return MS::kUnknownParameter;
    }
}
