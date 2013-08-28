.. include:: ../globals
.. _tutorial_tutorial01:

=====================================
Writing your first Report, part 1
=====================================

Let's learn by example.

Throughout this tutorial, we'll walk you through the creation of a
full featured report.

It'll consist of many parts:

* Creating a :ref:`ref_datasource` one related :ref:`ref_report`
* Define one or more :ref:`ref_renderers`
* Customize the Report columns using proper :ref:`ref_columns`
* Allow the user to add some cutomization like :ref:`ref_filtering`
* Use custom :ref:`ref_widgets`
* Define a custom :ref:`ref_cache` manager


Creating the Reports package
============================

For this tutorial we'll create a Report of the users of our website, and the report
will be exportable in ``.xls``, and ``html``.

Create a package named ``reports`` in your application to be like::

    myapp/
        reports/
            __init__.py
            users.py
            registry.py
            columns.py


Create the Datasource
====================================

The :ref:`ref_datasource` contains the data that you want to
display in your reports. Each Datasource can provide data to many reports.


Edit the :file:`users.py` file so it looks like this

.. code-block:: python

    from ereports.engine.datasource import Datasource
    from django.contrib.auth.models import User


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

Edit the :file:`users.py` and add the following code

.. code-block:: python

    from ereports.engine.report import BaseReport


    class UserReport(BaseReport):
        datasource = UserDataSource.as_datasource()
        title = 'Users'


    from ereports.engine.registry import registry
    registry.register(UserReport)
