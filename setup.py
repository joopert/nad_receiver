from setuptools import setup

setup(name='nad_receiver',
      version='0.0.4',
      description='Library to interface with NAD receivers through the RS232 and tcp/ip',
      url='https://github.com/joopert/nad_receiver',
      author='joopert',
      author_email=':(',
      license='MIT',
      packages=['nad_receiver'],
      install_requires=['pyserial==3.2.1'],
      zip_safe=True) 
