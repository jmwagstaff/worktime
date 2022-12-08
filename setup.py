from setuptools import setup

setup(
    name='worktimes',
    version='0.1.0',
    py_modules=['worktimes'],
    install_requires=[
        'Click',
        'pandas',
        'datetime'
    ],
    entry_points='''
        [console_scripts]
        wt=worktimes:wt
    ''',
)