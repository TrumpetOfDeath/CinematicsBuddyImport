
This Blender add-on allows the importing of animation data exported from 
[Cinematics Buddy Beta](https://bakkesplugins.com/plugins/view/95).

## Installation

You need to install four things (five, if you plan to export to After effects):

##### 1. Cinematics Buddy BETA
- Download [here](https://bakkesplugins.com/plugins/view/95).

##### 2. Blender  
You have two options for this:

- Install from [Steam](https://store.steampowered.com/app/365670/Blender/) 
(automatically updates when new versions are released).
    
- Directly from the [Blender site](https://www.blender.org/).

##### 3. Template

The importer needs the FBX objects that come with Cinematics Buddy Beta. For convenience you can
use this template (which already contains the object data).

- Download the template [here](https://github.com/TrumpetOfDeath/CinematicsBuddyImport/releases/download/v0.1.0/Cinematics_Buddy.zip) 
(don't unzip it!).

- Open Blender and click the `App` menu (the little Blender icon to the left of the `File` menu) 
then click `Install Application Template...`

- Select `Cinematics_Buddy.zip` and click the install button.

##### 4. Importer

- Download the importer [here](https://github.com/TrumpetOfDeath/CinematicsBuddyImport/releases/download/v0.1.0/io_import_cinematics_buddy.zip) 
(don't unzip it!).

- Go to `Edit > Preferences > Add-ons` then click `Install...`

- Select `io_import_cinematics_buddy.zip` then click the install button. 

- Enable the add-on by clicking the check box next to 
`Import-Export: Import: Cinematics Buddy Data (.txt)`
    
Once everything is installed you can safely move/delete the downloaded zip files.

---

**Tip:** When recording the Cinematics Buddy frames, try not to go to above 70 fps. Setting Rocket League's fps too high 
will produce a ton of Blender subframes which can cause jitters during playback.

**Tip:** For best results, record the Cinematics Buddy frames at the same time you record the actual game play.

**Tip:** You can read up on the dollycam docs [here](https://docs.google.com/document/d/18MUmF7qsFZQdKZQOJvlWqzIxgGMyDm58uy9ivAnzFk4/edit)
 and [here](https://docs.google.com/spreadsheets/d/1YyTT8HzlDoLAaAPntU9iz2iQ9DaJiVYEMgpBe9eHdBU/edit#gid=0). 
 Any questions you may have about it can be asked in the Bakkesmod [discord](https://t.co/4GKsbJlAcH?amp=1).
 

## Importing into Blender
    
##### 1. Create a new project by going to `File > New > Cinematics Buddy`

##### 2. Import the frame data:
- `File > Import > Cinematics Buddy Animation (.txt)`

- Select your animation export file (`bakkesmod\data\CinematicsBuddy\AnimationExports\your-file-name.txt`).

- In the panel on the right, enter the full path to your campath/snapshot 
file (this is optional but highly recommended as it improves framerate consistency).

- Select the speed your replay was recorded with.

- Select the fps rate you plan to use in Blender/After Effects (60 fps is recommended).

- Click the import button.

Import may take several minutes (you can see its progress in the console: Window > Toggle System Console).

To view the animation, switch to Camera view (by either pressing 0 on the numpad or clicking the camera icon
 in the viewport) and then press play.

## Exporting to After Effects

I've created a custom version of the AE exporter which adds the ability to center anchor points and 
apply custom scaling.
**Note:** If you've installed the default version of the After Effects exporter 
it will be overwritten by this one.

-  Right-click [here](https://raw.githubusercontent.com/TrumpetOfDeath/blender-addons-contrib/master/io_export_after_effects.py) 
and choose `Save Link As...` and save it somewhere memorable.

- In Blender go to `Edit > Preferences > Add-ons` then click `Install...`

- Select `io_export_after_effects.py` then click the install button. 

- Enable the add-on by clicking the check box next to 
`Import-Export: Export: Adobe After Effects (.jsx)` 

- To export, select all the Blender objects by pressing `A`

- Go to `File > Export > Adobe After Effects (.jsx)`

- Type in a file name and press the export button.

- In After Effects, go to `File > Scripts > Run Script File...` and select the .jsx file you just created. 
A new composition will be created that contains the camera and null object data.
---
Known issues:

- When a car is demo'd, it is placed in the center of the field. You'll need to manually hide it.
- Although the campath/snapshot file improves framerate consistency it isn't always perfect! Some 
adjustment may still be necessary.

 




