from mongoengine import *

connect(db='Cluster0',
        host='mongodb+srv://bezhukvadim56:VVBXIIBVTdILQpyb@cluster0.ssxsfik.mongodb.net/?retryWrites=true&w=majority')


class Model(Document):
    fullname = StringField()
    email = StringField()
    boolean = BooleanField(default=False)
    meta = {"collection": 'email'}
