import platform

import PyInstaller.__main__
import shutil
import os

# Make sure we are building clean, remove build and dist and spec
if os.path.exists('__main__.spec'):
    os.remove('__main__.spec')

if os.path.exists('build'):
    shutil.rmtree('build')

if os.path.exists('dist'):
    shutil.rmtree('dist')

# Run build
PyInstaller.__main__.run(['./heybrochecklog/__main__.py'])

# Copy resources to path
copy_src = './heybrochecklog/resources'
copy_dest = './dist/__main__/heybrochecklog/resources'
shutil.copytree(copy_src, copy_dest, ignore=shutil.ignore_patterns('*.py'))

# Rename __main__s to heybrochecklog
if platform.system() == "Windows":
    os.rename('./dist/__main__/__main__.exe', './dist/__main__/hbcl.exe')
else:
    os.rename('./dist/__main__/__main__', './dist/__main__/hbcl')

os.rename('./dist/__main__', './dist/hbcl')

# Finally compress them into ZIP archive
shutil.make_archive(f'./dist/hbcl-{platform.system()}-{platform.architecture()[0]}', 'zip', './dist/hbcl')
