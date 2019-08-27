from setuptools import setup

setup(
    name="nixpkgs-pytools",
    description="Tools for removing the tedious nature of creating nixpkgs derivations",
    version="1.3.0",
    packages=["nixpkgs_pytools"],
    license="MIT",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="Christopher Ostrouchov",
    author_email="chris.ostrouchov@gmail.com",
    url="https://github.com/nix-community/nixpkgs-pytools/",
    install_requires=["jinja2", "setuptools", "rope"],
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "python-package-init = nixpkgs_pytools.python_package_init:main",
            "python-rewrite-imports = nixpkgs_pytools.import_rewrite:main"
        ]
    },
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Code Generators",
        "Topic :: System :: Software Distribution",
    ],
)
