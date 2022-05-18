from distutils.core import setup

setup(
    name='django_post_deploy',
    packages=['post_deploy'],
    version='0.9.0',
    license='cc-by-4.0',
    description='Add a generic method to have post-deploy actions done.',
    author='Erlend ter Maat',
    author_email='erwitema@gmail.com',
    url='https://github.com/erlendgit/django_post_deploy',  # Provide either the link to your github or to your website
    download_url='https://github.com/erlendgit/django_post_deploy/archive/v0.9.0.tar.gz',  # I explain this later on
    keywords=['Django', 'Deployment', 'Management', 'CLI'],  # Keywords that define your package best
    install_requires=[
        'Django',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers :: Administrators :: Product owners',
        'Topic :: Software Development :: Build Tools',
        'License :: Creative Commons Attribution-ShareAlike 4.0',
        'Programming Language :: Python :: 3',
    ],
)
