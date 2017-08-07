#!/bin/bash

rm -r html
#rm source/rst/*
#sphinx-apidoc -o source/rst ../iprPy -d 2
#python build.py
sphinx-build -b html source html