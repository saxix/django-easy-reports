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

pep8:
	pep8 demo/ ereports/ \
	    --max-line-length=120 \
	    --exclude=migrations,factories,settings,tests \
	    --ignore E501,E401,W391,E128,E261

flake8:
	flake8 --max-line-length=120 --exclude=migrations,factories,settings,tests \
	    --ignore=E501,E401,W391,E128,E261 --format pylint demo/ ereports/

docs:
	mkdir -p ${BUILDDIR}/docs
	sphinx-build docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif


.PHONY: docs test demo
