import os
from setuptools import setup, find_packages

required_packages = [line.strip('\n') for line in
                     open('requirements.txt').readlines()]
                     
dependency_links=[
    '-e git+https://github.com/techoutlooks/django-objectset.git@develop#egg=django_objectset',
]

def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='rapidsms-groups',
    version=__import__('groups').__version__,
    author='Caktus Consulting Group',
    author_email='solutions@caktusgroup.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/ewheeler/rapidsms-groups/',
    license='BSD',
    description=u' '.join(__import__('groups').__doc__.splitlines()).strip(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=read_file('README.rst'),
    tests_require=required_packages,
    test_suite="runtests.runtests",
    install_requires=required_packages,
    zip_safe=False,
)
