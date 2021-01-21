from setuptools import setup, find_packages
 
setup(name='fluentbit-server-py',
      version='1.0.7',
      url='https://github.com/laulin/fluentbit-server-py',
      license='MIT',
      author='Laurent MOULIN',
      author_email='gignops@gmail.com',
      description='Simple server to gather data from fluentbit agent (forward protocol)',
      packages=find_packages(exclude=['tests', 'etc']),
      install_requires=["msgpack"],
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      zip_safe=False,
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      python_requires='>=3')