# setup.py

from setuptools import setup, find_packages

setup(
    name='concepts',
    version='0.7.10.dev0',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Formal Concept Analysis with Python',
    keywords='fca complete lattice graph join meet galois',
    license='MIT',
    url='http://github.com/xflr6/concepts',
    packages=find_packages(),
    install_requires=[
        'bitsets>=0.7, <0.8',
        'graphviz>=0.3, <0.5',
    ],
    extras_require={
        'test': ['nose', 'coverage', 'flake8', 'pep8-naming'],
        'dev': ['wheel'],
    },
    platforms='any',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
