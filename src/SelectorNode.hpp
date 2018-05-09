//
//  SelectorNode.hpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

/*
 * Node Attributes
 *   input: iaStart - the start of the section that keyframe selection should be performed on
 *   input: iaEnd - the end of that section
 *   input: iaErrorTable - an error table from an AnalysisNode
 *   input: iaNKeyframes - an integer denoting the number of keyframes to use in the presented selection
 *   output: oaSelections - the set of all selections
 *   output: oaSelection - the keyframes of the presented selection, represented as an array of integers
 */

#ifndef SelectorNode_hpp
#define SelectorNode_hpp

#include <vector>

#include <maya/MPxNode.h>

class SelectorNode : public MPxNode {
public:
    SelectorNode() {}
    
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
    static void* creator() { return new SelectorNode; }
    static MStatus initialize();
    
    static MTypeId id;
    static MObject iaStart;
    static MObject iaEnd;
    static MObject iaStartOffset;
    static MObject iaNFramesTotal;
    static MObject iaErrorTable;
    static MObject iaMode;
    static MObject iaNKeyframes;
    static MObject oaSelectionErrors;
    static MObject oaSelection;
    
};

#endif /* SelectorNode_hpp */
