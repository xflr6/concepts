# setup.py

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='concepts',
    version='0.6',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Formal Concept Analysis with Python',
    license='MIT',
    keywords='fca complete lattice graph join meet galois',
    url='http://github.com/xflr6/concepts',
    packages=['concepts'],
    install_requires=[
        'bitsets==0.6',
        'graphviz==0.2',
    ],
    platforms='any',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
