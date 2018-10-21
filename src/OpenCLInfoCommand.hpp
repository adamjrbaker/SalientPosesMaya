//
//  OpenCLInfoCommand.hpp
//  SalientPosesMaya
//
//  Created by Richard Roberts on 12/10/18.
//

#ifndef OpenCLInfoCommand_hpp
#define OpenCLInfoCommand_hpp

#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>


class OpenCLInfoCommand : public MPxCommand {
public:
    OpenCLInfoCommand() {}
    virtual MStatus  doIt(const MArgList& args);
    virtual MStatus  undoIt() { return MS::kSuccess; }
    virtual MStatus  redoIt() { return MS::kSuccess; }
    virtual bool isUndoable() const { return false; }
    static void* creator() { return new OpenCLInfoCommand; }
    static MSyntax newSyntax();
    
    const static char* kName;
};



#endif /* OpenCLInfoCommand_hpp */
