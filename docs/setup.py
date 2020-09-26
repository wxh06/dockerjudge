"Run `tx pull --all`"

import subprocess


subprocess.run(["tx", "pull", "--all"], check=True)
