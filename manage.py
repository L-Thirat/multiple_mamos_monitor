from app_getonly import sql_db, MamosNetwork


def create_db():
    sql_db.create_all()


def delete():
    sql_db.drop_all()


def write_data(data):
    # data = MamosNetwork(ip = "xxx.xxx.x.x")
    sql_db.session.add(data)
    # sql_db.session.add(data)
    sql_db.session.commit()


def query():
    print(MamosNetwork.query.all())
    # MamosNetwork.query.first()
    # MamosNetwork.query.filter_by(ip="xxx.xxx.x.x")  # .first()
    # MamosNetwork.query.all()


# data = MamosNetwork(ip="192.168.8.104")
# write_data(data)
# query()
delete()
create_db()
