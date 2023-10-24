# gendef-msvc
Repackaging the GPL'd gendef tool for use in bare-Win32 world

`gendef.exe` is used to create a .def file from an existent `.dll` file. Once that's been done, you can rename the `.dll` and change the name of the library in the `.def` file and the resulting `.lib` file, linked into an `.exe` file will connect the two.

## My contributions

### under GPL:
* CMakeLists.txt -- a meta-build for the gendef tool, suitable for building in a pure Win32/MSVC environment

### under SQLite3-style "blessing":

Standins, using python, for the lack of auto-tools in a pure Win32/MSVC environment:
* configure.cmd
* choosep3.py
* configure.py
* make.py

## How to Use
Once you have Visual Studio, CMake and Python3 installed, the steps are simple.
1. Once you've sync'd this project, make it your current directory
2. Execute `.\configure`
 2.1. if this fails because the system claims:
```Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.```
If you have installed Python and it is on the path, disable this shortcut and the interpreter SHOULD be able to find your Python install.
 2.2 if this fails because:
```'python' is not recognized as an internal or external command, operable program or batch file.```
determine the path to your Python3 interpreter. Let's pretend it's `C:\PythonForMe\python.exe`
re-run configure as `.\configure.cmd --python C:\PythonForMe\python.exe`
3. `.\make`
4. `.\make install` -- puts `gendef.exe` into `C:\ProgramData\bin`

The rationale for the default destination `C:\ProgramData\bin` is discussed in `ANSAK-PATHS`. If you want the installation to go somewhere else, you can use the `--prefix` argument as documented from `python3 configure.py --prefix`.
