from distutils.core import setup

setup(
    name='django_post_deploy',
    packages=['post_deploy'],
    version='0.9.1',
    license='cc-by-4.0',
    description='Add a generic method to have post-deploy actions done.',
    author='Erlend ter Maat',
    author_email='erwitema@gmail.com',
    url='https://github.com/erlendgit/django_post_deploy',
    download_url='https://github.com/erlendgit/django_post_deploy/archive/refs/tags/v0.9.1.tar.gz',
    keywords=['Django', 'Deployment', 'Management', 'CLI'],
    install_requires=[
        'Django',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
    ],
)
