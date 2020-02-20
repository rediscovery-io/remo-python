
cleanup:
	rm -rf build dist remo_sdk.egg-info

wheel: cleanup
	REMO_SKIP_SDK_INIT="True" python setup.py sdist bdist_wheel

publish: wheel
	twine upload dist/*


# Minimal makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = remo-sdk
SOURCEDIR     = doc/source
BUILDDIR      = doc/build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@REMO_SKIP_SDK_INIT="True" $(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

#build-doc:
#	REMO_SKIP_SDK_INIT="True" sphinx-build -M html doc/source doc/build
