from setuptools import setup
from sys import version_info
from helga-queue.version import VERSION

with open('README.rst') as file:
    long_description = file.read()

requires = ['helga>=1.0.0']

classifiers = [
    'Development Status :: 4 - Beta',
    'Topic :: Communications :: Chat :: Internet Relay Chat',
    'Framework :: Twisted',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name='helga-queue',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=['helga_queue', 'helga_queue.tests'],
    url='http://github.com/jantman/helga-queue/',
    description='Simple queue plugin for Helga IRC bot.',
    long_description=long_description,
    install_requires=requires,
    keywords="helga queue todo irc",
    classifiers=classifiers,
    entry_points = dict(
        helga_plugins=[
            'queue = helga_queue.plugin:queue_plugin',
        ],
    ),
)
