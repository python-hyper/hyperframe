.PHONY: publish

publish:
	rm -rf dist/
	tox -e packaging
	twine upload -s dist/*
