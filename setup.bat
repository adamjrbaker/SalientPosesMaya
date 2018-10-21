set /p ide="Enter IDE: "
set /p mayaversion="Enter Maya version: "
mkdir build
cd build
cmake -G "%ide%" -DMAYA_VERSION="%mayaversion%" ../
echo "Setup finished"
pause