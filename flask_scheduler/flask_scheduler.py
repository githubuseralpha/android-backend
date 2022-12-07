import atexit

from apscheduler.schedulers.background import BackgroundScheduler


class FlaskScheduler:
    def __init__(self, app=None, seconds=0, minutes=0, hours=0,
                 timezone=None, trigger="interval"):
        self.scheduler = BackgroundScheduler(timezone=timezone)
        self.app = app
        self._registered_functions = []

        self.seconds = seconds
        self.minutes = minutes
        self.hours = hours
        self.trigger = trigger

    def init_app(self, app):
        self.app = app

    def start(self):
        for func in self._registered_functions:
            self.scheduler.add_job(func=func[0],
                                   trigger=self.trigger,
                                   seconds=self.seconds,
                                   minutes=self.minutes,
                                   hours=self.hours)
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown())

    def register_job(self, func):
        return self.job(func)

    def job(self, func):
        def wrapper():
            if self.app:
                with self.app.app_context():
                    func()
        if len(self._registered_functions) == 0:
            self._registered_functions.append((wrapper, func))
        elif func not in self._registered_functions[:][1]:
            self._registered_functions.append((wrapper, func))
        return wrapper
