The SDK class contains some core functionalities of Remo. It mainly acts as a wrapper around our API endpoints.

Use the SDK class to:

* create a dataset and annotation set

* list and retrieve datasets

* export annotations without a need to intialize a dataset

Most of the functions documented below can be called from Python by doing

.. code-block:: python

    import remo

    remo.function_name()

.. module:: remo

.. autoclass:: remo.sdk.SDK
    :members:
    :undoc-members:
