from b_module import BClass


A_INTEGER = 1
A_STRING = "A_STRING"


class AClass(BClass):
    CLASS_VAR = 0

    def __init__(self):
        self._instance_attr = 1.4

    def a_method(self, arg1, arg2=2):
        a_var = 1
        pass

A_INSTANCE = AClass()

A_CLASS = AClass

