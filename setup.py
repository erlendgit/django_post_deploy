import io
from distutils.core import setup
from os.path import exists

from setuptools import find_packages
from post_deploy import VERSION

setup(
    name='django_post_deploy',
    packages=find_packages(),
    version=VERSION[1:],
    license='cc-by-4.0',
    description='A generic way to have post-deploy actions done.',
    long_description=io.open("README.md", encoding='utf-8').read() if exists("README.md") else "",
    long_description_content_type='text/markdown',
    author='Erlend ter Maat',
    author_email='erwitema@gmail.com',
    url='https://github.com/erlendgit/django_post_deploy',
    download_url=f'https://github.com/erlendgit/django_post_deploy/archive/refs/tags/{VERSION}.tar.gz',
    keywords=['Django', 'Deployment', 'Management', 'CLI'],
    install_requires=[
        'Django',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
    ],
)
