
<img src="https://github.com/rediscovery-io/remo-python/blob/master/img/remo_normal.png" width="200">

# Welcome to Remo
Remo is an open-access web-application for managing and visualising images and annotations for Computer Vision. 

Use Remo to:

- visualise and inspect both datasets and annotations
- search for images with chosen classes or tags, and group them
- visualise statistics like # objects / class
- quickly annotate your images.

Remo runs on Windows, Linux and Mac. It is written using Python and React.JS and uses a lightweight database to store metadata.
To read more about Remo and download it, visit [remo.ai](http://remo.ai) (the website is still under construction :) )


This repo is an open-source implementation of our python SDK

## Remo python SDK

You can see example of usage of the SDK in the examples folder, and specifically in [the SDK examples Jupyer notebook](https://github.com/rediscovery-io/remo-python/blob/master/examples/Python-SDK-examples.ipynb)

What | Notebook
---|---
Quick Tour | [examples/Intro to Remo-SDK.ipynb](https://github.com/rediscovery-io/remo-python/blob/master/examples/Intro to Remo-SDK.ipynb)
Parsing annotations | parsing_annotations
Visualising predictions | visualise_predictions

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
