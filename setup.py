from setuptools import setup
import sys

if not sys.version_info[0] >= 3 and sys.version_info[1] >=5:
    sys.exit('Requires Python >= 3.5')

setup(name='aioget',
      version='0.1',
      author='Fernando Giannasi <phoemur@gmail.com>',
      url='https://github.com/phoemur/aioget',
      download_url = 'https://github.com/phoemur/aioget/tarball/0.1',

      description="Async io command line download utility written in python",
      license="Unlicense",
      classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
      ],

      py_modules=['aioget'],
      include_package_data=True,
      zip_safe=False,
    
      install_requires=[
          'setuptools',
          'aiohttp',
          'aiofiles',
          'blessings',
          # -*- Extra requirements: -*-
      ],

      long_description='''
      ''',
    
      entry_points={
          'console_scripts': [
              'aioget = aioget:main',
              ],
      },
)