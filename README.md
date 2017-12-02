# PetPy
When away, make sure your pet [fish, cat, dog] never goes hungry with this remote activated feeder/treat dispenser.

DISCLAIMER: This web server is not meant to serve millions of connections or thousands of users since there's not much memory in the micropython boards and not a lot of processing power either. Therefore, this is really meant to just serve one user connection. However, it can act as a simple control interface to publish an API or a protocol so a web page can send a request to turn ON a light, a relay, a servo, or read analog inputs like the kind used for IOT projects. Also note that I have little to no HTML, CSS, and Javascript experience so they can definitely be improved.

## How it works:

The feeder receives a HTTP signal through a browser HTML page to activte the servo. A food container [with a small hole in its side] is attached to the servo and when the it turns, a few pellets/kibble/treats drop into the bowl. You can adjust the hole and size of the container accordingly depending on whether you are feeding a cat, dog, or fish.

The standard GitHub repos aren't web hosting servers so I use the pages.github.com to server the style.css and the script.js as external files instead of having them embedded into the Python script.

