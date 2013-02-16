import os
import pyodbc
from elementtree import TidyTools, ElementTree as ET

import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'braindump'))
from settings import DATABASES

server =  '127.0.0.1'
database = DATABASES['default']['NAME']
uid = DATABASES['default']['USER']
password = DATABASES['default']['PASSWORD']

cnxn = pyodbc.connect('DRIVER={PostgreSQL uniCODE};SERVER=%s;PORT=5432;DATABASE=%s;UID=%s;PWD=%s' % (server, database, uid, password))
cursor = cnxn.cursor()

class XML:
	def __init__(self):
		self.root = ET.Element('sphinx:docset')
		self.get_schema()
	
	def get_schema(self):
		self.schema = ET.SubElement(self.root, 'sphinx:schema')
		ET.SubElement(self.schema, 'sphinx:field', {'name':'text'})
		ET.SubElement(self.schema, 'sphinx:attr', {'name':'uid', 'type':'int'})

	def get_tags(self):

		for row in cursor.execute("select * from core_tag"):			
			doc = ET.SubElement(self.root, 'sphinx:document', {'id':'%s' % str(row.id)})
			
			elsubject = ET.SubElement(doc, 'text')
			elsubject.text = row.name
			elsubject.attrib['uid'] = '1'
		
	def output(self):
		return ET.tostring(self.root, 'UTF-8')



tags = XML()
tags.get_tags()
print(tags.output())
		

