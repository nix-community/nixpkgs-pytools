from setuptools import setup

setup(
    name="nixpkgs-pytools",
    description="Tools for removing the tedious nature of creating nixpkgs derivations",
    version="1.0.0",
    packages=["nixpkgs_pytools"],
    license="MIT",
    long_description=open("README.md").read(),
    author="Christopher Ostrouchov",
    author_email="chris.ostrouchov@gmail.com",
    install_requires=[
        "jinja2", "setuptools"
    ],
    entry_points={"console_scripts": ["python-package-init = nixpkgs_pytools.python_package_init:main"]},
    classifiers=[
        "Intended Audience :: Human",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
