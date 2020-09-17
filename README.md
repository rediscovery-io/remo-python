<p align="center"><img src="https://github.com/rediscovery-io/remo-python/blob/master/img/remo_normal.png" width="200"></p>

<p align="center">
  <a href="https://pypi.org/project/remo/">
    <img src="https://img.shields.io/pypi/v/remo-python.svg?color=cool&logo=pypi&logoColor=white">
  </a>
  <a href="https://pypi.org/project/remo/">
    <img src="https://img.shields.io/pypi/dm/remo?color=cool&logo=pypi&logoColor=white">
  </a>
</p>

<p align="center">
    <a href="#welcome-to-remo">Welcome</a> •
  <a href="#features">Features</a> •
  <a href="#smirk-quick-installation">Installation</a> •
  <a href="#rabbit-remo-python-library">Remo-python</a> •
  <a href="#tada-whats-new">What's new</a> •
  <a href="#gift-what-we-are-working-on-next">What's next</a> •
  <a href="#bug-get-in-touch">Get in touch</a>
</p>

---

# Welcome to remo


Remo is a web-based application to organize, annotate and visualize Computer Vision datasets.

It has been designed to be your team's private platform to manage images, in an End-to-End fashion.
<br/>

**Use Remo to:**

- **access your datasets from one place**, avoiding scattered files and keeping data secure locally
- **quickly annotate** your images. We designed our annotation tool from the ground-up
- **build better datasets** and models, by exploring in depth your Images and Annotations data
- **collaborate with your team**, accessing the same data remotely

<br/>

<p align="center">Visualizing Datasets in Jupyter with Remo</p>
<p align="center"><img width="500" src="https://i.imgur.com/47wEEob.gif"></p>

---

<p align="center">Annotating using Bounding Box and smart zoom</p>
<p align="center"><img width="500" src="https://i.imgur.com/hm1tH4p.gif"></p>


----

<br/>

## Features

*Configuration*

- Runs on Windows, Linux, Mac or directly in Google Colab Notebooks
- Can be served on a private server, accessed remotely for team collaboration
- Can be accessed from within Jupyter Notebooks, a browser tab or on its own app

<br/>

*Supported data*

- Compatible with all the most common image formats: jpeg, jpgs, png, tiff
- Support for many annotation formats: import and export using a variety of formats (CoCo, Pascal, CSV, etc) and options (skip images witha no annotations, append file paths, etc)
- Abiliy to upload data directly from URLs or as an archive


<br/>

*Annotation*

- Support for Polygons, Bounding boxes, Image labels and Tags
- Manage annotation progress: Sort images by On Hold, Done, To Do and visualize % completion
- Faster annotation thanks to keyboard shortcuts and the custom design
- One-click group actions: rename or delete objects of a class, duplicate sets of annotation


<br/>

*Dataset management*

- Centralized access to your data - link directly to your images, in whatever folder they are
- Easily query your data, searching by filename, class, tag
- Immediately visualize aggregated statiscs on your datasets
- Version your annotations using Annotation Sets, and your images using virtual datasets


<br/>

*Integration from code*

- An easier way to pass annotations and image data to your models
- Visualize and store your annotations and predictions
- Create multiple virtual train/test splits without needing to move data around

<br/>

<p align="center"><img src=examples/assets/dataset.jpeg alt="alt text" width=400><img src=examples/assets/annotation_tool.jpeg width=400></p>

**About Remo**

- Remo is written using Python, React.JS and PostgreSQL to store metadata
- This repo is the open source repo for the Remo python library, which allows to call Remo directly from Python
- Remo itself has a permissive license, allowing for free commercial use (provided you give credits and don't redistribute or expose a modified version)
- Read more here: [remo.ai](http://remo.ai)


<br/>

## :smirk: Quick installation

1. In a Python 3.6+ environment: `pip install remo` 

This will install both the Python library and the remo app.

2. Initialise config: `python -m remo_app init`


That's it! 

To launch Remo, run `python -m remo_app`. 
To call Remo from python once you have a server running, use `import remo`.


To read more about installation and other features, visit [remo.ai](http://remo.ai)


<br/>




## :rabbit: Remo python library

You can see example of usage of the library in our documentiation or in the examples folder. 

What | Where | Colab Links
---|--- | ---
Documentation | [Official Docs](https://remo.ai/docs/sdk-intro/) | -
Intro Notebook | [Intro to Remo-Python notebook](examples/intro_to_remo-python.ipynb) | -
Uploading annotations | [Upload Annotations and Predictions Tutorial notebook](examples/tutorial_upload_annotations.ipynb) | -
PyTorch Image Classification using Remo | [PyTorch Image Classification notebook](examples/tutorial_pytorch_image_classification.ipynb) | [![im_classification_tutorial](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/rediscovery-io/remo-python/blob/master/examples/google-colab/tutorial_pytorch_image_classification.ipynb)
PyTorch Object Detection using Remo | [PyTorch Object Detection Notebook](examples/tutorial_pytorch_object_detection.ipynb) | [![obj_detection_tutorial](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/rediscovery-io/remo-python/blob/master/examples/google-colab/tutorial_pytorch_object_detection.ipynb)

<br/>

## :tada: What's new
1-Sep-2020: Added tutorial on Remo for PyTorch Object Detection

<br/>

## :gift: What we are working on next

- Tighter integration with PyTorch
- Ability to split datasets in train vs test
- Ability to store and inspect models' performance in remo

<br/>

## :bug: Get in touch
If you have any issues around the library, feel free to open an issue in the repo.

For anything else, you can write on our <a href="https://discuss.remo.ai" target="_blank">discuss forum.</a>  

<br/>

## :raising_hand: For contributors

The library is organized in 3 main layers:
- api
- sdk
- domain objects, such as datasets

We exepect the end user to use mainly the SDK layer and domain objets.

`API` is responsible for low level communication with the server. It mostly returns raw data.

`SDK` doesn't access backend endpoints directly, rather it uses the `API` layer for that. This layer knows about domain objects, 
so instead of raw data, it returns domain objects.

`Domain objects` keeps entity information and knows about the `SDK` layer. Most functions are simple short-hands for sdk methods.
This layer doesn't know anything about `API`. 



### Naming conventions

* Functions which are responsible to open the UI on a specific page use the `view_` prefix
    
        view_dataset, view_annotations

* Functions which return always only one object, present the name of that object in singular form.
    
        get_image(id) - returns one image

* Functions which might return multiple objects use the plural form of that object
    
        get_images() - may return multiple images 
