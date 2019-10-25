from peewee import *
import json
from remo.domain.task import AnnotationTask
# from playhouse.postgres_ext import PostgresqlExtDatabase

#db = PostgresqlExtDatabase('postgres', user=' postgres', password='admin',host='localhost', port=5432,
#                            autocommit=True, autorollback=True)


# db_path = '../.remo/remo_db.sqlite3'
db = None
# db = SqliteDatabase(db_path, autocommit=True, autorollback=True)
#
# try:
#     db
# except NameError:
#     print("\nERROR! Initialise 'db' to be")
#     print("'=PostgresqlExtDatabase('x', user='x', password='x',host='x', port=x,autocommit=True,autorollback=True)'\n")
#
# db.connect()


class pewee_BaseModel(Model):
    class Meta:
        database = db

class pewee_Table(pewee_BaseModel):
    id = AutoField()
    name = CharField()
    license_id = IntegerField()
    
class pewee_AnnotationStats(pewee_BaseModel):
    id = AutoField()
    annotation_set_id = IntegerField()
    classes = CharField()
    tags = CharField()
    top3_classes = CharField()
    total_classes = IntegerField()
    total_annotated_images = IntegerField()
    total_annotation_objects = IntegerField()
    dataset_id = IntegerField()
    
    
class pewee_AnnotationSets(pewee_BaseModel):
    id = AutoField()
    name = CharField()
    dataset_id = IntegerField()
    task_id = IntegerField()
    user_id = IntegerField()
    ann_stats = ForeignKeyField(pewee_AnnotationStats)
    
class pewee_Annotation(pewee_BaseModel):
    id = AutoField()
    # MC: Some of them are actually binary json but
    # BinaryJSONField() is not recognized in the package
    classes = CharField()
    tags = CharField()
    task = CharField()
    data = CharField()
    annotation_set_id = IntegerField()
    dataset_id = IntegerField()
    image_id = IntegerField()
    annotation_sets = ForeignKeyField(pewee_AnnotationSets)

def get_dataset_info(table_name = 'datasets'):
    new_table = pewee_Table
    if table_name is not None:
        new_table._meta.set_table_name(table_name)
    query = new_table.select()
    dataset_info = []
    for q in query:
        dataset_info.append({'id':q.id, 'name':q.name, 'license_id':q.license_id})
    return dataset_info

def list_annotation_sets(dataset_id):
    '''
    Given a dataset_id returns information of its annotation sets
    '''
    annotation_set = pewee_AnnotationSets
    annotation_set._meta.set_table_name('annotation_sets')
    annotation_stats = pewee_AnnotationStats
    annotation_stats._meta.set_table_name('annotation_set_statistics')
 
    base_query = annotation_set.select(annotation_set.name, annotation_set.id, annotation_set.task_id,
                                   annotation_stats.classes).join(annotation_stats, 
                                                        on=(annotation_set.id==annotation_stats.annotation_set_id))
    annotation_sets = []
    for q in base_query.where(annotation_set.dataset_id == dataset_id):
        # TODO: n_classes using query count()
        n_classes = len(json.loads(q.ann_stats.classes))
        annotation_sets.append({'annotation_name':q.name, 'annotation_set_id':q.id, 'task':q.task_id,
                             'num_classes':n_classes})
    return annotation_sets

#def get_annotation_set(ann_set_id):
#    '''
#    Given an annotation_set_id returns its information
#    '''
#    annotation = pewee_Annotation
#    annotation._meta.set_table_name('new_annotations')
#    annotationSets = pewee_AnnotationSets
#    annotationSets._meta.set_table_name('annotation_sets')
#    
#    base_query = annotation.select(annotation.id, annotation.classes, annotation.tags, annotation.task, annotation.data, 
#                                   annotation.annotation_set_id, 
#                              annotationSets.name, annotation.dataset_id, annotation.image_id).join(annotationSets, 
#                                                        on=(annotation.annotation_set_id==annotationSets.id))
#    annotation_set = []
#    for q in base_query.where(annotation.annotation_set_id == ann_set_id):
#        annotation_set.append({'id':q.id, 'classes':q.classes, 'tags':q.tags, 'task':q.task, 'data':q.data, 
#                             'annotation_set_id':q.annotation_set_id, 'annotation_set_name': q.annotation_sets.name,
#                               'dataset_id':q.dataset_id, 'image_id':q.image_id})
#    return annotation_set

#def get_annotation_statistics(dataset_id):
#    '''
#    Given a dataset id returns its annotation set statistics
#    '''
#    annotation_statistics = pewee_AnnotationStats
#    annotation_statistics._meta.set_table_name('annotation_set_statistics')
#    query = annotation_statistics.select(annotation_statistics.id, annotation_statistics.annotation_set_id, annotation_statistics.classes, 
#                                             annotation_statistics.tags, annotation_statistics.top3_classes, annotation_statistics.total_classes, annotation_statistics.total_annotated_images, annotation_statistics.total_annotation_objects).where(annotation_statistics.dataset_id == dataset_id)
#    ann_stats = []
#    for q in query:
#        ann_stats.append({'id': q.id, 'annotation_set_id': q.annotation_set_id, 'classes':q.classes, 'tags': q.tags, 'top3_classes': q.top3_classes, 'total_classses': q.total_classes, 'total_annotated_images': q.total_annotated_images, 'total_annotation_objects': q.total_annotation_objects})
#    return ann_stats
        
    
