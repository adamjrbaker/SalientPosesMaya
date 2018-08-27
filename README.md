# SalientPoses - Maya Implementation

*Please check the [issues panel](https://github.com/richard-roberts/SalientPosesMaya/issues) for known issues.*

This project implements the [Salient Poses](https://github.com/richard-roberts/PhD) algorithm as a plug-in for Maya. Please refer to [Getting Started](#getting-started) for more information about obtaining and running this implementation, to [Details](#details) for more information about the design of the plug-in, and to [Contributing](#contributing) for more information about developing the plug-in itself.

Here's a six-minute YouTube tutorial on how to use the plug-in: [Edit mocap easily in Maya using keyframes](https://youtu.be/KdJ4XS9cWEM).


Getting Started
---------------

Getting started is simple: navigate to the [releases](https://github.com/richard-roberts/SalientPosesMaya/releases) page of this repository and download the package that corresponds to your operating system. Each package contains a folder, which includes:

- the plug-in itself (a pre-compiled binary), and
- a pair of scripts that provide a GUI for the plug-in.

There are just two steps to complete before you can use the tool. First, load the plug-in's binary file using the Maya's `Plug-in Manager`. Next, run the following command to open the GUI:

```
import maya.cmds as cmds; cmds.loadPlugin("SalientPosesMaya")
import sys; sys.path.append("/absolute/path/to/SalientPoses")
import scripts.salient_poses_menu as spm; spm.show()
```

Make sure you set the path to the  `SalientPoses` folder correctly!

To make this process automatic, you can update [Maya's plug-in path](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2016/ENU/Maya/files/GUID-8EFB1AC1-ED7D-4099-9EEE-624097872C04-htm.html) so that it can find the plug-in and update the `PYTHONPATH` variable so that it can find the `SalientPoses` folder. I personally like to put assign the command to a shelf button and a hot-key.

If you haven't done so already, it might be useful to checkout my [introduction to the plug-in](https://youtu.be/KdJ4XS9cWEM).


Details
-------

*Note: this section is incomplete, but should at least give an idea of how the plug-in is designed.*

This plug-in provides two dependency nodes: an `AnalysisNode` that performs the analysis step of Salient Poses, a `SelectorNode` that performs the selection step, and a `ReduceCommand` that is responsible for creating a new animation by firstly removing non-keyframes and secondly running the interpolation step of Salient Poses to best recover the detail of the original animation.

The `AnalysisNode` effectively wraps the `ErrorTable` class provided by the [performance implementation of Salient Poses](https://github.com/richard-roberts/SalientPosesPerformance): it receives as input a list of `MPoints` and, from these, it instantiates and executes the `ErrorTable`, and then sets it output based on the result. In a similar way, the `SelectorNode` effectively wraps the `Selector` from the performance implementation: it creates a Selector from its input (the start frame for the selection, the end frame, and the result from the error table), executes the selector, and then sets its output to the selector's result. Finally the `ReduceCommand` takes, as input, a particular set of keyframes and a list of objects. The command iterates through each of the objects and, for each of their animation curves, it first bakes and caches the animation of that attribute, then removes all non-keyframes, and finally updates the resulting interpolation to best recover the cached animation. 

See the [menu](https://github.com/richard-roberts/SalientPosesMaya/blob/master/scripts/salient_poses_menu.py) and [test](https://github.com/richard-roberts/SalientPosesMaya/blob/master/tests/test_salient_poses.py) files for examples of how to create and use the two nodes and the commands directly through Python code. 

Contributing
------------

This implementation is written in C++ and is supported by the [cmake](https://cmake.org/) build tool. To build the implementation, your machine will need to have a C compiler and also a device that supports [OpenCL](https://www.khronos.org/opencl/) along with an OpenCL SDK - this [blog post](https://anteru.net/blog/2012/11/03/2009/index.html) explains how to get started with OpenCL for Intel, AMD, and NVIDIA devices.

Before building the plug-in you will need to have an installation of Maya, 2017 or later, running on your machine (Autodesk provides free educational licences that can be obtained [here](https://www.autodesk.com/education/free-software/maya)).

Once Maya has been installed, clone the [parent repository](https://github.com/richard-roberts/PhD) and then run the `ideinit.sh` script to create the build files corresponding to your favourite C++ IDE. After you've successfully built the project using the `Install` configuration, run the tests via the `run-tests.sh` script.

Here are the steps:

```
# Install Maya and it's devkit

# Clone the parent repo
git clone --recursive https://github.com/richard-roberts/PhD.git

# Build the project and run the tests
cd SalientPosesPerformance
./ideinit <your favourite ide here>
cd build
cmake --build . config -- Install
cd ..
./run-tests.sh
```

Feel free to get in touch with any questions via the [issues panel](https://github.com/richard-roberts/SalientPosesMaya/issues)!
