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

    # ALR: do we need folder_id here?
    def create_dataset(self, name, paths_to_add=[], paths_to_upload=[], urls=[], annotation_task=None, 
                       folder_id=None, public=False) -> Dataset:
        
        #TODO: add documentation on annotation tasks and urls upload
        ''' Creates a dataset from an url or path

        Args:
            name: string, name of the Dataset
            files: list of paths of files
            urls: URL of images
            annotation_task: in case we are uploading annotations, specify the annotation task
            folder_id: 

        Returns: remo Dataset
        '''
        
        result = self.api.create_dataset(name, public)
        print(result)
        my_dataset = Dataset(self, **result)
        my_dataset.add_data(paths_to_add, paths_to_upload, urls, annotation_task, folder_id)
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

    def add_data_to_dataset(self, dataset_id, paths_to_add = [],
                            paths_to_upload=[], urls=[], annotation_task=None, folder_id=None):
        # JSONDecodeError: Expecting value: line 1 column 1 (char 0)
        '''
        Adds data to existing dataset
        
        Args:
            dataset_id: id of the desired dataset to extend (integer)
            files: path to data source 
            url: link to data source
            annotation_task:
            folder_id:
        '''
        
        
        result = {}
        if len(paths_to_add):
            if type(paths_to_add) is not list:
                raise ValueError ('Function parameter "paths_to_add" should be a list of file or directory paths, but instead is a ' + str(type(paths_to_add)))
                            
            files_upload_result = self.api.upload_files(dataset_id = dataset_id, 
                                                        paths_to_add = paths_to_add, 
                                                        paths_to_upload = [],
                                                        annotation_task = annotation_task, 
                                                        folder_id = folder_id,
                                                       status = None)
            
            result['files_link_result'] = files_upload_result  
            
        if len(paths_to_upload):
            if type(paths_to_upload) is not list:
                raise ValueError ('Function parameter "paths_to_upload" should be a list of file or directory paths, but instead is a ' + str(type(paths_to_upload)))
            
            files_upload_result = self.api.upload_files(dataset_id = dataset_id, 
                                                        paths_to_add = [], 
                                                        paths_to_upload = paths_to_upload,
                                                        annotation_task = annotation_task, 
                                                        folder_id = folder_id,
                                                       status = None)
            
            result['files_upload_result'] = files_upload_result  
            
        if len(urls):
            if type(urls) is not list:
                raise ValueError ('Function parameter "urls" should be a list of URLs, but instead is a ' + str(type(urls)))
                
            urls_upload_result = self.api.upload_files(dataset_id = dataset_id, 
                                                        paths_to_add = [], 
                                                        paths_to_upload = urls,
                                                        annotation_task = annotation_task, 
                                                        folder_id = folder_id,
                                                       status = None)
            
            print(urls_upload_result)
            result['urls_upload_result'] = urls_upload_result
        return result 
    
    def get_annotation_set(self, ann_set_id):
        result = self.api.get_annotation_set(ann_set_id)
        return result
    
    def list_annotation_sets(self, dataset_id):
        result = self.api.list_annotation_sets(dataset_id)
        return result
    
    def list_dataset_images(self, dataset_id, folder_id = None, endpoint=None, **kwargs):
        if folder_id is not None:
            result = self.api.list_dataset_contents_by_folder(dataset_id, folder_id, **kwargs)
        else:
            result = self.api.list_dataset_contents(dataset_id, **kwargs)
            
        #print('Next:', result.get('next'))
        images = []
        for entry in result.get('results', []):
            name = entry.get('name')
            images.append(name)

        return images
    
    def ann_statistics(self, dataset_id):
        result = self.api.get_annotation_statistics(dataset_id)
        return result