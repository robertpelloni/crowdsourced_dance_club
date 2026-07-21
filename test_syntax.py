import py_compile
try:
    py_compile.compile("src/main.py", doraise=True)
    print("Syntax OK")
except Exception as e:
    print(e)
