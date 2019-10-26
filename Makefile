
cleanup:
	rm -rf build dist remo_sdk.egg-info

wheel: cleanup
	python setup.py sdist bdist_wheel

publish: wheel
	twine upload dist/*
