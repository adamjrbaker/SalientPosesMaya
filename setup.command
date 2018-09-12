cd `dirname $0`
echo "Enter IDE: "; read ide
echo "Enter Maya version: "; read mayaversion
mkdir -p build && cd build && cmake -G $ide -DMAYA_VERSION=$mayaversion ../ 
echo "Setup finished"
