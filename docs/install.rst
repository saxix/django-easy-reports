.. include:: globals

.. _install:


Installation
============

.. code-block:: sh

    pip install django-easy-reports


Add :mod:`ereports` to your `INSTALLED_APPS`

.. code-block:: python

    INSTALLED_APPS = (
        'ereports',
        'django.contrib.admin',
        'django.contrib.messages',
    )

Add urls to your urls.py

.. code-block:: python

    urlpatterns = patterns('',
        ...
        (r'^ereports/', include(ereports.urls)),
    )
