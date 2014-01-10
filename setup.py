# setup.py

from distutils.core import setup

setup(
    name='concepts',
    version='0.1.1',
    url='http://pypi.python.org/pypi/concepts',
    license='MIT',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Formal Concept Analysis with Python',
    install_requires=['bitsets == 0.1.1'],
    long_description=open('README.txt').read(),
    packages=['concepts'],
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
