# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import create_app, db
from app.models import User, Group, Educator, Lesson

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Group': Group, 'Educator': Educator,
            'Lesson': Lesson}
