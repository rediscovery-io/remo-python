
#----------------------------------------------------------
#    (\(\
#    (>':')  Remo
#
#  NB: This script is a simple conversion of the Python SDK example notebook
#----------------------------------------------------------

# coding: utf-8

# In[1]:


import sys
# MC: need to specify path to remo in notebook
local_path_to_repo =  'C:/Users/Andrea.LaRosa/Desktop/Projects/repo/rem_repo/remo-python'

sys.path.insert(0, local_path_to_repo)


# In[2]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')
import remo


# # Basic functionalities
# - Create dataset
# - Visualize the dataset in the UI
# - List and retrieve existing dataset
# - Add data to existing dataset
# - Print annotations statistcs
# - Visualize statistics dashboard

# ## Create and visualize a dataset
#

# Let's create a new dataset.
#
# The following code will create an entry in our database, which allows us explore the data via the remo app.
#
# How to load data:
# - We can pass an url to a remote archive, containing images and optionally annotations
# - We can also pass paths to local data, as folders or list of files
#
# When creating a dataset, we would also need to specify the name of the dataset and the task of the annotation, if any.
#
# Read more about what type of annotation tasks and formats we support in [our documentation](https://remo.ai/docs/annotation-formats/).
#
#
#
#
#

# In[3]:


urls = ['https://remo-scripts.s3-eu-west-1.amazonaws.com/open_images_sample_dataset.zip']

my_dataset = remo.create_dataset(name = 'open images detection',
                    urls = urls,
                    annotation_task = "Object detection")


#
#
# We can now visualize the dataset - this will open the UI in a separate window:

# In[4]:


my_dataset.view()


# We can later on add additional data to the dataset

# In[5]:


urls = ['https://remo-sample-datasets.s3-eu-west-1.amazonaws.com/open-image-sample_142.zip']

my_dataset.add_data(urls = urls,
                    annotation_task = "Object detection")


# ## List datasets & retrieve a specific dataset

# Let's list all of the datasets we uploaded in our local remo:

# In[6]:


my_datasets = remo.list_datasets()
my_datasets


# we can then get a remo dataset using its id

# In[9]:


my_dataset = remo.get_dataset(91)


# ## Explore annotations

# To explore annotations, we can print the stats of the annotation sets:

# In[12]:


my_dataset.get_annotation_statistics()


# Or we can view an interactive graph on the UI:

# In[13]:


my_dataset.view_annotation_statistics()


# ----
# # Annotation Sets

# Under the hood, Remo groups annotations in **Annotation Sets**.
#
# An Annotation Set is defined by:
# - a task (currently, one of: object detection, instance segmentation, image classification)
# - a list of classes to use
# - a list of of annotations for each image
# - a list of tags for each image
#
# The nice thing about explictly grouping annotations together is that we can easily manipulate these annotations to cover a variety of use cases, e.g.:
#
# - create a copy of annotation set
# - experiment grouping together classes or further separate objects of one class, based on models performance
# - use tags to group together certain type of images
# - compare annotations from different annotators
#
# ### How does it work
# Each dataset can have a number of different annotation set.
# To simplify things, Remo allows to select a *default* annotation set so that when an annotation set is not specified, it will be assumed that you refer to the default annotaiton set.
#
# The default annotation is the first annotation set you create - but this can be changed by passing the chosen annotation set id to  `dataset.default_annotation_set`
#
# <br>
#
# Before running the code below, I have manually created an annotation set from the UI:
# <br>
# <br>
#

# In[17]:


# this updates the dataset object to match the db
my_dataset.fetch()
my_dataset.annotation_sets


# In[18]:


my_dataset.default_annotation_set


# ### Annotate a specific annotation set

# In[19]:


my_dataset.view_annotate(38)


# Example of annotation tool:
#
# ![image.png](attachment:image.png)

# Now, if we list datasets again the datasets we have, we will see an increased number of objects in the annotation set "animal_plant_object"
#

# In[20]:


my_dataset.fetch()
my_dataset.annotation_sets


# In[21]:


my_dataset.get_annotation_statistics(38)


# In[22]:


my_dataset.view_annotation_statistics(38)


# ### Get annotations

# We can get annotations of our dataset using get_annotatins(). If annotation_set_id is not specified it returns default annotations.

# In[23]:


annotation_sample = my_dataset.export_annotations()


# In[24]:


annotation_sample[0]


# ### Export annotations to csv

# In[27]:


my_dataset.export_annotation_to_csv(output_file='output.csv')


# In[32]:


import pandas as pd
df = pd.read_csv('output.csv')
df.head()


# In[33]:


my_dataset.export_annotation_to_csv(annotation_set_id=38, output_file='output2.csv')
df2 = pd.read_csv('output2.csv')
df2.head()


# # Search Images

# ### View search bar

# Browse the search bar in Remo

# In[34]:


remo.view_search()


# ### Search images by class and task

# Let's search for images within our dataset that have both a dog and a person in it.

# In[38]:


result = my_dataset.search_images(class_list=['Dog,person'], task=remo.task.object_detection)


# In[37]:


result[0]


# List images in a dataset

# In[42]:


my_list = my_dataset.list_images()
my_list[:5]


# ### View images

# In[43]:


my_dataset.view_image(34597)


# ### Plot Images by ID

# We can get and plot images using directly through dataset.get_images(image_id)

# In[44]:


from PIL import Image
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

result = my_dataset.get_images_by_id(34597)
img = Image.open(result)
img = img.save("img.jpg")


# In[45]:


image = plt.imread('img.jpg')
fig, ax = plt.subplots()
im = ax.imshow(image)
plt.show()


# ### Plot Images by Classes and Tasks

# You can get images by filtering classes and tasks

# In[49]:


from PIL import Image
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

result = my_dataset.get_images_by_search(class_list=['Dog'], task=remo.task.object_detection)


# In[52]:


result[0:3]


# In[53]:


for _img in result[0:3]:
    im = Image.open(_img['img'])
    im = im.save("im.jpg")
    image = plt.imread('im.jpg')
    fig, ax = plt.subplots()
    im = ax.imshow(image)
    plt.show()
