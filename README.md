## Remo python SDK

See examples of usage



## For contributors

SDK organized in simple layers:
- api
- sdk
- domain objects

`API` responsible for low level communication with server and returns raw data.

`SDK` doesn't access backend endpoints directly, only via `API`. Also this layer knows about domain objects, 
so instead of raw data, it can return domain objects.

`Domain objects` keeps entity information and knows about sdk, so most functions are simply short hands for sdk methods.
This layer doesn't know anything about `API`. 

End user mainly uses SDK and domain objects.


### Naming convension

* Function which responsible for open UI on specific page has prefix `view_`.
    
        view_dataset, view_annotations

* Function which returns one object has singular form.
    
        get_image(id) - returns one image

* Function which returns multiple objects has plural form.
    
        get_images() - may return multiple images 
