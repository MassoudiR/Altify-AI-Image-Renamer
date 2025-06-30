import sys
import subprocess
import os

if __name__ == '__main__':
    image_paths = sys.argv[1:]

    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)  
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    altify_path = os.path.join(script_dir, 'Altify.exe')

    cmd = [altify_path, '--mini'] + image_paths




    if os.path.exists(altify_path):
        try:
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            print(f"Subprocess failed: {e}")
    else:
        print("Altify.exe NOT FOUND!")
