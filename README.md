# multiPhotoScanner
Tool to quickly scan multiple photos at the same time

# Installation
1. Install Libinsane https://doc.openpaper.work/libinsane/latest/libinsane/install.html
2. In Windows, if Pillow is not already installed, it can be installed in Msys2 with `
pacman -S mingw-w64-x86_64-python-pillow`
3. In the Msys2 home/<user>/ directory (the same directory where Libsinsane should be installed), clone the repository using `git clone https://github.com/JeremieBourque1/multiPhotoScanner.git` 
4. Install PySide2 in Msys2

# Installing PySide2 in Msys2
1. `pacman -S patch`
2. `git clone https://github.com/msys2/MINGW-packages.git`
3. The packages that we need to install are: `mingw-w64-shiboken2-qt5`, `mingw-w64-pyside2-qt5`. The instructions on how to install a package can be found [here](https://github.com/msys2/MINGW-packages/blob/master/README.md)
