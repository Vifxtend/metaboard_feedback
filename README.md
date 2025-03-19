
# Interactive Metahuman Faceboard
https://github.com/user-attachments/assets/b09b5790-1c0d-470a-ae06-fea978a92c73

---
## Description
Smoothly interpolate from YELLOW to RED-color based on control input using MAYA colorsets and expression nodes

![metaboard_init_icon](https://github.com/user-attachments/assets/731be98b-cbcc-43cd-ab4d-0277e94b5637) Display Feedback

![metaboard_default_icon](https://github.com/user-attachments/assets/f45c03a9-7176-4ed6-b28a-642035dcf3a2) Use Default Display


## Features
+ Supports namespaces and references
+ Has no impact on performance
+ Individual attributes to control feedback sensivity (scriptable)

## Requirements
+ Python 3

## Installation
1. Extract archive contents to your `MAYA_MODULE_PATH` folder (usually its `User/Documents/maya/modules`)
2. Run Maya and see new shelf called **"Meta"**

**Note:** To prevent new shelf to create edit `.mod` file with removing `MAYA_SHELF` line.

---
## Examples:
+ To manually call and remove feedback display use ```mfeedback.init()``` and ```mfeedback.remove()``` methods.
+ To change control (transform node) sensivity edit `.feedback_Multiply` attribute (float).

For code snippets look for `example` folder.




