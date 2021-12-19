import sys, os, importlib

modules = ["colorama", "readchar", "irc", "nuitka"]
if os.name == "nt": modules += "pywin32"

def check_module(module):
    try: importlib.import_module(module)
    except ModuleNotFoundError: return False
    else: return True

if __name__ == "__main__":
    failures = [module for module in modules if not check_module(module)]
    if failures: 
        print(f"Module(s) \"{', '.join(failures)}\" not found, please install via pip")
        sys.exit(1)
