from .api import API
from .domain.dataset import Dataset
from .ui import UI

class SDK:
    def __init__(self, server, user_email=None, user_password=None):
        self.api = API(server)
        self.ui = UI(server)
        if user_email and user_password:
            self.api.login(user_email, user_password)

    def search_images(self, search_terms_dictionary):
        result = self.api.search_images(search_terms_dictionary) 
        
    def login(self, user_email, user_pwd):
        self.api.login(user_email, user_pwd)

    def create_dataset(self, name, public=False,  
                       files=[], urls=[], annotation_task=None, folder_id=None) -> Dataset:
        ''' creates a dataset from an url or path
        name: string
        files: 
        urls: link to data source
        '''
        result = self.api.create_dataset(name, public)
        print(result)
        my_dataset = Dataset(self, **result)
        my_dataset.add_data(files, urls, annotation_task, folder_id)
            
        return my_dataset
    
    def list_datasets(self):
        dataset_info = self.api.list_datasets()
        return dataset_info
        
    def all_info_datasets(self, **kwargs) -> [Dataset]:
        result = self.api.all_info_datasets(**kwargs)
        return result
    
    def get_dataset(self, dataset_id) -> Dataset:
        '''
        Given a dataset id, returns the dataset
        '''
        result = self.api.get_dataset(dataset_id) 
        return Dataset(self, **result)

    def add_data_to_dataset(self, dataset_id, files=[], urls=[], annotation_task=None, folder_id=None):
        # JSONDecodeError: Expecting value: line 1 column 1 (char 0)
        '''
        adds data to existing dataset
        dataset_id: id of the desired dataset to extend (integer)
        files: path to data source 
        url: link to data source
        annotation_task:
        folder_id:
        '''
        result = {}
        if len(files):
            files_upload_result = self.api.upload_files(dataset_id, files, annotation_task, folder_id)
            result['files_upload_result'] = files_upload_result
        if len(urls):
            urls_upload_result = self.api.upload_urls(dataset_id, urls, annotation_task, folder_id)
            print(urls_upload_result)
            result['urls_upload_result'] = urls_upload_result
        return result 
    
    def get_annotation_set(self, ann_set_id):
        result = self.api.get_annotation_set(ann_set_id)
        return result
    
    def list_annotation_sets(self, dataset_id):
        result = self.api.list_annotation_sets(dataset_id)
        return result
    
    def list_dataset_images(self, dataset_id, folder_id = None, **kwargs):
        if folder_id is not None:
            result = self.api.list_dataset_contents_by_folder(dataset_id, folder_id, **kwargs)
        else:
            result = self.api.list_dataset_contents(dataset_id, **kwargs)
            
        print('Next:', result.get('next'))
        images = []
        for entry in result.get('results', []):
            name = entry.get('name')
            images.append(name)

        return images
   