import os


SCRAPPER_DATABASES = {
    'default': {
        'engine': 'pymongo',
        'host': os.environ.get('MONGO_HOST', 'localhost'),
        'port': os.environ.get('MONGO_PORT', 27017),
        'db_name': os.environ.get('MONGO_DB_NAME', 'overbot')
    }
}
