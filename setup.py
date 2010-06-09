#!/usr/bin/env python

from distutils.core import setup

import kbtune

setup(
    name='kbtune',
    version=kbtune.__version__,
    license='BSD',
    description='Keyboard tuning calculator',
    long_description=open('README.txt').read(),
    author='Matthias C. M. Troffaes',
    author_email='matthias.troffaes@gmail.com',
    url='http://github.com/mcmtroffaes/kbtune',
    platforms='any',
    packages=['kbtune'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio',
        ],
    )
