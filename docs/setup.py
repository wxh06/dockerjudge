import subprocess


try:
    subprocess.run(['tx', 'pull', '--all'])
except Exception as e:
    print(e)
