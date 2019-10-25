
wheel:
	python setup.py sdist bdist_wheel

publish-package:
	twine upload dist/*
