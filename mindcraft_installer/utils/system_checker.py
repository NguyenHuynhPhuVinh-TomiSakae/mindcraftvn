import subprocess

def check_nodejs():
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, 
                              text=True,
                              shell=True)
        return result.returncode == 0
    except:
        return False

def check_python():
    try:
        result = subprocess.run(['python', '--version'], 
                              capture_output=True,
                              text=True,
                              shell=True)
        return result.returncode == 0
    except:
        try:
            result = subprocess.run(['python3', '--version'],
                                  capture_output=True,
                                  text=True,
                                  shell=True)
            return result.returncode == 0
        except:
            return False