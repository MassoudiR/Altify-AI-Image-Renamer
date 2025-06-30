import os
import sys
import winreg
import pythoncom
from win32com.shell import shell
from utils.config import Config


config = Config()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def register_crea_context_menu(base_path):
    # Use the actual EXE if bundled, otherwise fallback to main.py
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        app_path = os.path.abspath(os.path.join(base_path, "main.py"))

    icon_path = resource_path(os.path.join("assets", "Logo", "logo-rounded.ico"))

    key_path = r"Directory\Background\shell\Altify"
    command_key = key_path + r"\command"

    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Create 'crea' folders here")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_key) as command:
            command_line = f'"{app_path}" --create_now_crea "%V"'
            winreg.SetValueEx(command, "", 0, winreg.REG_SZ, command_line)

        print(f"[+] 'crea' context menu registered for folders using: {app_path}")

    except PermissionError:
        print("[!] Permission denied. Run this script as Administrator.")
    except Exception as e:
        print(f"[!] Error registering context menu: {e}")


def unregister_crea_context_menu():
    try:
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\Altify\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\Altify")
        print("[-] 'crea' context menu unregistered.")
    except FileNotFoundError:
        print("[~] 'crea' context menu not found.")
    except PermissionError:
        print("[!] Permission denied. Run this script as Administrator.")
    except Exception as e:
        print(f"[!] Error unregistering context menu: {e}")


def create_sendto_shortcut(target_path, shortcut_name, icon_path=None):
    sendto_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\SendTo')
    shortcut_path = os.path.join(sendto_dir, f"{shortcut_name}.lnk")

    shell_link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )

    shell_link.SetPath(target_path)
    shell_link.SetDescription(shortcut_name)
    shell_link.SetWorkingDirectory(os.path.dirname(target_path))

    if icon_path and os.path.exists(icon_path):
        shell_link.SetIconLocation(icon_path, 0)

    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)

    print(f"[+] Shortcut created: {shortcut_path}")

unregister_crea_context_menu()