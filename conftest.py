from pytest_socket import disable_socket

pytest_plugins = [
    "tests.fixtures",
]

def pytest_runtest_setup():
    disable_socket()
