import io
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup

PROJECT_URL = 'https://github.com/SteinHeselmans/DucoBox'
__version__ = 'unknown'
exec(open('src/duco/__version__.py').read())


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


requires = ['setuptools-scm', 'pyserial', 'influxdb']

setup(
    name='duco.ducobox',
    url=PROJECT_URL,
    version=__version__,
    setup_requires=[],
    author='Stein Heselmans',
    author_email='stein.heselmans@gmail.com',
    description='Read parameters from DucoBox.',
    long_description=open("README.rst").read(),
    zip_safe=False,
    license='GNU General Public License v3 (GPLv3)',
    platforms='any',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={'console_scripts': ['ducobox = duco.ducobox:main']},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['duco'],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Home Automation',
    ],
    keywords=['Duco', 'DucoBox', 'DucoBox Silent', 'ventilation', 'home automation'],
)
