from setuptools import setup, find_packages
import os

packages = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

f = open('README.md')
readme = f.read()
f.close()

setup(
    name='bw2waterbalancer',
    version="0.1.1",
    packages=find_packages(),
    package_data={'bw2waterbalancer': ['data/*.json']},
    author="Pascal Lesage",
    author_email="pascal.lesage@polymtl.ca",
    license="MIT; LICENSE.txt",
    install_requires=[
        'brightway2',
        'numpy',
        'pyprind',
        'presamples',
    ],
    url="https://gitlab.com/pascal.lesage/bw2waterbalance",
    long_description=readme,
    long_description_content_type="text/markdown",
    description='Package used to create balanced LCA water exchange samples to override unbalanced sample in Brightway2.',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
