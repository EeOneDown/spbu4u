from app import db, create_app
from app.models import Group, Educator


def create_obj():
    first_group = Group(id=0, title="No Group")
    db.session.add(first_group)

    first_edu = Educator(id=0, title="No Educator")
    db.session.add(first_edu)

    db.session.commit()


def check_obj():
    first_group = Group.query.filter_by(title="No Group").first()
    if first_group.id != 0:
        first_group.id = 0
        db.session.add(first_group)

    first_edu = Educator.query.filter_by(title="No Educator").first()
    if first_edu.id != 0:
        first_edu.id = 0
        db.session.add(first_edu)

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        create_obj()
        check_obj()
