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
    const static char* kOpenCLPlatformFlagShort;
    const static char* kOpenCLPlatformFlagLong;
    const static char* kOpenCLDeviceFlagShort;
    const static char* kOpenCLDeviceFlagLong;
    const static char* kHelpFlagShort;
    const static char* kHelpFlagLong;
    const static char* kStartFlagShort;
    const static char* kStartFlagLong;
    const static char* kFinishFlagShort;
    const static char* kFinishFlagLong;
	const static char* kAnimFlagShort;
	const static char* kAnimFlagLong;
	const static char* kDimensionsFlagShort;
	const static char* kDimensionsFlagLong;

	static MString openCLDirectory;
    
private:
    
    int _start = -1;
    int _finish = -1;
	std::vector<float> _animData;
    std::vector<int> _fixedKeyframes;
	std::vector<std::string> _dimensions;
    int openCLPlatformIndex;
    int openCLDeviceIndex;
    MStatus GatherCommandArguments(const MArgList& args);
};


#endif /* SelectCommand_hpp */
