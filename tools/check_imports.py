import sys, os, importlib

modules = ["colorama", "readchar", "irc", "nuitka", "keyring"]
if os.name == "nt": modules += ["win32api"]
else: modules += ["sagecipher"]

def check_module(module):
    try: importlib.import_module(module)
    except ModuleNotFoundError: return False
    else: return True

if __name__ == "__main__":
    failures = [module for module in modules if not check_module(module)]
    if "win32api" in failures: failures[failures.index("win32api")] = "pywin32"
    if failures: 
        print(f"Module(s) \"{', '.join(failures)}\" not found, please install via pip")
        sys.exit(1)
