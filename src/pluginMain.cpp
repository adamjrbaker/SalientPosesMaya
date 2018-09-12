#include <sstream>

#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MString.h>
#include <maya/MStatus.h>

#include "AnalysisNode.hpp"
#include "SelectorNode.hpp"
#include "SelectCommand.hpp"
#include "ReduceCommand.hpp"
#include "MayaUtils.hpp"

MStatus initializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj, "Richard Roberts", "0.0.1", "201700");
    
    status = plugin.registerNode("vuwAnalysisNode", AnalysisNode::id, AnalysisNode::creator, AnalysisNode::initialize);
    if (status != MS::kSuccess) { Log::error("vuwAnalysisNode failed to register");  }
    
    status = plugin.registerNode("vuwSelectorNode", SelectorNode::id, SelectorNode::creator, SelectorNode::initialize);
    if (status != MS::kSuccess) { Log::error("vuwSelectorNode failed to register"); }
    
	status = plugin.registerCommand(SelectCommand::kName, SelectCommand::creator, SelectCommand::newSyntax);
	if (status != MS::kSuccess) { Log::error("vuwSelectCommand failed to register"); }

    status = plugin.registerCommand(ReduceCommand::kName, ReduceCommand::creator, ReduceCommand::newSyntax);
    if (status != MS::kSuccess) { Log::error("vuwReduceCommand failed to register"); }
    
	AnalysisNode::openCLDirectory = plugin.loadPath();
	SelectCommand::openCLDirectory = plugin.loadPath();

    return status;
}

MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj);
    
    status = plugin.deregisterNode(AnalysisNode::id);
    if (status != MS::kSuccess) { Log::error("vuwAnalysisNode failed to deregister"); }
    
    status = plugin.deregisterNode(SelectorNode::id);
    if (status != MS::kSuccess) { Log::error("vuwSelectorNode failed to deregister"); }
    
	status = plugin.deregisterCommand(SelectCommand::kName);
	if (status != MS::kSuccess) { Log::error("vuwSelectCommand failed to deregister"); }

    status = plugin.deregisterCommand(ReduceCommand::kName);
    if (status != MS::kSuccess) { Log::error("vuwReduceCommand failed to deregister"); }
    
    return status;
}
