import sys
import os
import pyodbc

binpath = sys.argv[1]

sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'braindump'))
print(os.path.abspath('.'))
#kill the sphinx search daemon
os.system('killall searchd')
# update the indexes
os.system(binpath +'indexer --all')
# start the daemon
os.system(binpath +'searchd')

from settings import DATABASES

server =  '127.0.0.1'
database = DATABASES['default']['NAME']
uid = DATABASES['default']['USER']
password = DATABASES['default']['PASSWORD']

cnxn = pyodbc.connect('DRIVER={PostgreSQL uniCODE};SERVER=%s;PORT=5432;DATABASE=%s;UID=%s;PWD=%s' % (server, database, uid, password))

cursor = cnxn.cursor()

cursor.execute('delete from core_searchcache')
cursor.commit()


