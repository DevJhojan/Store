"""Configuración para hacer el paquete instalable."""
from setuptools import setup, find_packages
import os

# Leer README si existe
long_description = "Sistema de gestión de inventarios con interfaz gráfica"
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="inventory-manager",
    version="1.0.0",
    author="Store Development Team",
    description="Sistema de gestión de inventarios con interfaz gráfica",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/inventory-manager",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Inventory",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No hay dependencias externas, solo usa bibliotecas estándar
    ],
    entry_points={
        "console_scripts": [
            "inventory-manager=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

