from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="EasyCells",
    version="0.1.5",
    author="poweron",
    author_email="nathanpinheiro99@gmail.com",
    description="Uma biblioteca para criação de jogos e interfaces gráficas.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/poweron0102/EasyCells",
    packages=find_packages(include=["EasyCells", "EasyCells.*"]),  # Inclui apenas o código-fonte da biblioteca
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",  # Versão mínima do Python
    install_requires=[         # Dependências do projeto
        "pygame-ce>=2.5.2",
        "numpy>=2.1",          # Para PhysicsComponents
        "numba>=0.60",         # Para PhysicsComponents
        "scipy>=1.15",         # Para PhysicsComponents
        "pyfmodex>=0.7.2",     # Para FMOD
        "midvoxio>=0.1.6",     # Para SpriteStacks
        "matplotlib>=3.10",    # Para SpriteStacks
    ],
)
