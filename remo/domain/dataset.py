from .. import utils
#from .api import API
import psycopg2
from PIL import Image
from io import BytesIO
import requests

class data:
    @staticmethod
    def repr(obj):
        items = []
        for prop, value in obj.__dict__.items():
            try:
                item = "%s = %r" % (prop, value)
                assert len(item) < 20
            except:
                item = "%s: <%s>" % (prop, value.__class__.__name__)
            items.append(item)

        return "%s(%s)" % (obj.__class__.__name__, ', '.join(items))

    def __init__(self, cls):
        cls.__repr__ = data.repr
        self.cls = cls

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)
    
#@data
class Dataset:
    """remo long desc """
    __doc__ = "dataset from remo!"
    
    def __repr__(self):
        return "Dataset {} - '{}'".format(self.id, self.name)
        
    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.annotation_sets = kwargs.get('annotation_sets')
        self.created_at = kwargs.get('created_at')
        self.license = kwargs.get('license')
        self.is_public = kwargs.get('is_public')
        self.users_shared = kwargs.get('users_shared')
        self.top3_classes = kwargs.get('top3_classes')
        self.total_classes = kwargs.get('total_classes')
        self.total_annotation_objects = kwargs.get('total_annotation_objects')
   
    def __str__(self):
        return 'Dataset (id={}, name={})'.format(self.id, self.name)

    def upload(self, files=[], urls=[], annotation_task=None, folder_id=None):
        '''
        uploads the dataset to existing one
        '''
        return self.sdk.upload_dataset(self.id, files, urls, annotation_task, folder_id)

    def fetch(self):
        dataset = self.sdk.get_dataset(self.id)
        self.__dict__.update(dataset.__dict__)

    def browse(self):
        utils.browse(self.sdk.ui.dataset_url(self.id))

    def annotate(self):
        # TODO: select by annotation task
        print(self.annotation_sets)
        if len(self.annotation_sets) > 0:
            utils.browse(self.sdk.ui.annotate_url(self.annotation_sets[0]))
        else:
            print("No annotation sets in dataset " + self.name)

    def images(self, folder_id = None, **kwargs):
        return self.sdk.list_dataset_images(self.id,folder_id = None, **kwargs)

    def search(self, **kwargs):
        pass
    
    def ann_statistics(self):
        #cur = self.sdk.con.cursor()
        # we won't need this after arranging endpoints
        con = psycopg2.connect(database=.., user=.., password=.. host=.., port=..)
        cur = con.cursor()
        query = "SELECT t.* FROM public.annotation_set_statistics t where dataset_id = %s"
        cur.execute(query % self.id)
        rows = cur.fetchall()

        statistics = dict()
        for row in rows:
            statistics["Annotation SET ID "] = row[1]
            statistics["Classes"] = row[2]
            statistics["Tags"] = row[4]
            statistics["Top3 Classes"] = row[5]
            statistics["Total Classes"] = row[6]
            statistics["Total Annotated Images"] = row[7]
            statistics["Total Annotation Objects"] = row[8]
      
        self.sdk.con.close()
        return statistics 
        
        
    def get_images(self, cls=None, tag=None):
        # TODO: add class and tags 
        dataset_details = self.sdk.all_info_datasets() 
        dataset_info = None
        for res in dataset_details['results']:
            if res['id'] == self.id:
                dataset_info = res
        url_ = dataset_info.get('image_thumbnails')[0]['image']
        bytes_ = (requests.get(url_)).content
        # TODO: get list of the images
        rawIO = BytesIO(bytes_)

        return rawIO
    
    def show_images(self, cls=None, tag=None):
        # TODO: redirect to ui with endpoints
        img = self.get_images(cls, tag)
        return Image.open(img)
  
    
    def show_objects(self, cls, tag):
        pass
        

 