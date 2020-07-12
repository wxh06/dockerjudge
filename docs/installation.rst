============
Installation
============

Docker
======

To run :mod:`dockerjudge`, `Docker Engine <https://www.docker.com>`_ is required.

Install using the convenience script (for servers)
--------------------------------------------------

.. code:: shell

    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh

See `Install Docker Engine | Docker Documentation <https://docs.docker.com/engine/install/>`_ for more information.

Package :mod:`dockerjudge`
==========================

From the `Python Package Index (PyPI) <https://pypi.org>`_
-----------------------------------------------------------

`dockerjudge · PyPI <https://pypi.org/project/dockerjudge/>`_

- `PyPI <https://pypi.org/simple/dockerjudge/>`_
- `Alibaba Open Source Mirror <https://mirrors.aliyun.com/pypi/simple/dockerjudge/>`_
- `Tsinghua Open Source Mirror <https://pypi.tuna.tsinghua.edu.cn/simple/dockerjudge/>`_

Via `pip <https://pip.pypa.io>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

    pip install dockerjudge

Via `Easy install <https://setuptools.readthedocs.io/en/latest/easy_install.html>`_ (deprecated)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

    easy_install dockerjudge


From `source <https://github.com/wxh06/dockerjudge>`_ on `GitHub <https://github.com>`_
---------------------------------------------------------------------------------------

- HTTPS: `https://github.com/wxh06/dockerjudge.git`
- SSH: `git@github.com:wxh06/dockerjudge.git`

.. code:: shell

    git clone https://github.com/wxh06/dockerjudge.git
    cd dockerjudge

    make pip && make  # python3 -m pip install -Ur requirements.txt && python3 setup.py build
    sudo make install  # python3 setup.py install
