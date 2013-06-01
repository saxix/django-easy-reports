.. include:: globals.rst

.. _quickstart:


Quickstart
============

--------------------
Create a DataSource
--------------------

Edit the :file:`reports.py` file so it looks like this

.. code-block:: python

    from ereports.engine.datasource import Datasource
    from django.contrib.admin.models import User

    class UserDataSource(Datasource):
        model = User
        columns = ['username',
                   'last_name',
                   'first_name',
                   'email',
                   'is_staff',
                   'is_active',
                   'date_joined']

------------------
Define the Report
------------------

Edit the :file:`reports.py` file so it looks like this

.. code-block:: python

    from ereports.engine.report import BaseReport

    class UserReport(BaseReport):
        datasource = UserDataSource.as_datasource()
        title = 'Users'


    from ereports.engine.registry import registry
    registry.register(UserReport)

------------------------
Setup the url
------------------------

Edit the :file:`urls.py` file so it looks like this

.. code-block:: python

    from django.conf.urls import patterns
    import ereports.urls


    urlpatterns = patterns('',
                           (r'', include(include(ereports.urls))),
                           (r'^admin/', include(include(public_site.urls))),
                          )

-------------------
Register the Report
-------------------
.. code-block:: sh

    $ ./manage.py register_report --module myapp.reports
