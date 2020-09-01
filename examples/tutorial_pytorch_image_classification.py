

# The path to the folders
path_to_images =  './small_flowers/images/'
path_to_annotations = './small_flowers/annotations/'

cat_to_index = { 0 : 'Pink Primrose',  
                 1 : 'Hard-leaved Pocket Orchid', 
                 2 : 'Canterbury Bells'}

annotations_file_path = os.path.join(path_to_annotations, 'annotations.csv')

remo.generate_annotations_from_folders(path_to_data_folder = path_to_images, 
                                       output_file_path = annotations_file_path)


im_list = [os.path.abspath(i) for i in glob.glob(path_to_images + '/**/*.jpg', recursive=True)]
im_list = random.sample(im_list, len(im_list))

# Definining the train test split
train_idx = round(len(im_list) * 0.8)
valid_idx = train_idx + round(len(im_list) * 0.1)
test_idx  = valid_idx + round(len(im_list) * 0.1)

# Creating a dictionary with tags
tags_dict =  {'train' : im_list[0:train_idx], 
              'valid' : im_list[train_idx:valid_idx], 
              'test' : im_list[valid_idx:test_idx]}

train_test_split_file_path = os.path.join(path_to_annotations, 'images_tags.csv') 
remo.generate_image_tags(tags_dictionary  = tags_dict, 
                         output_file_path = train_test_split_file_path)

# The annotations.csv is generated in the same path of the sub-folder
flowers =  remo.create_dataset(name = 'flowers', 
                              local_files = [path_to_images, path_to_annotations],
                              annotation_task = 'Image classification',
                              class_encoding = cat_to_index)

flowers.view()

flowers.get_annotation_statistics()

flowers.view_annotation_stats()

"""class FlowerDataset(Dataset):
    
    def __init__(self, annotations, train_test_valid_split, mapping = None, mode = 'train', transform = None):
        # Pandas is used to read in the csv file into a DataFrame for data loading
        self.data = pd.read_csv(annotations).set_index('file_name')
        self.train_test_valid_split = pd.read_csv(train_test_valid_split).set_index('file_name')
        self.data['tag'] = self.train_test_valid_split['tag']
        self.data.update(self.train_test_valid_split)
        self.data = self.data.reset_index()
        
        self.mapping = mapping
        self.transform = transform
        self.mode = mode
        
        i_index = self.data['tag'] == self.mode
        self.data_df = self.data[i_index][['file_name', 'class_name']].reset_index(drop = True)
        
    def __len__(self):
        return len(self.data_df)

    def __getitem__(self, idx):
        if self.mapping is not None:
            labels = int(self.mapping[self.data_df.loc[idx, 'class_name'].lower()])
        else:
            labels = int(self.data_df.loc[idx, 'class_name'])
        
        im_path = self.data_df.loc[idx, 'file_name']
        
        label_tensor =  torch.as_tensor(labels, dtype=torch.long)
        im = Image.open(im_path)
    
        if self.transform:
            im = self.transform(im)
    
        if self.mode == 'test':
            # For saving the predictions, the file name is required
            return {'im' : im, 'labels': label_tensor, 'im_name' : self.data_df.loc[idx, 'file_name']}
        else:
            return {'im' : im, 'labels' : label_tensor}"""


train_dataset = FlowerDataset(annotations =  annotations_file_path,
                              train_test_valid_split = train_test_split_file_path,
                              transform =  train_transforms,
                              mode =  'train')

valid_dataset = FlowerDataset(annotations = annotations_file_path,
                              train_test_valid_split = train_test_split_file_path,
                              transform = test_valid_transforms,
                              mode = 'valid')

test_dataset  = FlowerDataset(annotations = annotations_file_path,
                              train_test_valid_split = train_test_split_file_path,
                              transform = test_valid_transforms,
                              mode = 'test')

train_loader =  torch.utils.data.DataLoader(train_dataset, batch_size=5, shuffle=True, num_workers=1)
val_loader   =  torch.utils.data.DataLoader(valid_dataset, batch_size=1,  shuffle=False, num_workers=1)
test_loader  =  torch.utils.data.DataLoader(test_dataset,batch_size=1, shuffle=False, num_workers=1)
predictions = flowers.create_annotation_set(annotation_task='Image Classification', 
                                            name = 'model_predictions',
                                            paths_to_files = [train_test_split_file_path, model_predictions_path])

flowers.view()
