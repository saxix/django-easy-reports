=============
Datasource
=============


.. module:: ereports.engine.datasource
   :synopsis: Datasource


``Datasource``
--------------

.. class:: Datasource([auto_now=False, auto_now_add=False, **options])

.. attribute:: Datasource.auto_now

    Automatically set the field to now every time the object is saved. Useful
    for "last-modified" timestamps. Note that the current date is *always*
    used; it's not just a default value that you can override.
