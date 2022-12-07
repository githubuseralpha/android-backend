import datetime
from . import scheduler, models, db

@scheduler.job
def clean_tokens():
    print('Removing')
    tokens = models.Token.query.filter(models.Token.expiration < datetime.datetime.now())
    tokens.delete()
    db.session.commit()
    