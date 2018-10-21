# Example usage for Mixamo animation, run from Maya's script editor
# 
# import os
# import sys; sys.path.append("path/to/this/folder);
# import salient_runner as r; reload(r); r._reload()
# for_selection = [u'mixamorig:Hips', u'mixamorig:Spine', u'mixamorig:Spine1', u'mixamorig:Spine2', u'mixamorig:Neck', u'mixamorig:Head', u'mixamorig:HeadTop_End', u'mixamorig:LeftShoulder', u'mixamorig:LeftArm', u'mixamorig:LeftForeArm', u'mixamorig:LeftHand', u'mixamorig:RightShoulder', u'mixamorig:RightForeArm', u'mixamorig:RightArm', u'mixamorig:RightHand', u'mixamorig:LeftUpLeg', u'mixamorig:LeftLeg', u'mixamorig:LeftFoot', u'mixamorig:LeftToeBase', u'mixamorig:LeftToe_End', u'mixamorig:RightUpLeg', u'mixamorig:RightLeg', u'mixamorig:RightFoot', u'mixamorig:RightToeBase', u'mixamorig:RightToe_End']
# for_reduction = [u'mixamorig:Hips', u'mixamorig:Spine', u'mixamorig:Spine1', u'mixamorig:Spine2', u'mixamorig:Neck', u'mixamorig:Head', u'mixamorig:HeadTop_End', u'mixamorig:LeftEye', u'mixamorig:RightEye', u'mixamorig:LeftShoulder', u'mixamorig:LeftArm', u'mixamorig:LeftForeArm', u'mixamorig:LeftHand', u'mixamorig:LeftHandThumb1', u'mixamorig:LeftHandThumb2', u'mixamorig:LeftHandThumb3', u'mixamorig:LeftHandThumb4', u'mixamorig:LeftHandIndex1', u'mixamorig:LeftHandIndex2', u'mixamorig:LeftHandIndex3', u'mixamorig:LeftHandIndex4', u'mixamorig:LeftHandMiddle1', u'mixamorig:LeftHandMiddle2', u'mixamorig:LeftHandMiddle3', u'mixamorig:LeftHandMiddle4', u'mixamorig:LeftHandRing1', u'mixamorig:LeftHandRing2', u'mixamorig:LeftHandRing3', u'mixamorig:LeftHandRing4', u'mixamorig:LeftHandPinky1', u'mixamorig:LeftHandPinky2', u'mixamorig:LeftHandPinky3', u'mixamorig:LeftHandPinky4', u'mixamorig:RightShoulder', u'mixamorig:RightArm', u'mixamorig:RightForeArm', u'mixamorig:RightHand', u'mixamorig:RightHandPinky1', u'mixamorig:RightHandPinky2', u'mixamorig:RightHandPinky3', u'mixamorig:RightHandPinky4', u'mixamorig:RightHandRing1', u'mixamorig:RightHandRing2', u'mixamorig:RightHandRing3', u'mixamorig:RightHandRing4', u'mixamorig:RightHandMiddle1', u'mixamorig:RightHandMiddle2', u'mixamorig:RightHandMiddle3', u'mixamorig:RightHandMiddle4', u'mixamorig:RightHandIndex1', u'mixamorig:RightHandIndex2', u'mixamorig:RightHandIndex3', u'mixamorig:RightHandIndex4', u'mixamorig:RightHandThumb1', u'mixamorig:RightHandThumb2', u'mixamorig:RightHandThumb3', u'mixamorig:RightHandThumb4', u'mixamorig:LeftUpLeg', u'mixamorig:LeftLeg', u'mixamorig:LeftFoot', u'mixamorig:LeftToeBase', u'mixamorig:LeftToe_End', u'mixamorig:RightUpLeg', u'mixamorig:RightLeg', u'mixamorig:RightFoot', u'mixamorig:RightToeBase', u'mixamorig:RightToe_End']
# r.run_on_directory(for_selection, for_reduction, save_fbx=True, save_maya_ascii=True, save_csv=True)
#

from os import listdir
from os.path import isfile, join

import maya.cmds as cmds
import maya.mel as mel

import salient_utils
import salient_api

def _reload():
    reload(salient_utils)
    reload(salient_api)

def export_meta_information(filepath, start, end, title):

    header = "start,end,title\n"
    body = "%d,%d,%s\n" % (start, end, title)

    # Combine the header and body and save to file
    csv_string = header + body
    f = open(filepath, "w")
    f.write(csv_string)
    f.close()


def export_animation_data_as_csv(filepath, objects, start, end):
    """
    Gets the animation data as a table, where rows are frames and columns are dimensions
    """
    # Attach proxies
    proxies = []
    for object in objects:
        proxy = cmds.spaceLocator()[0]
        cmds.parentConstraint(object, proxy)
        proxies.append(proxy)

    # Create the csv header (list of dimensions)
    header = ""
    for object in objects:
        header += "%s.x,%s.y,%s.z," % (object, object, object)
    header = header[:-1] + "\n"

    # Create the csv body (world-space position of proxies)    
    body = ""
    for i in range(start, end + 1):
        frame = ""
        for object in proxies:
            x, y, z = cmds.getAttr("%s.worldMatrix" % object, time=i)[12:15]
            frame += "%2.7f,%2.7f,%2.7f," % (x, y, z)
        body += frame[:-1] + "\n"
    
    # Clean up
    cmds.delete(proxies)

    # Combine the header and body and save to file
    csv_string = header + body
    f = open(filepath, "w")
    f.write(csv_string)
    f.close()

def run_on_fbx_file(directory, filename, objects_for_selection, objects_for_reduction, cl_selected_device_str="", save_maya_ascii=False, save_fbx=False, save_csv=False):

    # Choose OpenCL device
    if cl_selected_device_str == "":
        cl_selected_device_str = salient_utils.Prompt.get_string("Choose OpenCL device", "Enter device index:")
        if cl_selected_device_str is None:
            return
        else:
            cl_selected_device_str = cl_selected_device_str
    cl_platform_ix_str, cl_device_ix_str = cl_selected_device_str.split(".")
    cl_platform_ix = int(cl_platform_ix_str)
    cl_device_ix = int(cl_device_ix_str)

    # Start a new file
    cmds.file(new=True, force=True)

    # Import the fbx
    mel.eval("FBXImport -file \"%s/%s\"" % (directory, filename))
    
    # Get the start and end frame from the timeline
    start = int(cmds.playbackOptions(query=True, minTime=True))
    end = int(cmds.playbackOptions(query=True, maxTime=True))

    if save_maya_ascii:
        # Save the original as a Maya ASCII file
        cmds.file(rename=directory + "/%s-%d-keyframes.ma" % (filename, end - start + 1))
        cmds.file(save=True, type='mayaAscii')

    cmds.bakeResults(objects_for_reduction, t=(start, end), sampleBy=1, minimizeRotation=True, preserveOutsideKeys=True)

    if save_csv:
        # Save the original as a CSV file
        title = filename.replace(".fbx", "").replace("_", " ")
        export_meta_information(directory + "/meta.csv", start, end, title)
        export_animation_data_as_csv(directory + "/%s-%d-keyframes.csv" % (filename, end - start + 1), objects_for_selection, start, end)

    if save_fbx:
        # Save the original version as an FBX    
        mel.eval("FBXExport -f \"%s\"" % (directory + "/%s-%d-keyframes.fbx" % (filename, end - start + 1)))

    # Perform selection
    cmds.select(objects_for_selection, replace=True)
    selections = salient_api.select_keyframes(cl_platform_ix, cl_device_ix, start, end, []) # no fixed keyframes

    # Set choices of keyframes for compression @ 80%, 90%, 95%, and 97.5%
    n_frames = end - start + 1
    choices_of_n_keyframes = [
        int(round(n_frames * 0.2)),
        int(round(n_frames * 0.1)),
        int(round(n_frames * 0.05)),
        int(round(n_frames * 0.025)),
    ]
    
    # Perform each reduction
    for n_keyframes in choices_of_n_keyframes:

        # Skip the selection if too few keyframes
        if n_keyframes <= 2: continue

        # Create a new file and import the fbx
        cmds.file(new=True, force=True)
        mel.eval("FBXImport -file \"%s/%s\"" % (directory, filename))
        
        # Perform the reduction
        selection = selections[n_keyframes]["selection"]
        cmds.select(objects_for_reduction, replace=True)
        salient_api.reduce_keyframes(selection)

        # Set output filepath
        compression = 1 - float(n_keyframes) / n_frames
        suffix = " compressed %2.4f (%d keyframes left from %d)" % (compression, n_keyframes, n_frames)
        outputFilepathNoExtension = "%s%s" % (directory + filename.replace(".fbx", ""), suffix)
        
        if save_maya_ascii:
            # Save the compressed version as a Maya ASCII
            cmds.file(rename=directory + "/%s-%d-keyframes.ma" % (filename, n_keyframes))
            cmds.file(save=True, type='mayaAscii')

        # Bake the result
        cmds.bakeResults(objects_for_reduction, t=(start, end), sampleBy=1, minimizeRotation=True, preserveOutsideKeys=True)

        if save_csv:
            # Save the compressed version as a CSV
            export_animation_data_as_csv(directory + "/%s-%d-keyframes.csv" % (filename, n_keyframes), objects_for_selection, start, end)

        if save_fbx:
            # Save the compressed version as an FBX    
            mel.eval("FBXExport -f \"%s\"" % (directory + "/%s-%d-keyframes.fbx" % (filename, n_keyframes)))


def run_on_directory(objects_for_selection, objects_for_reduction, directory="", cl_selected_device_str="",
    save_maya_ascii=False, save_fbx=False, save_csv=False):

    # Choose directory
    if directory == "":
        directory = salient_utils.Prompt.get_folder("Choose a directory (must contain FBX files):")
        if directory is None:
            return
    
    filename = directory.split("/")[-1] + ".fbx"
    run_on_fbx_file(directory, filename, objects_for_selection, objects_for_reduction, cl_selected_device_str, save_maya_ascii=save_maya_ascii, save_fbx=save_fbx, save_csv=save_csv)
        