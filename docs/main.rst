==============================
:mod:`dockerjudge.main` - Main
==============================

.. automodule:: dockerjudge.main

Judge
=====

.. autofunction:: dockerjudge.main.judge

Callback
========

Compile
-------

========= ================= =================================================
Parameter Type              Description
========= ================= =================================================
`0`       `int`             Return value of the compiler
`1`       `byte` or `tuple` Output of compiler, value type depends on `demux`
========= ================= =================================================

Judge
-----

========= =================================== ===============================
Parameter Type                                Description
========= =================================== ===============================
`0`       `int`                               Test case id, starting from `0`
`1`       :class:`~dockerjudge.status.Status` Status
`2`       `tuple`                             Output `(stdout, stderr)`
`3`       `float`                             Time used
========= =================================== ===============================
