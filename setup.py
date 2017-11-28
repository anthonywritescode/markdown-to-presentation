from setuptools import setup

setup(
    name='markdown-to-presentation',
    description='Takes markdown and turns it into an html slideshow.',
    url='https://github.com/anthonywritescode/markdown-to-presentation',
    version='0.0.16',
    author='Anthony Sottile',
    author_email='asottile@umich.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'libsass',
        'markdown-code-blocks>=1.1.0',
    ],
    py_modules=['markdown_to_presentation'],
    entry_points={
        'console_scripts': [
            'markdown-to-presentation=markdown_to_presentation:main',
        ],
    },
)
