import subprocess

command = f"abq cae nogui=simple_job.py"
print(command)

result = subprocess.run(command,  text=True, shell=True)