call py -m coverage run --source=. -m unittest -v %*
call py -m coverage report -m
