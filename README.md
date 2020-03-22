
<img src="https://github.com/rediscovery-io/remo-python/blob/master/img/remo_normal.png" width="200">

# Welcome to Remo
This the open source repository for Remo python library.

Remo is an open-access web-application for managing and visualising images and annotations for Computer Vision. 

Use Remo to:

- **visualise and inspect** datasets and annotations
- **organise and search** your images
- **visualise statistics** like # objects per class
- **quickly annotate** your images

Remo runs on Windows, Linux and Mac. It is written using Python and React.JS and uses a lightweight database to store metadata.

## Quick installation

1. In a Python 3.6+ environment: `pip install remo` 

This will install both the Python library and the remo app.
If it is installed in a conda environment, calling ` import remo` will also automatically launch remo. Otherwise, you can call it with `python -m remo_app` from command line.

2- Initialise config: `python -m remo_app init`


To read more about Remo, visit [remo.ai](http://remo.ai) (the website is still under construction)

<img src=examples/assets/dataset.jpeg alt="alt text" width=400><img src=examples/assets/annotation_tool.jpeg width=400>

<br/>




## Remo python SDK

You can see example of usage of the SDK in our documentiation or in the examples folder. 

What | Where
---|---
Documentation | [Official Docs](https://remo.ai/docs/sdk-intro/)
Intro Notebook | [Intro to Remo-Python notebook](examples/intro_to_remo-python.ipynb)
Uploading annotations | [Upload Annotations Tutorial notebook](examples/tutorial_upload_annotations.ipynb)
Visualising predictions | visualise_predictions - Coming soon

<br/>

## Get in touch
If you have any issues around the SDK, feel free to open an issue in the repo.
For general questions around Remo, you can get in touch at hello AT remo.ai

<br/>

## For contributors

The SDK is organized in 3 main layers:
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
