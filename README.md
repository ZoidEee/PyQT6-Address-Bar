# PyQT6-Address-Bar


This is a Address Bar or BreadCrumb Navigation that is implemented on file managers and explorers.

This was created in due, to the fact I was unable to find any material online in how to create one using PyQt6.

Two custom classes are used to achieve this:
  1. AddressBarLabel
    - is used for the names of the directories in the path being displayed
    - is also used for emitting a signal (directory name) when clicked on to load the directory corresponding to that name
  2. AddressBar
    - is used for the layout of the address bar.
    - is used used for emitting a signal (path)
    - is used for connecting the actions to the MainWindow as well 

