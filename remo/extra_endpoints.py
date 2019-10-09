from peewee import *

db = PostgresqlExtDatabase('postgres', user='postgres', password='admin',host='localhost', port=5432)
db.connect()


class Table(Model):
    id = AutoField()
    name = CharField()
    license_id = IntegerField()
    
    
    def get_attributes_dict():
        my_dict_keys = ['id','name', 'license_id']
        return my_dict_keys
    
    class Meta:
        database = db

         
def get_dataset_info(table_name = 'datasets'):
    new_table = Table
    if table_name is not None:
        new_table._meta.set_table_name(table_name)
    query = new_table.select()
    dataset_info = []
    for q in query:
        dataset_info.append({'id':q.id, 'name':q.name, 'license_id':q.license_id})
    return dataset_info