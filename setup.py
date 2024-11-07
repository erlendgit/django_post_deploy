from setuptools import setup, find_packages
from post_deploy import VERSION

setup(
    name="django-post-deploy",
    version=VERSION,
    description="Django post-deployment utility",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Erlend ter Maat",
    author_email="erwitema@gmail.com",
    license='cc-by-4.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=['Django', 'Deployment', 'Management', 'CLI'],
)
