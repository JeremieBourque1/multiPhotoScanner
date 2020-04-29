# multiPhotoScanner
Tool to quickly scan multiple photos at the same time

# Installation (Windows)
1. Install Libinsane https://doc.openpaper.work/libinsane/latest/libinsane/install.html
2. In Msys2, install the package dependencies with the following command: 
    ```
    pacman -S mingw-w64-x86_64-python-pillow \
              mingw-w64-x86_64-python-pyqt5
    ```
3. In the Msys2 `home\<user>\` directory (the same directory where Libsinsane should be installed), clone the repository using `git clone https://github.com/JeremieBourque1/multiPhotoScanner.git` 
4. multiPhotoScanner can now be launched in Msys2 by going to the repo directory and using the command `python multiPhotoScanner.py`