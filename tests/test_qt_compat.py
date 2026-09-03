from qt_compat import application_exec

class Qt6Application:
    def exec(self): return 6

class Qt5Application:
    def exec_(self): return 5

def test_application_exec_supports_pyside6():
    assert application_exec(Qt6Application()) == 6

def test_application_exec_supports_pyside2():
    assert application_exec(Qt5Application()) == 5
