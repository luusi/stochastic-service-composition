from setuptools import setup, find_packages

setup(name='stochastic_service_composition',
      version='0.1.0',
      description='Implementation of stochastic service composition.',
      url='http://github.com/luusi/stochastic-service-composition',
      author='Luciana Silo',
      author_email='silo.1586010@studenti.uniroma1.it',
      license='MIT',
      packages=find_packages(include='stochastic_service_composition*'),
      zip_safe=False,
      install_requires=[
            "numpy",
            "graphviz"
      ]
      )
