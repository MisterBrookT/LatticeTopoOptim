import subprocess

command = f"abq cae nogui=test2.py"
print(command)

result = subprocess.run(command,  text=True, shell=True)