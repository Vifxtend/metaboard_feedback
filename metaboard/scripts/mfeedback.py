import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

import maya.cmds as cmd
import maya.mel as mel


import api.colorset as ColorSet
import api.utils as Utils





def get_controls() -> om.MDagPathArray:
    '''return array of faceboard nodes'''


    MSelection = om.MSelectionList() #construct empty MSelectionList

    #try to get CTRL_expressions node:
    try:
        MSelection.add('CTRL_expressions')
    
    except:
        try:
            MSelection.add('*:CTRL_expressions')

        except: pass


    if MSelection.length() == 0:
        cmd.warning('[get_controls] Failed to find "CTRL_expressions" node.')

        return False #didnt find CTRL_expressions, return 0
        
    
    
    
    MDagPath = MSelection.getDagPath(0) #dagPath to CTRL_expressions
    MObject = MSelection.getDependNode(0) #MObject to CTRL_expressions
    fullPath = MDagPath.fullPathName() #fullpath to CTRL_expressions
    nodeName = Utils.from_fullPath(fullPath) #CTRL_expressions node name (namespace included)

    facial_expressions = cmd.listAttr(fullPath, k=1, v=1) #get all expression attributes from CTRL_expressions
    controls_buffer = list() #empty buffer to store faceboard transform nodes



    kRigLogic = Utils.isRigLogic(MObject)

    if kRigLogic == True:
    
        #iterate over CTRL_expressions attributes to get driver control for each expression attribute:
        for expression in facial_expressions:
            '''
            @note:
                CONTROL -> animCurve -> CTRL_expressions.<expression> -> RigLogic

                we just doing it backward:
                    CONTROL <- animCurve <- CTRL_expressions.<expression>

            '''
            animCurve = cmd.listConnections(f'{fullPath}.{expression}', et=1, t='animCurveUU') #get animCurve plug that connected in expression attribute

            if animCurve:
                control = cmd.listConnections(f'{animCurve[0]}.input', scn=1) #CONTROL, return control name
                
                if (not control[0] in controls_buffer
                    and control[0] != nodeName):

                    '''
                    @control[0] != nodeName:
                        listConnections may return "CTRL_expressions" in some cases, making sure to not append it to controls buffer
                    '''
                        
                    controls_buffer.append(control[0]) #get control and append it to buffer
                
                

        '''
        @note:
                    to get eye controls we have to get at least one expression attribute 
            that corresponds to one of the eyes and iterate though all upstream nodes from this plug

            
            because eyes has more complex setup than other controls and it looks something like this:

            CTRL_eye -> animCurve -> blendWeight -> locator -> orientConstraint -> locator -> SDK -> SDK -> CTRL_expressions -> RigLogic

        '''
        eyelook_attrs = ['eyeLookLeftR', 'eyeLookLeftL'] #define CTRL_expressions look attributes
        drivers = ['CTRL_C_eye', 'CTRL_L_eye', 'CTRL_R_eye'] #define controls that drives eyelook attributes


        MObject = MSelection.getDependNode(0) #get CTRL_expressions as MObject
        MFnDependencyNode = om.MFnDependencyNode(MObject)

        for attr in eyelook_attrs:

            try:
                plug = MFnDependencyNode.findPlug(attr, False) #get CTRL_expressions look attribute
            
            except:
                continue



            iter = om.MItDependencyGraph(plug, om.MFn.kInvalid, om.MItDependencyGraph.kUpstream) #construct upstream iterator

            #iterate upstream the plug until we find needed control:
            while not iter.isDone():

                iter_MObj = iter.currentNode()
                iter_MFnDep = om.MFnDependencyNode(iter_MObj)

                nodeName = iter_MFnDep.name()

                if any(d in nodeName for d in drivers):

                    if not nodeName in controls_buffer:
                        controls_buffer.append(nodeName)

                iter.next()




        #convert transform nodes to MDagPath objects and append it to MDagPathArray:
        controls_dagPaths = om.MDagPathArray()
        
        for control in controls_buffer:
            try:
                MSelection = om.MGlobal.getSelectionListByName(control)
                MDagPath = MSelection.getDagPath(0)
                shape = MDagPath.extendToShape()

                if cmd.objectType(shape) == 'mesh':
                    controls_dagPaths.append(MDagPath)

            except:
                continue
            


        return controls_dagPaths
    



    elif kRigLogic == False:
        
        MSelection = om.MSelectionList()
        controls = ['CTRL_C_*', 'CTRL_L_*', 'CTRL_R_*']
        

        for c in controls:
            try:
                MSelection.add(c)

            except:
                MSelection.add(f'*:{c}')

        
        if MSelection.length() == 0:
            return False
        
        
        iter = om.MItSelectionList(MSelection)
        controls_dagPaths = om.MDagPathArray()


        while not iter.isDone():

            iter_MObj = iter.getDependNode()
            iter_MFnDep = om.MFnDependencyNode(iter_MObj)

            if iter_MFnDep.typeName == 'mesh':

                MDagPath = iter.getDagPath()
                controls_dagPaths.append(MDagPath)

                iter.next()


            iter.next()


        return controls_dagPaths
        




def create_feedSets(dagPaths:om.MDagPathArray):
    '''create colorsets for controls to draw interactive feedback'''

    kColorsetFeedback = 'feedback_set'
    
    for obj in dagPaths:
        ColorSet.remove_all(obj)
        

        fullPath = Utils.from_MDagPath(obj)
        shapeNode = om.MDagPath(obj).extendToShape()
        nodeName = Utils.from_fullPath(fullPath)

        ColorSet.create(kColorsetFeedback, obj)
        ColorSet.color_fill(kColorsetFeedback, obj, color=(1, 1, 0))

        try:
            cmd.setAttr(f'{shapeNode}.displayColors', 1)

        except:
            cmd.warning(f'[create_feedSets] Something went wrong with node -> "{nodeName}" on set ".displayColors" attribute.')





def setup_feedback(dagPath:om.MDagPath, fdbset:str, fdtype:str):
    '''setup feedback for given control'''

    control = Utils.from_MDagPath(dagPath)
    control_fullPath = dagPath.fullPathName()
    control_shape = dagPath.extendToShape()
    control_name = Utils.from_MDagPath(dagPath)
    

    ctransform = Utils.from_fullPath(control_name)
    ctransform_blast = ctransform.split('_', maxsplit=1)
    blast_size = len(ctransform_blast)

    control_basename = ctransform_blast[blast_size - 1]


    if not cmd.objExists(control):
        cmd.warning(f'[setup_feedback] Cant find node with given name -> "{control_name}". ')
       
        return False
    

    if not ColorSet.exists(fdbset, dagPath):
        cmd.warning(f'[setup_feedback] Cant find colorset with name -> "{fdbset}". ')

        return False
    


    colormod_node = cmd.polyColorMod(control_fullPath, bcn=fdbset)[0]
    cmd.addAttr(colormod_node, ln='feedback', at='bool', k=0, h=0, dv=1)
    

    try:
        mel.eval(f"catchQuiet(`python(\"cmd.connectAttr(f'{colormod_node}.output', f'{control_shape}.inMesh', f=1)\")`)")
        mel.eval(f"catchQuiet(`python(\"cmd.setAttr(f'{control_shape}.ihi', 0)\")`)")
        
    
    except:
        #i dont know
        try:
            cmd.connectAttr(f'{colormod_node}.output', f'{control_shape}.inMesh', f=1)
            cmd.setAttr(f'{control_shape}.ihi', 0)

        except: pass

    

    kMultiplyAttr = 'feedback_Multiply'
    fdb_mult = cmd.attributeQuery(kMultiplyAttr, n=control, ex=1)
    
    if not fdb_mult:
        try:
            cmd.addAttr(control, ln=kMultiplyAttr, at='float', k=0, h=0, dv=1, hsn=1, min=1)

        except: pass
    
    else:
        cmd.setAttr(f'{control}.{kMultiplyAttr}', 1)

    

#---|
    fourdir_exp = f"""
    float $avg = (abs({control}.translateX) + abs({control}.translateY));

    {colormod_node}.huev = max(-60, $avg * (-60) * 0.9 * {control}.{kMultiplyAttr});
    """

#--

    onedir_exp = f"""
    {colormod_node}.huev = max(-60, abs({control}.translateY) * (-60) * 1.2 * {control}.{kMultiplyAttr});
    """
#---|


    if fdtype == '2way':
    #if control has only one axis:

        exp_node = cmd.expression(n=f'{control_basename}_CExpression', s=onedir_exp, o=colormod_node, ae=1, uc='all')
        cmd.addAttr(exp_node, ln='feedback', at='bool', k=0, h=0, dv=1)


    #if control has two free axis:
    elif fdtype == '4way':
   
        exp_node = cmd.expression(n=f'{control_basename}_CExpression',s=fourdir_exp, o=colormod_node, ae=1, uc='all')
        cmd.addAttr(exp_node, ln='feedback', at='bool', k=0, h=0, dv=1)

    else:
        cmd.delete(colormod_node)
        return False
    


    cm_buffer = om.MSelectionList()

    try:
        cm_buffer.add(colormod_node)
        mod = om.MDagModifier()
        mod.renameNode(cm_buffer.getDependNode(0), f'{control_basename}_CM')
        mod.doIt()

    except: pass
    





def remove():
    node_types = ['polyColorMod', 'deleteColorSet', 'polyColorPerVertex', 'createColorSet']


    for node in cmd.ls(typ=node_types):
    
        if (cmd.objectType(node) == 'polyColorMod'):

            is_fdb = cmd.attributeQuery('feedback', n=node, ex=1)

            if not is_fdb:
                continue

            
            try:
                cmd.delete(node)
                
            except: pass
        

        else:
            try:
                cmd.delete(node)

            except: pass
        

            

def init():

    remove()

    panels = cmd.getPanel(typ='modelPanel')

    for p in panels:
        cmd.modelEditor(p, e=1, udm=0)



    controls = get_controls() #get faceboard controls

    if not controls:
        cmd.warning(f'[feedback_init] Failed to find any faceboard control.')

        return False #didnt find any control, return 0
    


    

    
    MSelection = om.MSelectionList()

    try:
        MSelection.add('CTRL_expressions')

    except:
        MSelection.add('*:CTRL_expressions')




    kColorsetFeedback = 'feedback_set' #define colorset for feedback
    kRigLogic = Utils.isRigLogic(MSelection.getDependNode(0))
   
    if kRigLogic == True:
        create_feedSets(controls) #create feedback colorsets for controls


        for c in controls:

            ctransform = Utils.from_MDagPath(c)
            control_dirs = cmd.listAttr(ctransform, k=1, v=1) #get control free axis

            if len(control_dirs) == 1:
                setup_feedback(c, kColorsetFeedback, fdtype='2way')

            elif len(control_dirs) == 2:
                setup_feedback(c, kColorsetFeedback, fdtype='4way')

            else:
                continue



    elif kRigLogic == False:
        create_feedSets(controls) #create feedback colorsets for controls


        for c in controls:
            ctransform = Utils.from_MDagPath(c)
            MObject = Utils.to_MObject(ctransform)

            animatedPlugs = oma.MAnimUtil.findAnimatedPlugs(MObject, checkParent=False)

            if animatedPlugs:
                if len(animatedPlugs) == 1:
                    setup_feedback(c, kColorsetFeedback, fdtype='2way')

                elif len(animatedPlugs) > 1:
                    setup_feedback(c, kColorsetFeedback, fdtype='4way')

                








