### QGIS Tutorials

# QGIS Tasks – delegate chores to the background

This tutorial shows how to use tasks in pyQGIS by giving a short introduction to the concept and giving an example of how tasks may be utilized in an example plugin. We assume that you are familiar with pyQgis and the basics of plugin development in QGIS. In case you want to catch up on the latter, please refer to our [QGIS plugin development guide](https://gis-ops.com/qgis-3-plugin-tutorial-plugin-development-reference-guide/).

**Goals:** 
- become familiar with the concept of tasks in pyQGIS
- be able to apply it in plugin development

Imagine you are developing a plugin that requires the user to download huge amounts of geodata and do something with it afterwards. If you simply start the download in your main plugin code, you will notice that the whole program freezes until the download finishes and the rest of the plugin logic completes. What if you wanted to let the user keep using QGIS while the download takes place? Enter tasks, or – more specifically – `QgsTask`. 
Tasks help to perform work in the background, while giving the user GUI control. So not only is this useful for CPU intense work, but also for operations where little of your machine's computing resources are needed, like downloads.

There are three main ways in which tasks can be created:

- creating it from a function,
- from a processing algorithm,
- or by extending `QgsTask`

In this tutorial, we will only cover the latter way. So let's start with a basic plugin idea: we would like to create a small plugin that lets the user download elevation tiles from 

This means 


