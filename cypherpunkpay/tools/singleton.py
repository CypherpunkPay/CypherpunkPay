import threading


# See: https://stackoverflow.com/a/6798042
class Singleton(type):
    _lock = threading.RLock()
    _instances = {}

    def __call__(cls, *args, **kwargs):
        from cypherpunkpay import App
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            app: App = cls._instances[cls]
            return app
