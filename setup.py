from setuptools import setup

setup(name='multiPhotoScanner',
      version='0.1.0',
      packages=['multiPhotoScanner'],
      entry_points={
          'gui_scripts': [
              'multiPhotoScanner = multiPhotoScanner.__main__:main'
          ]
      },
      package_data={
          "": ["*.ui"],
      }
      )
