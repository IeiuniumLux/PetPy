# PetPy
PetPy is a simple local HTTP server that lets you feed your pet remotely. The server receives a HTTP signal through the browser to activte the feeder. A food container (with a small hole in its side) is attached to the servo and when the it turns, a few pellets/kibble/treats drop into the bowl. You can adjust the hole and size of the container accordingly depending on whether you are feeding a cat, dog, or fish.

## Technology
PetPy is built on [MicroPython](http://micropython.org), the lean implementation of the Python 3 standard library that is optimised to run on microcontrollers and in constrained environments.  It uses the [GitHub Pages](https://pages.github.com/) to server the style.css as an external remote file instead of having it embedded into the Python script.

*NOTE: This web server is not meant to serve hundreds of connections or users since there's not much memory in the micropython boards and not a lot of processing power either. Therefore, this is really meant to just serve one user connection. However, it's nice to see that it can easly act as a simple control interface so a web page can send remote requests to control devices, or read analog inputs like the kind used for IOT projects. Notice also that I have little to no HTML, CSS, and Javascript experience so the code can definitely be improved.*
