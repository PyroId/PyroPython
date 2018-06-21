from setuptools import setup

setup(name='pyropython',
      version='0.01',
      description='Python utility for pyrolysis parameter identification',
      url='https://ringworld.vtt.fi/scm/git/PyroPython',
      author='Topi Sikanen',
      author_email='topi.sikanen@vtt.fi',
      license='VTT',
      packages=['pyropython'],
      entry_points = {
        "console_scripts": ['pyropython = pyropython.pyropython:main',
        					'plot_pyro = pyropython.plotting:main']
      },
      zip_safe=False)