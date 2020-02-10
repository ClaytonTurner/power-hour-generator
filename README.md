# Power Hour Generator

## Installation
### Required Programs/Files
These are packages that need to be downloaded in order for this software to work.

In addition to downloading these files, you will need to add the folders you download below to your PATH.

How to add folders/files to your path: [Windows](http://windowsitpro.com/systems-management/how-can-i-add-new-folder-my-system-path) [Mac](http://architectryan.com/2012/10/02/add-to-the-path-on-mac-os-x-mountain-lion/#.WMxEafkrLIU) [Linux](http://askubuntu.com/questions/60218/how-to-add-a-directory-to-the-path)


#### Automatic installation

If you have homebrew installed, then you should be able to run the following to install the required programs
```shell script
brew install python && brew install ffmpeg && brew install youtube-dl
```

#### Manual installation

[Python 3](https://www.python.org/downloads/)  
Used to execute the program

[youtube-dl](https://rg3.github.io/youtube-dl/)  
This package is needed to download videos off of youtube


[ffmpeg](https://ffmpeg.org/download.html)  
This package is needed in order to splice videos from your local machine and add different videos together


### Confirm Installation

The following commands should give you filepaths to your installed/discoverable new software
```shell script
which python
which youtube-dl
which ffmpeg
```


### How to use

The key to running this program in its current state is the songs.txt file. In this directory currently is a songs.txt that I have tested and confirmed to work. The format is as follows:

```text
youtube link for beep
beep start time
beep end time
youtube link for song 1
song 1 start time
youtube link for song 2
song 2 start time
...
youtube link for song 60
song 60 start time
```

You don't have to add 60 songs/videos, but we currently only support going up to 60.

Once you have your songs.txt ready, then you should be able to create the power hour by running the power_hour.py file. This can be done either by double-clicking it in your file explorer (as .py files should be associated with python now) or opening up a command prompt/terminal, navigating to the directory with the file, and typing "python power_hour.py"

If any issues come up, then please post to the [Issues](https://github.com/ClaytonTurner/power-hour-generator/issues)


## Disclaimer

This software is not to be used for infringing upon copyright, but for personal use only
