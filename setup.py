from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()


setup(
    name = 'Actioneer',
    packages = ['actioneer'],
    version = '0.5',
    license='MIT',
    description = 'Actioneer is a multi-purpose command handler that can be used on its own or embedded in other projects',
    author = 'Zomatree',
    url = 'https://github.com/clamor-py/Actioneer/',
    download_url = 'https://github.com/clamor-py/Actioneer/archive/v0.5.0.tar.gz',
    keywords = ['commands', 'handler'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
