from setuptools import setup

setup(name='funtool',
        version='0.0.81',
        url='https://github.com/pjanis/funtool',
        description='FUN Tool engine: Used process an analysis',
        author='Active Learning Lab',
        author_email='pjanisiewicz@gmail.com',
        license='MIT',
        packages=[
            'funtool',
            'funtool.lib'
        ],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4'
        ],
        install_requires=[
            'PyYAML'
        ],
        zip_safe=False)
