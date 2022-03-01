import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='qchecker',
    version='0.0.0a1',
    author='James Finnie-Ansley',
    description=('A simple library for finding statement-level '
                 'substructures in Abstract Syntax Trees'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/James-Ansley/qchecker',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(
        where='src',
    ),
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        'tomli~=2.0.1',
    ]
)
