"""
    pyspecific.py
    ~~~~~~~~~~~~~

    Sphinx extension with Python doc-specific markup.

    :copyright: 2008-2014 by Georg Brandl.
    :license: Python license.
"""


from sphinx import addnodes
from sphinx.domains.python import PyModulelevel, PyClassmember


# Support for documenting decorators

class PyDecoratorMixin(object):
    def handle_signature(self, sig, signode):
        ret = super(PyDecoratorMixin, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_addname('@', '@'))
        return ret

    def needs_arglist(self):
        return False


class PyDecoratorFunction(PyDecoratorMixin, PyModulelevel):
    def run(self):
        # a decorator function is a function after all
        self.name = 'py:function'
        return PyModulelevel.run(self)


class PyDecoratorMethod(PyDecoratorMixin, PyClassmember):
    def run(self):
        self.name = 'py:method'
        return PyClassmember.run(self)


class PyCoroutineMixin(object):
    def handle_signature(self, sig, signode):
        ret = super(PyCoroutineMixin, self).handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('coroutine ', 'coroutine '))
        return ret


class PyCoroutineFunction(PyCoroutineMixin, PyModulelevel):
    def run(self):
        self.name = 'py:function'
        return PyModulelevel.run(self)


class PyCoroutineMethod(PyCoroutineMixin, PyClassmember):
    def run(self):
        self.name = 'py:method'
        return PyClassmember.run(self)


def setup(app):
    app.add_directive_to_domain('py', 'decorator', PyDecoratorFunction)
    app.add_directive_to_domain('py', 'decoratormethod', PyDecoratorMethod)
    app.add_directive_to_domain('py', 'coroutinefunction', PyCoroutineFunction)
    app.add_directive_to_domain('py', 'coroutinemethod', PyCoroutineMethod)
