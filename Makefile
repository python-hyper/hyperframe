.PHONY: certs publish test bench

certs:
	curl http://ci.kennethreitz.org/job/ca-bundle/lastSuccessfulBuild/artifact/cacerts.pem -o hyper/certs.pem

publish:
	rm -rf dist/
	python setup.py sdist bdist_wheel
	twine upload -s dist/*

test:
	py.test -n 4 --cov hyperframe test/

bench:
	python -m pytest bench/ --benchmark-only --benchmark-group-by=name --benchmark-autosave --benchmark-compare
