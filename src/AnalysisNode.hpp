//
//  AnalysisNode.hpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

#ifndef AnalysisNode_hpp
#define AnalysisNode_hpp

#include <vector>

#include <maya/MPxNode.h>

#include "../SalientPosesPerformance/src/AnimationProxy.hpp"

class AnalysisNode : public MPxNode {
public:
    AnalysisNode() {}
    
    AnimationProxy getAnim(MDataBlock& data, MArrayDataHandle curvesHandle, int start, int nF, int nD);
    MStatus computeAnalysis(const MPlug& plug, MDataBlock& data, int mode);
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
    
    static void* creator() { return new AnalysisNode; }
    static MStatus initialize();
    
    static MTypeId id;
    static MObject iaMode;
    static MObject iaStart;
    static MObject iaEnd;
    static MObject iaCurveArray;
    static MObject oaErrorTable;
    static MObject oaIndexTable;
    static MString openCLDirectory;
    
};

#endif /* AnalysisNode_hpp */
