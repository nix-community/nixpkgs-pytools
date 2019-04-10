from setuptools import setup

setup(
    name="nixpkgs-pytools",
    description="Tools for removing the tedious nature of creating nixpkgs derivations",
    version="1.0.1",
    packages=["nixpkgs_pytools"],
    license="MIT",
    long_description=open("README.md").read(),
    author="Christopher Ostrouchov",
    author_email="chris.ostrouchov@gmail.com",
    url="https://github.com/nix-community/nixpkgs-pytools/",
    install_requires=["jinja2", "setuptools"],
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "python-package-init = nixpkgs_pytools.python_package_init:main"
        ]
    },
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Code Generators",
        "Topic :: System :: Software Distribution",
    ],
)
