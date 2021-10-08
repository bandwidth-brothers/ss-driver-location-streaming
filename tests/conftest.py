import pytest


@pytest.fixture
def test_kwargs():
    class TestKwargs(object):
        def __call__(self, **kwargs):
            self.__args = kwargs

        def get_args(self):
            return self.__args
    return TestKwargs()


@pytest.fixture
def call_count():
    class CallCount(object):
        __count = 0

        def __call__(self, *args, **kwargs):
            self.__count += 1

        def get_count(self):
            return self.__count
    return CallCount()
