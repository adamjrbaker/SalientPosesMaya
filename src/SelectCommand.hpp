//
//  SelectCommand.hpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 12/09/18.
//

#ifndef SelectCommand_hpp
#define SelectCommand_hpp

#include <vector>

#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>


class SelectCommand : public MPxCommand {
public:
    SelectCommand() {}
    virtual MStatus  doIt(const MArgList& args);
    virtual MStatus  undoIt() { return MS::kSuccess; }
    virtual MStatus  redoIt() { return MS::kSuccess; }
    virtual bool isUndoable() const { return false; }
    static void* creator() { return new SelectCommand; }
    static MSyntax newSyntax();
    
    const static char* kName;
    const static char* kHelpFlagShort;
    const static char* kHelpFlagLong;
    
private:
    
    MStatus GatherCommandArguments(const MArgList& args);
};


#endif /* SelectCommand_hpp */
