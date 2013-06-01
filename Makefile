BUILDDIR=~build

test:
	py.test -vv

coverage:
	py.test --cov ereports --cov-report html --cov-config ereports/tests/.coveragerc
ifdef BROWSE
	firefox ${BUILDDIR}/coverage/index.html
endif


demo:
	pip install -r ereports/requirements/install.pip
	pip install -r ereports/requirements/testing.pip
	pip install -r demo/demoproject/requirements.pip
	./manage.py syncdb --noinput --migrate --all
	./manage.py register_report -m demoproject.demoapp.reports


clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage .pytest MEDIA_ROOT MANIFEST .cache *.egg build STATIC
	find . -name __pycache__ -prune | xargs rm -rf
	find . -name "*.py?" -prune | xargs rm -rf
	find . -name "*.orig" -prune | xargs rm -rf
	rm -f coverage.xml flake.out pep8.out pytest.xml


docs:
	mkdir -p ${BUILDDIR}/docs
	sphinx-build docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif


.PHONY: docs test demo
