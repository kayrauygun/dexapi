import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dexapi",
    version="0.1.0",
    author="Kayra Uygun",
    author_email="kayrauygun@gmail.com",
    description="Python wraper for DEX API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kayrauygun/dexapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
   install_requires=[
          'pandas', 'requests',
   ],
   python_requires='>=3.6',
)