import atexit

from apscheduler.schedulers.background import BackgroundScheduler


class FlaskScheduler:
    def __init__(self, app=None, timezone=None, trigger="interval"):
        self.scheduler = BackgroundScheduler(timezone=timezone)
        self.app = app
        self._registered_functions = []

        self.trigger = trigger

    def init_app(self, app):
        self.app = app

    def start(self):
        for func in self._registered_functions:
            self.scheduler.add_job(func=func[0],
                                   trigger=self.trigger,
                                   seconds=func[2],
                                   minutes=func[3],
                                   hours=func[4])
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown())

    def register_job(self, func):
        return self.job(func)

    def job(self, seconds=0, minutes=1, hours=0):
        def inner(func):
            def wrapper():
                if self.app:
                    with self.app.app_context():
                        func()
            funcs = [f[1] for f in self._registered_functions]
            if len(self._registered_functions) == 0:
                self._registered_functions.append((wrapper, func, seconds, minutes, hours))
            elif func not in funcs:
                self._registered_functions.append((wrapper, func, seconds, minutes, hours))
            return wrapper
        return inner
