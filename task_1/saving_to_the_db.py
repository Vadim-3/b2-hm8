from mongoengine import *
from json import load
import redis

connect(db='Cluster0',
        host='mongodb+srv://bezhukvadim56:VVBXIIBVTdILQpyb@cluster0.ssxsfik.mongodb.net/?retryWrites=true&w=majority')
client = redis.StrictRedis(host="localhost", port=6379, password=None)


class Author(Document):
    fullname = StringField(max_length=50, required=True)
    born_date = StringField(max_length=50)
    born_location = StringField(max_length=50)
    description = StringField()
    meta = {"collection": 'authors'}


class Quote(Document):
    tags = ListField(StringField(max_length=30))
    author = ReferenceField(Author)
    quote = StringField()
    meta = {"collection": 'quotes'}


def load_authors(filename):
    with open(filename, "r") as f:
        unpacked = load(f)
        for author in unpacked:
            result = Author(fullname=author['fullname'], born_date=author['born_date'],
                            born_location=author['born_location'], description=author['description'])
            result.save()
            print(result)


def load_quotes(filename):
    with open(filename, "r") as f:
        unpacked = load(f)
        for quote in unpacked:
            author_name = quote['author']
            author = Author.objects(fullname=author_name).first()
            quote['author'] = author
            result = Quote(
                tags=quote['tags'], quote=quote['quote'], author=quote['author'])
            result.save()
            print(result)


def command_name(name):
    if len(name) <= 2:
        cached_result = client.get(f'command_name:{name}')
        if cached_result:
            print(cached_result.decode('utf-8'))
        else:
            authors = Author.objects()
            authors_name = []
            for author in authors:
                author_name = author.fullname
                if author_name.lower().startswith(name):
                    authors_name.append(author_name)
            author_name = Author.objects(fullname=authors_name[0]).first()
            if author_name:
                quotes = Quote.objects(author=author_name)
                result = '\n'.join([quote.quote for quote in quotes])
                client.set(f'command_name:{name}', result)
                print(result)
            else:
                "Such an author does not exist"
    else:
        cached_result = client.get(f'command_name:{name}')
        if cached_result:
            print(cached_result.decode('utf-8'))
        else:
            author_name = Author.objects(fullname=name).first()
            if author_name:
                quotes = Quote.objects(author=author_name)
                result = '\n'.join([quote.quote for quote in quotes])
                client.set(f'command_name:{name}', result)
                print(result)
            else:
                "Such an author does not exist"


def command_tag(tag_name):
    if len(tag_name) <= 2:
        cached_result = client.get(f'command_tag:{tag_name}')
        if cached_result:
            print(cached_result.decode('utf-8'))
        else:
            quotes = Quote.objects()
            quotes_tag = []
            for quote in quotes:
                quote_tag = quote.tags
                for i in quote_tag:
                    if i.lower().startswith(tag_name):
                        quotes_tag.append(i)
            quotes = Quote.objects(tags=quotes_tag[0])
            result = '\n'.join([quote.quote for quote in quotes])
            client.set(f'command_tag:{tag_name}', result)
            print(result)
    else:
        cached_result = client.get(f'command_tag:{tag_name}')
        if cached_result:
            print(cached_result.decode('utf-8'))
        else:
            quotes = Quote.objects(tags=tag_name)
            result = '\n'.join([quote.quote for quote in quotes])
            client.set(f'command_tag:{tag_name}', result)
            print(result)


def command_tags(tags):
    tags_split = tags.split(",")
    quotes = Quote.objects(tags__in=tags_split)
    for quote in quotes:
        print(f"{quote.quote}")


def search():
    while True:
        command_input = input(
            "Please, enter your command as ('command: value'): ")
        command_split = command_input.split(":")
        command = []
        for i in command_split:
            command.append(i.strip())
        if command[0] == "name":
            command_name(command[1])
        elif command[0] == "tag":
            command_tag(command[1])
        elif command[0] == "tags":
            command_tags(command[1])
        elif command[0].lower() == "exit":
            break
        else:
            print(
                "You entered a command that does not exist, enter one of the commands listed ['name','tag','tags','exit']!")


search()
load_authors("authors.json")
load_quotes('quotes.json')
