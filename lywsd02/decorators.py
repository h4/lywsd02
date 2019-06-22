def with_connect(func):
    def wrapper(self, *args, **kwargs):
        self._peripheral.connect(self._mac)
        result = func(self, *args, **kwargs)
        self._peripheral.disconnect()
        return result

    return wrapper
