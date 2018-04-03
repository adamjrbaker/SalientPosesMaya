//
//  ReduceCommand.hpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 3/04/18.
//

#ifndef ReduceCommand_hpp
#define ReduceCommand_hpp

#include <vector>

#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>


class ReduceCommand : public MPxCommand {
public:
    ReduceCommand() {}
    virtual MStatus  doIt(const MArgList& args);
    virtual MStatus  undoIt() { return MS::kSuccess; }
    virtual MStatus  redoIt() { return MS::kSuccess; }
    virtual bool isUndoable() const { return false; }
    static void* creator() { return new ReduceCommand; }
    static MSyntax newSyntax();
    
    const static char* kName;
    const static char* kHelpFlagShort;
    const static char* kHelpFlagLong;
    const static char* kStartFlagShort;
    const static char* kStartFlagLong;
    const static char* kFinishFlagShort;
    const static char* kFinishFlagLong;
    const static char* kSelectionFlagShort;
    const static char* kSelectionFlagLong;
    
private:
    
    int _start = -1;
    int _finish = -1;
    std::vector<int> _selection;
    MStatus GatherCommandArguments(const MArgList& args);
};


#endif /* ReduceCommand_hpp */
