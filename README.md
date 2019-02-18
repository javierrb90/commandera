# CommandEra
A little command line tool that you can use to browse the ResetEra's forum boards and read its threads

## Getting Started

### Prerequisites

The project comes with a requirements.txt file with all the libraries that you should need:

```
beautifulsoup4
requests
colorama
PyInquirer
```

Just do a ...
```
pip install -r requirements.txt
```

And you should be ready to go.

### Installing

After cloning the repo and installing the required libraries you should be able to install the project without any issues.

Just go to the root of the folder where you have cloned it, and manually install it using pip:

```
pip install .
```

After that you should be able to execute it from the command line with...

```
python -m commandera
```

...Or directly importing it to an existing python project (I don't know why you'd want to do that, though)

```
from commandera import Era
Era()
```
## Screenshots
### Which board to browse
![Which board to browse](https://i.imgur.com/HHSjaWL.png "Which board to browse")
### Which thread to read
![Which thread to read](https://i.imgur.com/vl7G8m1.png "Which thread to read")

### Where to start reading the thread

![Where to start reading the thread](https://i.imgur.com/hwzayYW.png "Where to start reading the thread")

### How to comments are formated

The images' links are parsed to strings, and the quotes are wrapped in a white background:

![How to comments are formated](https://i.imgur.com/hpy6mCv.png "How to comments are formated")

### It parses even the tweets
![It parses even the tweets](https://i.imgur.com/GzRbUrS.png "It parses even the tweets")

### ...and the spoilers are also taken into account!
You should be able to read them if you click on them using your mouse
![The spoilers are also taken into account](https://i.imgur.com/ppF6tdf.png "The spoilers are also taken into account")