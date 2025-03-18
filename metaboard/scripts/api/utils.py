import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

import maya.cmds as cmd

from typing import Union


def isRigLogic(CTRL_expressions:om.MObject) -> Union[bool, None]:
    '''simple way to check if CTRL_expressions used to drive RigLogic'''

    if not isinstance(CTRL_expressions, om.MObject):
        return None
    

    kRigLogic = bool()

    MObject = om.MObject(CTRL_expressions)
    MFnDependencyNode = om.MFnDependencyNode(MObject)
    
    MSelection = om.MSelectionList()
    
    try:
        MSelection.add(MFnDependencyNode.name())

    except:
        return None


    MDagPath = MSelection.getDagPath(0)
    fullPath = MDagPath.fullPathName()


    facial_expressions = cmd.listAttr(fullPath, k=1, v=1)
    sdk_counter = int()

    for attr in facial_expressions:

        plug = MFnDependencyNode.findPlug(attr, False)

        sdkCurve = oma.MAnimUtil.findSetDrivenKeyAnimation(plug)
        sdk_counter += len(sdkCurve[0])


    if sdk_counter == 0:
        kRigLogic = False

    else:
        kRigLogic = True


    return kRigLogic




def to_MDagPath(node:str) -> om.MDagPath:
    '''return MDagPath for given node if its mesh type of object'''

    if not cmd.objExists(node):
        return False
    
    
    MSelection = om.MGlobal.getSelectionListByName(node)

    MObject = MSelection.getDependNode(0)
    MFnDependencyNode = om.MFnDependencyNode(MObject)
    
    if not MFnDependencyNode.typeName == 'mesh':
        return None
    

    return MSelection.getDagPath(0)




def to_MObject(node:str) -> om.MObject:
    '''retrun MObject for given node'''

    try:
        MSelection = om.MGlobal.getSelectionListByName(node)

    except:
        return None
    
    MSelection = om.MGlobal.getSelectionListByName(node)
    return MSelection.getDependNode(0)
    



def from_MObject(mobj:om.MObject) -> str:
    '''return object name from MObject'''

    MFnDependencyNode = om.MFnDependencyNode(mobj)
    return MFnDependencyNode.name()




def from_MDagPath(dagPath:om.MDagPath) -> str:
    '''return fullpath name to transform node for given MDagPath object'''

    fullPath = dagPath.fullPathName()
    shapeMObject = dagPath.node()
    shape_name = om.MFnDependencyNode(shapeMObject).name()

    transform = str(fullPath).removesuffix(f'|{shape_name}')

    return transform




def from_fullPath(fullPath:str) -> Union[str, None]:
    '''return last element of fullPath. from "|a|node|pCube1" -> to "pCube1"'''

    blast = fullPath.split('|')

    if not blast:
        return None
    

    return blast[len(blast) - 1]


