# Salient Poses (Maya implementation)

Salient Poses is an algorithm that
uses a technique called "keyframe reduction"
to convert hard-to-edit motion capture
into easy-to-edit keyframe animation.
This project contains a **Maya plug-in** that enables
artists to run Salient Poses directly inside of Maya.

# Want to jump right in?

Grab the [latest release](https://github.com/richard-roberts/SalientPosesMaya/releases/tag/0.2), [add it to Maya](#getting-started), and then follow along with the [video tutorial](https://www.youtube.com/watch?v=WzFoJoXZO-g)!

[![Video Tutorial](http://richardroberts.co.nz/images/hosting/spmv0.2_tutorial_thumbnail.jpg)](https://www.youtube.com/watch?v=WzFoJoXZO-g)

## Table Of Contents

This document starts off with
an **general introduction to the algorithm**, 
outlines exactly **what you get**,
provides the typical **getting started guide**, and
then gives some **detail on the code**:

1. [Easy-to-Edit Motion Capture!](#easy-to-edit-motion-capture)
2. [What's in this Project?](#whats-in-this-project)
3. [Getting Started](#getting-started)
4. [Digging Into the Code](#digging-into-the-code)

Please see [Salient Poses website](https://salientposes.com/)
for more detailed information
selected results, links to academic work,
and more.

Finally, know that I'm always happy to help!
Feel free to post bugs and feature requests to the
[issues board](https://github.com/richard-roberts/SalientPosesMaya/issues)
or otherwise click here to join the
[Slack](https://join.slack.com/t/salientposes/shared_invite/enQtNDU1MTM0Nzk4Mjk0LWY5MzlhYTNkMjAzM2ZkYWNmNjY5YWViNWMzZDVkNzkxYTFlYmFjMjAxZWUzOGM4MzQ0OGU0YThmM2I5N2Y1MTI) channel and chat with me.

## Easy-to-Edit Motion Capture!

Motion capture has become a **core component** of the animation pipeline in the visual effects industry. Whether it's a live-action blockbuster film or an indie game being developed in a back-alley office, motion capture is likely to be involved. While this technology is awesome - it allows actors to truly embody a fantasy character - it does have its problems.

#### The Problem

Say we start of with a mocap animation (here's one that I grabbed from [Adobe's Mixamo](https://www.mixamo.com)):

![Salient Example (Original)](http://richardroberts.co.nz/images/hosting/Salient_Example_1.gif)

While the animation looks nice, it actually has lots of [keyframes](https://en.wikipedia.org/wiki/Key_frame). Let's take a look at the keyframes, visualized here as blue outlines. There are so many keyrames; one for every frame. In this case there are 60 per second!

![Salient Example (Mocap Keyframes)](http://richardroberts.co.nz/images/hosting/Salient_Example_2.png)

While having all of these keyframes involved is necessary during recording - we want to **capture** the actor's performance precisely - they involve a large memory footprint (problematic for video games) and make the motion hard to change (problematic for motion editors). Here's a picture of just **some** of the data for the animation above. Can you imagine loading all the animations for a protagonist character in a video game (there are 1000s of unique clips for a main character in recent triple-A games)? How about trying to adjust the motion using this data?

![Salient Example (Mocap Data)](http://richardroberts.co.nz/images/hosting/Salient_Example_3.png)

#### The Solution

To address this problem, I've developed a new algorithm for compressing and editing motion capture. Titled "Salient Poses", this algorithm uses an optimal **keyframe reduction** technique to simplify motion-capture animation. Conceptually, **Salient Poses converts motion capture into hand-crafted keyframe animation**. 

More precisely, the algorithm works by finding potential set of important - that is, "salient" - poses. In each set of poses, the choice of poses has been carefully determined so that it most accurately reconstructs the original motion. Once found, we can create a new animation using just these poses. Here's an illustration of one possible optimal set of poses selected for the animation above:

![Salient Example (Selected Keyframes)](http://richardroberts.co.nz/images/hosting/Salient_Example_4.png)

Comparing these poses to the original motion-capture, we can already see the benefit: the motion can be expressed with fewer poses. Having fewer poses in the animation means a **smaller memory footprint** and also that **editors invest less time** for editing (fewer changes are required). And, furthermore, the data is now much sparser than before:

![Salient Example (Data Before And After)](http://richardroberts.co.nz/images/hosting/Salient_Example_5.png)

With all that done, the last step is to create a new motion using on the selected poses. To do this the algorithm performs [inbetweening](https://en.wikipedia.org/wiki/Inbetweening), which is the process of deciding how to transition between the poses to best recreate the original animation. It's hard to describe exactly how the in-betweening works, but you might imagine it as recreating the curve traced by each of the character's joints.

![Salient Example (Data Before And After)](http://richardroberts.co.nz/images/hosting/Salient_Example_6.png)

#### Before and After

To sum the whole process up, here's a look at the original animation (right side) and the same animation after compression with Salient Poses (left side). In this particular case the compressed animation contains only 7 keyframes (those illustrated above), paired with the reconstructed curves. Compared to the original animation, with 112 keyframes, that's around 94% compression!

![Salient Example (Anim Before And After)](http://richardroberts.co.nz/images/hosting/Salient_Example_7.gif)


# What's in this project?

This repository presents an implementation of the Salient Poses algorithm as a command-based **Maya plug-in** that I've designed for interactive use in Maya by motion-editors, animators, technical artists, and hobbyists. The tool is built with `C++` and uses `OpenCL` to redistribute some of the heavier number crunching. 

Since this implementation is designed for interactive use, it comes with its own interface. Using the interface you can specify parameters around the selection and then apply that selection to perform the keyframe-reduction. Once applied, the resulting animation consists of only the keyframes paired with curves that provide the inbetweens - much like hand-crafted animation.

*Note: If you are looking for something that is super fast, runs offline, and can be automated, please check out the [Salient Poses - Performance](https://github.com/richard-roberts/SalientPosesPerformance) implementation. I'm also planning to work on a [Blender](https://www.blender.org/) implementation in the future). And, if that's not enough, let me know you're favorite animation tool, as I'd be happy to program up a custom implementation for you!*

# Getting Started

Getting the plug-in installed is simple. The steps are:

1. ensure you have an OpenCL device (most Intel, AMD, and NVIDIA chips are fine),
2. download the latest version matching your machine and Maya version from the [releases page](https://github.com/richard-roberts/SalientPosesMaya/releases), and finally
3. add the plug-in and its supporting Python scripts to Maya.

Each release is a compressed file that contains a compiled plug-in file and a scripts directory.
The easiest way to add the plug-in and scripts to Maya is to load the compiled plug-in file using [Maya's Plug-in Manager](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-Customizing/files/GUID-2CF7D90B-EF10-40D1-9129-9D401CCAB952-htm.html). On Windows you are looking to select `SalientPosesMaya.mll`, on OSX its `SalientPosesMaya.bundle`, and Linux its `SalientPosesMaya.so`. 

![Loading the compile plug-in file](http://richardroberts.co.nz/images/hosting/spm-loading-the-plugin.png)

From there, copy and paste the `scripts` directory into your Maya project's scripts (see [this page](https://area.autodesk.com/tutorials/about-maya-projects/) if you're not familiar with projects).

Alternatively, if you want the plug-in to be available across all of your projects, you can configure Maya's `MAYA_PLUG_IN_PATH` to include the directory containing the compiled plug-in file and its `PYTHONPATH` to include the scripts folder. See [this page](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-EnvVar/files/GUID-8EFB1AC1-ED7D-4099-9EEE-624097872C04-htm.html) if you're not familiar with configuring Maya's environment variables.

![Setting Maya's environment variables](http://richardroberts.co.nz/images/hosting/spm-setting-maya-env.png) 

## Usage

*Note: don't forget to check out the [video tutorial](https://www.youtube.com/watch?v=WzFoJoXZO-g) as well.*

The interface guides you through the two phases: **selection** and **reduction**. Selection is process of choosing a range of potential keyframes for a given animation. Reduction is the process of first removing keyframes and then tweaking the resulting inbetweens to recreate the original motion. The interface will help you to manage these two steps.

#### Objects for selection versus objects for reduction

It's important to note that the objects you use for the selection step do not need to be the same as those for the reduction. For example, you might want to **choose keyframes from the movement of the hand**, but **apply the reduction to the entire body**. As an another example, you might **choose keyframes from right-leg** (perhaps so that the keyframes capture footsteps), but then **apply the reduction to the hips**. If you feel particularly crazy, you might even choose keyframes from a baked physics simulation and apply the reduction to something else entirely! Of-course, nothing is stopping you from using the same objects for both selection and reduction. Understanding the difference between these two steps is important because it gives you the **power to control how the keyframes are distributed** through the simplified version - which is essential for getting the result best-suited to your task.

#### Opening the tool

First, open the interface by running this Python code from [Maya's Script Editor](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-Scripting/files/GUID-7C861047-C7E0-4780-ACB5-752CD22AB02E-htm.html). *Note: you can alternatively load the shelf included in the release, which provides a button that launches this interface.*

```py
import salient_menu; salient_menu.show()
```

Here's what you should see:

![A look at the interface](http://richardroberts.co.nz/images/hosting/spm-a-look-at-the-interface.png) 

#### Configure OpenCL device

First off,
check the device listed next to the `OpenCL Device` label.
You can click on the drop-down to show all OpenCL-compatible devices;
choose whichever you prefer.
For most cases, you won't notice a difference,
but this is helpful
if you want to ensure that
Maya won't be holding up a particular device.

#### Using the tool

Now that we are setup, let's use the tool. Follow these five steps:

1. **Start / End Frame**. 
First check that the start and end frame are set appropriately.
These are set automatically,
based on Maya's timeline configuration,
when you open the interface.
You can change these variables to isolate
just a part of the animation for selection and reduction
if you wish. 

2. **Fixed Keyframes**. 
Next, enter any particular keyframes that you would
like to ensure are kept during reduction.
Enter any keyframes you want kept as as comma-separated whole numbers;
for example if you want to keep frames 30, 100, and 150 as keyframes
then you'd specify:
`30,100,150`.
Setting *fixed keyframes* can be important for some editing tasks;
for example, you might want to keep the frame at the very top of a jumping motion
as a keyframe.

3. **Evaluate**.
Now, select a set of animated objects in Maya;
the [outliner](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2018/ENU/Maya-Basics/files/GUID-4B9A9A3A-83C5-445A-95D5-64104BC47406-htm.html)
is useful for doing this.
The choice of what to include is up to you -
explore different choices to get a feeling for how the tool works.
If you're just interested in compression,
selecting the joints along a character's spine and limbs is generally the best option.
Otherwise, if you've got a specific change to make,
I find that choosing objects around the leading part is most useful
(the leading part is an animation term that
I first read about in John Lasseter's
[famous paper](https://courses.cs.washington.edu/courses/cse458/11au/resources/lasseter.pdf)).
*Remember,
the objects you select **don't** have to be those used later in the reduction step*.
Once you've got the objects selected,
**press the evaluate button**
and the tool will starting computing a range of *optimal* selections.

*Note: The word optimal means that each particular set of keyframes is
as-good-as-possible in terms of how well the simplified animation
will recreate the original motion.*

![Choosing a selection](http://richardroberts.co.nz/images/hosting/spm-choosing-a-selection.png) 

4. **Reduction**. 
At this point,
you need only **choose a particular set of keyframes**
and then apply the reduction.
You do this by adjusting the slider in the interface.
You'll see the keyframes illustrated interactively as blue silhouettes.
Once you've found a set of keyframes you would like to try,
**select the objects for reduction**
(this will usually be all controls for the character and any other props)
and press the `Reduce` button.
This will take a few seconds. 

![Before and After](http://richardroberts.co.nz/images/hosting/spm-before-and-after.png)

After you've applied the reduction,
play back the animation and also
examine the graph editor to see if the
result is satisfactory.
There's no right answer;
but generally you're looking for smooth curves
that look similar to the original.

5. **Explore**.
Perhaps the result you get the first time
wasn't quite right. Or maybe it was and that's great!
In either case,
the tool is designed to help you explore
and compare multiple solutions quickly.
You can explore by:

- using the slider to increase and decrease the number of keyframes,
- changing the start and end frame, and also
- setting fixed keyframes.

You can even apply a reduction,
do a
[playblast](https://knowledge.autodesk.com/support/maya-lt/learn-explore/caas/CloudHelp/cloudhelp/2017/ENU/MayaLT/files/GUID-1C6EDC8D-DA67-490E-81F1-1205336DEBD9-htm.html), 
and then undo the reduction. 
*Note: the undo button works like a stack,
you can do multiple reductions and then undo each one.*
As you explore,
its important to think carefully about
the **trade-off between compression and error**.
If you are using the tool to compress assets for a video-game,
you want to ensure that you retain a high level of detail
while using as few keyframes as possible. 
This will help you to save on the memory footprint for your game.
If you are using the tool for editing, 
try to examine how well the keyframes are distributed:
is there enough keyframes for you to make an adjustment
without distorting the motion?
The **graph** within the interface helps to communicate this tradeoff
(the red line indicates detail is lost for the current reduction).

**That's it.**
Please remember that I'm happy to help you along the way if you ever get stuck.
Feel free to jump onto the
[Slack Channel](https://join.slack.com/t/salientposes/shared_invite/enQtNDU1MTM0Nzk4Mjk0LWY5MzlhYTNkMjAzM2ZkYWNmNjY5YWViNWMzZDVkNzkxYTFlYmFjMjAxZWUzOGM4MzQ0OGU0YThmM2I5N2Y1MTI)
and chat with me, or otherwise check the
[Salient Poses website](https://salientposes.com/) for more information!

# Digging Into the Code

This algorithm works in a few steps, which I like to think of as:

1. **analysis**, building a table that expresses the importance of all potential keyframes,
2. **selection**, optimally choosing a set of poses for each level of compression, and
3. **reconstruction**, where we create the new animation from a given set of poses.

If you'd like to peek into the code,
it's best to start with the
[SalientPoses - Performance](https://github.com/richard-roberts/SalientPosesPerformance)
project (a high-performance command-line tool for running the algorithm offline).

If you're just interested in changing the interface, start by looking at [this Python file](https://github.com/richard-roberts/SalientPosesMaya/blob/master/scripts/salient_gui.py) and then some of the other files in the 
[scripts](https://github.com/richard-roberts/SalientPosesMaya/blob/master/scripts) directory. The implementation of the menu uses [PySide2](https://wiki.qt.io/PySide2) and should be familiar enough to anyone with a little experience using Python.

Otherwise, start by looking at the [Error Table](https://github.com/richard-roberts/SalientPosesPerformance/blob/5354a4f383fb6b8451cecae477872a475c9c833a//src/ErrorTable.hpp) class (this performs the analysis step), then the [Selector](https://github.com/richard-roberts/SalientPosesPerformance/blob/5354a4f383fb6b8451cecae477872a475c9c833a//src/Selector.hpp) class (this chooses optimal set of poses), and also the [Interpolator](https://github.com/richard-roberts/SalientPosesPerformance/blob/5354a4f383fb6b8451cecae477872a475c9c833a//src/Interpolator.hpp) class (this performs reconstruction using a basic curve-fitting technique). 

Once you get that far, check out the [SelectCommand](https://github.com/richard-roberts/SalientPosesMaya/blob/master/src/SelectCommand.hpp) and the [ReduceCommand](https://github.com/richard-roberts/SalientPosesMaya/blob/master/src/ReduceCommand.hpp) files. These two classes use the `Error Table`, `Selector`, and `Interpolator` to realize the algorithm in Maya.

If you've got this far and wait more information, jump on the [Slack Channel](https://join.slack.com/t/salientposes/shared_invite/enQtNDU1MTM0Nzk4Mjk0LWY5MzlhYTNkMjAzM2ZkYWNmNjY5YWViNWMzZDVkNzkxYTFlYmFjMjAxZWUzOGM4MzQ0OGU0YThmM2I5N2Y1MTI) with me or otherwise check the [Salient Poses website](https://salientposes.com/) for more information!
