#/bin/bash

python3 -m coverage run --source=. -m unittest -v $@
python3 -m coverage report -m
