import os

import maya.cmds as cmds
import cmt.shortcuts as shortcuts
from cmt.test import TestCase

from salient_poses_utils import MayaScene


def baked_ball_anim_from_keyframes_and_poses(keyframes, poses):
        obj = cmds.polySphere(r=1, sx=20, sy=20)[0]
        s, e = keyframes[0], keyframes[-1]

        def move_and_set_keyframe(time, position):
            cmds.currentTime(time)
            x, y, z = position
            cmds.move(x, y, z, absolute=True)
            cmds.setKeyframe("%s.translate" % obj);

        for (k, pose) in zip (keyframes, poses):
            move_and_set_keyframe(k, pose)

        MayaScene.bake_translation(obj, s, e)
        return obj

def create_simple_arc_animation_for_sphere(s, e):
    m = s + int((e - s) * 0.5)
    keyframes = [s, m, e]
    poses = [ (-12.0,   0.0,   0.0)
            , (  0.0,   8.0,   0.0)
            , ( 12.0,   0.0,   0.0) ]
    return baked_ball_anim_from_keyframes_and_poses(keyframes, poses)

def create_sin_animation_for_sphere(s, e):
    keyframes = [ s
                , int((e - s) * 0.25)
                , int((e - s) * 0.5)
                , int((e - s) * 0.75)
                , e]
    poses = [ (-12.0,   0.0,   0.0)
            , ( -6.0,   8.0,   0.0)
            , (  0.0,   0.0,   0.0)
            , (  6.0,  -8.0,   0.0)
            , ( 12.0,   0.0,   0.0) ]
    return baked_ball_anim_from_keyframes_and_poses(keyframes, poses)

def make_analysis_and_selector_node(obj, min_frame, max_frame, sel_from, sel_to):
    anim_snapshot = MayaScene.make_motion_curves([obj], "curves", min_frame, max_frame)
    curves = MayaScene.get_items_in_list_matching_type(anim_snapshot, "motionTrail")
    analysis_node_name = cmds.createNode("vuwAnalysisNode")
    cmds.setAttr("%s.start" % analysis_node_name, min_frame)
    cmds.setAttr("%s.end" % analysis_node_name, max_frame)
    MayaScene.connect_attribute_list(analysis_node_name, "curves", curves, "points")
    MayaScene.provoke_attribute(analysis_node_name, "errorTable")

    selector_node_name = cmds.createNode("vuwSelectorNode")
    cmds.setAttr("%s.startOffset" % selector_node_name, sel_from - min_frame)
    cmds.setAttr("%s.framesTotal" % selector_node_name, max_frame - min_frame + 1)
    cmds.setAttr("%s.start" % selector_node_name, sel_from)
    cmds.setAttr("%s.end" % selector_node_name, sel_to)
    cmds.setAttr("%s.nKeyframes" % selector_node_name, 3)
    cmds.connectAttr("%s.errorTable" % analysis_node_name, "%s.errorTable" % selector_node_name)

    return anim_snapshot, analysis_node_name, selector_node_name

def get_expected_as_string(name):
    directory = os.path.dirname(os.path.abspath(__file__))
    with open("%s/expected/%s.out" % (directory, name), 'r') as f:
        return f.read()

def get_expected_as_list_of_floats(name):
    return [float(v) for v in get_expected_as_string(name)[1:-1].split(",")] 

def get_expected_as_list_of_ints(name):
    return [int(v) for v in get_expected_as_string(name)[1:-1].split(",")]

def selections_from_cache(cache, nframes):
    selections = [[], []]
    for nk in range(2, nframes + 1):
        sel = []
        for i in range(nk):
            cache_ix = nframes * nk + i 
            sel.append(cache[cache_ix])
        selections.append(sel)
    return selections

class SalientPosesTests(TestCase):

    # Ensure all selections start and end with the same frames and each
    # successive selection is one greater than the previous
    # 
    # Note: skip the first two selections in the cache (which are invalid nk=0 and nk=1)
    def assertSelectionsAreValid(self, selectionCache, nframes):
        selections = selections_from_cache(selectionCache, nframes)
        s = selections[2][0]
        e = selections[2][-1]
        for sel in selections[2:]:
            self.assertTrue(s == sel[0])
            self.assertTrue(e == sel[-1])
        for i in range(2, len(selections) - 1):
            self.assertTrue(len(selections[i+1]) - len(selections[i]) == 1)

    # Ensure monotonically decreasing (or equal) errors and that 
    # the last error = 0
    #
    # Note: skip the first two errors in the cache (which are invalid nk=0 and nk=1)
    def assertSelectionErrorsValid(self, errors):
        for i in range(2, len(errors) - 1): self.assertTrue (errors[i+1] <= errors[i])
        self.assertTrue(errors[-1] == 0)

        
    def test_load_unload(self):
        cmds.loadPlugin("SalientPosesMaya")
        cmds.unloadPlugin("SalientPosesMaya")

    def test_analysis_node(self):
        cmds.loadPlugin("SalientPosesMaya")

        min_frame, max_frame = 1, 11
        obj = create_simple_arc_animation_for_sphere(min_frame, max_frame)
        anim_snapshot = MayaScene.make_motion_curves([obj], "curves", min_frame, max_frame)
        curves = MayaScene.get_items_in_list_matching_type(anim_snapshot, "motionTrail")
        analysis_node_name = cmds.createNode("vuwAnalysisNode")
        cmds.setAttr("%s.start" % analysis_node_name, min_frame)
        cmds.setAttr("%s.end" % analysis_node_name, max_frame)
        MayaScene.connect_attribute_list(analysis_node_name, "curves", curves, "points")
        errorTable = MayaScene.provoke_attribute(analysis_node_name, "errorTable")
        MayaScene.delete([analysis_node_name, obj] + anim_snapshot)
        cmds.flushUndo()
        cmds.unloadPlugin("SalientPosesMaya")

        expected = get_expected_as_list_of_floats("test_analysis_node")
        self.assertListAlmostEqual(errorTable, expected)

    def test_selector_node(self):
        cmds.loadPlugin("SalientPosesMaya")

        # Create scene
        min_frame, max_frame = 1, 11
        sel_from, sel_to = 1, 11
        obj = create_simple_arc_animation_for_sphere(min_frame, max_frame)
        anim_snapshot, analysis, selector = make_analysis_and_selector_node(obj, min_frame, max_frame, sel_from, sel_to)
        
        # Note that selection must be provoked before errors
        selection = MayaScene.provoke_attribute(selector, "selection")
        errors = MayaScene.provoke_attribute(selector, "errors")

        # Clean up
        MayaScene.delete([analysis, selector, obj] + anim_snapshot)
        cmds.flushUndo()
        cmds.unloadPlugin("SalientPosesMaya")

        # Inspection
        self.assertSelectionsAreValid(selection, max_frame - min_frame + 1)
        self.assertSelectionErrorsValid(errors)
        expected = get_expected_as_list_of_ints("test_selector_node_selection")
        self.assertListEqual([int(v) for v in selection], expected)
        expected = get_expected_as_list_of_floats("test_selector_node_errors")
        self.assertListAlmostEqual(errors, expected)

    def test_selector_node_sub_sel_a(self):
        cmds.loadPlugin("SalientPosesMaya")

        # Create scene
        min_frame, max_frame = 1, 61
        sel_from, sel_to = 9, 45
        obj = create_sin_animation_for_sphere(min_frame, max_frame)
        anim_snapshot, analysis, selector = make_analysis_and_selector_node(obj, min_frame, max_frame, sel_from, sel_to)
        
        # Note that selection must be provoked before errors
        selectionCache = MayaScene.provoke_attribute(selector, "selection")
        errors = MayaScene.provoke_attribute(selector, "errors")

        # Clean up
        MayaScene.delete([analysis, selector, obj] + anim_snapshot)
        cmds.flushUndo()
        cmds.unloadPlugin("SalientPosesMaya")

        # Inspection
        self.assertSelectionsAreValid(selectionCache, sel_to - sel_from + 1)
        self.assertSelectionErrorsValid(errors)
        expected = get_expected_as_list_of_ints("test_selector_node_sub_sel_a_selection")
        self.assertListEqual([int(v) for v in selectionCache], expected)
        expected = get_expected_as_list_of_floats("test_selector_node_sub_sel_a_errors")
        self.assertListAlmostEqual(errors, expected)
        
    def test_selector_node_sub_sel_b(self):
        cmds.loadPlugin("SalientPosesMaya")

        # Create scene
        min_frame, max_frame = 1, 61
        sel_from, sel_to = 20, 40
        obj = create_simple_arc_animation_for_sphere(min_frame, max_frame)
        anim_snapshot, analysis, selector = make_analysis_and_selector_node(obj, min_frame, max_frame, sel_from, sel_to)

        # Note that selection must be provoked before errors
        selectionCache = MayaScene.provoke_attribute(selector, "selection")
        errors = MayaScene.provoke_attribute(selector, "errors")

        # Clean up
        MayaScene.delete([analysis, selector, obj] + anim_snapshot)
        cmds.flushUndo()
        cmds.unloadPlugin("SalientPosesMaya")

        # Inspection
        self.assertSelectionsAreValid(selectionCache, sel_to - sel_from + 1)
        self.assertSelectionErrorsValid(errors)
        expected = get_expected_as_list_of_ints("test_selector_node_sub_sel_b_selection")
        self.assertListEqual([int(v) for v in selectionCache], expected)
        expected = get_expected_as_list_of_floats("test_selector_node_sub_sel_b_errors")
        self.assertListAlmostEqual(errors, expected)

    def test_selector_node_sub_sel_stress(self):
        cmds.loadPlugin("SalientPosesMaya")

        # Create scene
        min_frame, max_frame = 200, 800
        sel_from, sel_to = 424, 635
        obj = create_simple_arc_animation_for_sphere(min_frame, max_frame)
        anim_snapshot, analysis, selector = make_analysis_and_selector_node(obj, min_frame, max_frame, sel_from, sel_to)

        # Note that selection must be provoked before errors
        selectionCache = MayaScene.provoke_attribute(selector, "selection")
        errors = MayaScene.provoke_attribute(selector, "errors")

        # Clean up
        MayaScene.delete([analysis, selector, obj] + anim_snapshot)
        cmds.flushUndo()
        cmds.unloadPlugin("SalientPosesMaya")

        # Inspection
        self.assertSelectionsAreValid(selectionCache, sel_to - sel_from + 1)
        self.assertSelectionErrorsValid(errors)
        expected = get_expected_as_list_of_ints("test_selector_node_sub_sel_stress_selection")
        self.assertListEqual([int(v) for v in selectionCache], expected)
        expected = get_expected_as_list_of_floats("test_selector_node_sub_sel_stress_errors")
        self.assertListAlmostEqual(errors, expected)

    def test_fit_command(self):
        cmds.loadPlugin("SalientPosesMaya")
        min_frame, max_frame = 1, 11

        obj = create_simple_arc_animation_for_sphere(min_frame, max_frame)
        MayaScene.select([obj])

        # Cache the original interpolation
        xsBefore, ysBefore, zsBefore = [], [], []
        for time in range(min_frame, max_frame + 1):
            cmds.currentTime(time)
            xsBefore.append(cmds.getAttr("%s.tx" % obj))
            ysBefore.append(cmds.getAttr("%s.ty" % obj))
            zsBefore.append(cmds.getAttr("%s.tz" % obj))

        # Apply the interpolation and the sample it
        selection = [1, 6, 11]
        cmds.vuwReduceCommand(start=selection[0], finish=selection[-1], selection=selection)
        xsAfter, ysAfter, zsAfter = [], [], []
        for time in range(min_frame, max_frame + 1):
            cmds.currentTime(time)
            xsAfter.append(cmds.getAttr("%s.tx" % obj))
            ysAfter.append(cmds.getAttr("%s.ty" % obj))
            zsAfter.append(cmds.getAttr("%s.tz" % obj))

        # Check number of keyframes is correct
        nk = cmds.keyframe(obj, attribute='translateX', query=True, keyframeCount=True)
        self.assertEqual(nk, 3)

        # Check all keyframes are identical
        for s in selection:
            ix = s - selection[0]
            self.assertEqual(xsBefore[ix], xsAfter[ix])
            self.assertEqual(ysBefore[ix], ysAfter[ix])
            self.assertEqual(zsBefore[ix], zsAfter[ix])

        for i in range(selection[0], selection[-1] + 1):
            ix = i - selection[0]
            self.assertTrue((xsBefore[ix] - xsAfter[ix]) ** 2 < 0.4)
            self.assertTrue((ysBefore[ix] - ysAfter[ix]) ** 2 < 0.4)
            self.assertTrue((zsBefore[ix] - zsAfter[ix]) ** 2 < 0.4)
        
        MayaScene.delete([obj])
        cmds.flushUndo()
        cmds.unloadPlugin("SalientPosesMaya")
