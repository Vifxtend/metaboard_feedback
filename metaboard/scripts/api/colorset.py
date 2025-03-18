import maya.api.OpenMaya as om
from typing import Union



def isEmpty(dagPath:om.MDagPath) -> Union[bool, None]:
    '''return True if given object has no color sets, otherwise return False'''

    if not isinstance(dagPath, om.MDagPath):
        return None
    
    MFnMesh = om.MFnMesh(dagPath)

    if MFnMesh.numColorSets == 0:
        return True
    

    return False




def exists(colorset:str, dagPath:om.MDagPath) -> Union[bool, None]:
    '''return True if given color set exist for given object, otherwise return False'''

    if not isinstance(dagPath, om.MDagPath):
        return None
    

    if isEmpty(dagPath):
        return False
    

    MFnMesh = om.MFnMesh(dagPath)

    sets = MFnMesh.getColorSetNames()

    if colorset in sets:
        return True
    

    return False




def create(name:str, dagPath:om.MDagPath) -> Union[str, bool]:
    '''creates new colorset for given object'''

    if not isinstance(dagPath, om.MDagPath):
        return False

    MFnMesh = om.MFnMesh(dagPath)
    
    colorset = MFnMesh.createColorSet(name, False)

    return colorset




def remove_all(dagPath:om.MDagPath):
    '''removes all colorsets for given object'''
    
    if not isinstance(dagPath, om.MDagPath):
        return False

    if isEmpty(dagPath):
        return False


    MFnMesh = om.MFnMesh(dagPath)
   
    for set in MFnMesh.getColorSetNames():
        MFnMesh.deleteColorSet(set)




def update(colorset:str, dagPath:om.MDagPath):
    '''update given colorset display in viewport'''

    if not isinstance(dagPath, om.MDagPath):
        return False
    
    if isEmpty(dagPath):
        return False
    
    if not exists(colorset, dagPath):
        return False
    

    MFnMesh = om.MFnMesh(dagPath)
    MFnMesh.setCurrentColorSetName(colorset)




def color_fill(colorset:str, dagPath:om.MDagPath, color:tuple):
    '''fill all vertices in colorset with given color'''
    

    if not isinstance(dagPath, om.MDagPath):
        return False
    
    if isEmpty(dagPath):
        return False
    
    if not exists(colorset, dagPath):
        return False
    

    #-----------------------------------
    unit_color = list()

    for i in range(0, 3):
        if color[i] > 1:
            unit_value = color[i] / 255

            unit_color.append(unit_value)

        elif color[i] < 0:
            unit_color.append(0)

        else:
            unit_color.append(color[i])
    #-----------------------------------


    MFnMesh = om.MFnMesh(dagPath)
    vtx_size = MFnMesh.numVertices
    vtxArray = om.MIntArray()

    MColor = om.MColor(unit_color)
    MColorArray = om.MColorArray()
    
    for i in range(0, vtx_size):
        MColorArray.append(MColor)
        vtxArray.append(i)


    MFnMesh.setVertexColors(MColorArray, vtxArray)
    #update_colorset(colorset, dagPath)


    
