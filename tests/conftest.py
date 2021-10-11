import pytest


@pytest.fixture
def func_args():
    class FuncArgsFixture(object):
        def __call__(self, *args, **kwargs):
            self._args = args
            self._kwargs = kwargs

        def get_args(self):
            return self._args

        def get_kwargs(self):
            return self._kwargs
    return FuncArgsFixture()


@pytest.fixture
def ctor_args():
    _args = {}
    _kwargs = {}

    class CtorArgsFixture(object):
        def __init__(self, *args, **kwargs):
            _args['args'] = args
            _kwargs['kwargs'] = kwargs

        @staticmethod
        def get_kwargs():
            return _kwargs['kwargs']

        @staticmethod
        def get_args():
            return _kwargs['args']
    return CtorArgsFixture


@pytest.fixture
def call_count():
    class CallCount(object):
        _count = 0

        def __call__(self, *args, **kwargs):
            self._count += 1

        def get_count(self):
            return self._count
    return CallCount()
