# Set any operating-system dependent flags for the compiler
if (WIN32)
    set(COMPILE_FLAGS "/arch:AVX")
else()
    set(COMPILE_FLAGS "-mavx")
endif()

# Include our own source files
set(SOURCE_FILES
    "../SalientPosesPerformance/src/common.cpp"
    "../SalientPosesPerformance/src/common.hpp"
    "../SalientPosesPerformance/src/AnimationProxy.cpp"
    "../SalientPosesPerformance/src/AnimationProxy.hpp"
    "../SalientPosesPerformance/src/OpenCLProcess.hpp"
    "../SalientPosesPerformance/src/ErrorTable.cpp"
    "../SalientPosesPerformance/src/ErrorTable.hpp"
    "../SalientPosesPerformance/src/SelectionProxy.cpp"
    "../SalientPosesPerformance/src/SelectionProxy.hpp"
    "../SalientPosesPerformance/src/Selector.cpp"
    "../SalientPosesPerformance/src/Selector.hpp"
    "../SalientPosesPerformance/src/Interpolator.cpp"
    "../SalientPosesPerformance/src/Interpolator.hpp"
    "MayaUtils.cpp"
    "MayaUtils.hpp"
    "AnalysisNode.cpp"
    "AnalysisNode.hpp"
    "SelectorNode.cpp"
    "SelectorNode.hpp"
    "ReduceCommand.cpp"
    "ReduceCommand.hpp"
    "pluginMain.cpp"
)
add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

# Include Maya, OpenCL, and Eigen source files
target_include_directories(${PROJECT_NAME} PRIVATE Maya::Maya)
include_directories(${OpenCL_INCLUDE_DIRS})
include_directories(${EIGEN3_INCLUDE_DIR})

# Link Maya and OpenCL (Eigen is header only)
set(LIBS ${OpenCL_LIBRARY} Maya::Maya)
target_link_libraries (${PROJECT_NAME} PRIVATE ${LIBS})

# Set our own compiler options
target_compile_options(${PROJECT_NAME} PRIVATE ${COMPILE_FLAGS})

# Format as a Maya plugin.
MAYA_PLUGIN(${PROJECT_NAME})

# Include name and version meta-data
install(TARGETS ${PROJECT_NAME} ${MAYA_TARGET_TYPE} DESTINATION ./plug-ins/SalientPoses)

# Finally, copy OpenCL programs into the build's directory.
install(FILES "../SalientPosesPerformance/src/euclideanBoundedPointToLineDistance.cl" DESTINATION ./plug-ins/SalientPoses)
install(FILES "../SalientPosesPerformance/src/extremeBoundedPointToLineDistance.cl" DESTINATION ./plug-ins/SalientPoses)
