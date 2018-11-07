from setuptools import setup

setup(
    name="Migrate",
    version="0.1.0",
    author="Bruno Souza",
    author_email="brnosouza@gmail.com",
    packages=["migrate"],
    include_package_data=True,
    url="http://pypi.python.org/pypi/MyApplication_v010/",
    license="LICENSE.txt",
    description="Tool to migrate from databases.",
    # long_description=open("README.txt").read(),
    install_requires=["psycopg2", 'pymongo'],
)
