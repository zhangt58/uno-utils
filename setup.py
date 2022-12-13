# -*- coding: utf-8 -*-

from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


install_requires = [
    'numpy',
]

extra_require = {
    'test': ['pytest'],
}


setup(
    name='uno-utils',
    version='0.0.1',
    description='Utilities for uno development',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url="https://github.com/archman/uno-utils",
    author='Tong Zhang',
    author_email='zhangt@frib.msu.edu',
    packages=[
        'uno_utils',
    ],
    package_dir={
        'uno_utils': 'main',
    },
    install_requires=install_requires,
    extra_require=extra_require,
    license='GPL3+',
    keywords="uno libreoffice",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
