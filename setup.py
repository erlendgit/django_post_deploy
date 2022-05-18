from distutils.core import setup
from setuptools import find_packages

setup(
    name='django_post_deploy',
    packages=find_packages(),
    version='0.9.4',
    license='cc-by-4.0',
    description='Add a generic method to have post-deploy actions done.',
    author='Erlend ter Maat',
    author_email='erwitema@gmail.com',
    url='https://github.com/erlendgit/django_post_deploy',
    download_url='https://github.com/erlendgit/django_post_deploy/archive/refs/tags/v0.9.4.tar.gz',
    keywords=['Django', 'Deployment', 'Management', 'CLI'],
    install_requires=[
        'Django',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
    ],
)
