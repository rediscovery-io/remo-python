# PATHS AND DEFINITION

path_to_images =  './small_flowers/images/'
path_to_annotations = './small_flowers/annotations/'

cat_to_index = { 0 : 'Pink Primrose',  
                 1 : 'Hard-leaved Pocket Orchid', 
                 2 : 'Canterbury Bells'}

annotations_file_path = os.path.join(path_to_annotations, 'annotations.csv')

# GENERATING ANNOTATIONS
remo.generate_annotations_from_folders(path_to_data_folder = path_to_images, 
                                       output_file_path = annotations_file_path)

# GENERATING TRAIN TEST SPLIT
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

# CREATING DATASET WITHIN REMO
flowers =  remo.create_dataset(name = 'flowers', 
                              local_files = [path_to_images, path_to_annotations],
                              annotation_task = 'Image classification',
                              class_encoding = cat_to_index)

# VIEW DATASET AND ANNOTATIONS
flowers.view()

# ANALYZE ANNOTATIONS STATS/VIEW 
flowers.get_annotation_statistics()

flowers.view_annotation_stats()

# UPLOAD PREDICTIONS AND COMPARE MODEL AND GT
predictions = flowers.create_annotation_set(annotation_task='Image Classification', 
                                            name = 'model_predictions',
                                            paths_to_files = [train_test_split_file_path, model_predictions_path])

flowers.view()
