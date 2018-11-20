#!/bin/bash

python setup.py sdist
twine upload --repository pypi dist/*
