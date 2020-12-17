#Alan Zheng

import maya.cmds as cmds
import random
import functools


cmds.selectPref(trackSelectionOrder = True)
cmds.grid( toggle=0 )

# create ui to ask for user input
def createUI( pWindowTitle, pApplyCallback ):
    
    windowID = 'myWindowID'
    
    if cmds.window( windowID, exists=True ):
        cmds.deleteUI( windowID )
        
    cmds.window( windowID, title=pWindowTitle, sizeable=False, resizeToFitChildren=True )
    
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1,75), (2,60), (3,60) ], columnOffset=[ (1,'right',3) ] )
    
    cmds.text( label='Hex Number:' )
    
    numField = cmds.intField() 
    
    cmds.separator( h=10, style='none' )
    
    cmds.text( label='Time Range:' )
    
    startTimeField = cmds.intField( value=cmds.playbackOptions( q=True, minTime=True ) )
    endTimeField = cmds.intField( value=cmds.playbackOptions( q=True, maxTime=True ) )
    
    cmds.text( label='Attribute:' )
    
    targetAttributeField = cmds.textField( text='rotateY' )
    
    cmds.separator( h=10, style='none' )
    cmds.separator( h=10, style='none' )
    cmds.separator( h=10, style='none' )
    
    cmds.separator( h=10, style='none' )
    
    cmds.button( label='Apply', command=functools.partial( pApplyCallback, numField, startTimeField, endTimeField, targetAttributeField))
    
    def cancelCallback( *pArgs ):
        if cmds.window( windowID, exists=True ):
            cmds.deleteUI( windowID )
    
    cmds.button( label='Cancel', command=cancelCallback )
    
    cmds.showWindow()

# function for rotation animation
def keyFullRotation( pObjectName, pStartTime, pEndTime, pTargetAttribute):
    cmds.cutKey( pObjectName, time=(pStartTime, pEndTime), attribute=pTargetAttribute)
    cmds.setKeyframe( pObjectName, time=pStartTime, attribute =pTargetAttribute, value=0)
    cmds.setKeyframe( pObjectName, time=pEndTime, attribute=pTargetAttribute, value=360)
    cmds.selectKey( pObjectName, time=(pStartTime, pEndTime), attribute=pTargetAttribute, keyframe=True)
    cmds.keyTangent(inTangentType='linear', outTangentType='linear')

# function for expansion animation
def keyExpansion( pObjectName, pStartTime, pEndTime, pTargetAttribute):
    cmds.cutKey( pObjectName, time=(pStartTime, pEndTime), attribute=pTargetAttribute)
    cmds.setKeyframe( pObjectName, time=pStartTime, attribute =pTargetAttribute, value=100)
    cmds.setKeyframe( pObjectName, time=((pStartTime + pEndTime) / 2), attribute =pTargetAttribute, value=50)
    cmds.setKeyframe( pObjectName, time=pEndTime, attribute=pTargetAttribute, value=100)
    cmds.selectKey( pObjectName, time=(pStartTime, pEndTime), attribute=pTargetAttribute, keyframe=True)
    cmds.keyTangent(inTangentType='linear', outTangentType='linear')

    
    
# after the user presses apply
def applyCallback( pnumField, pStartTimeField, pEndTimeField, pTargetAttributeField, *pArgs ):
    
    n = cmds.intField( pnumField, query=True, value=True)
    
    random.seed (12345)

    # deletes previous hexs, groups, and sphere when rerunning the script
    hexList = cmds.ls("myHex*")
    if len(hexList) > 0:
        cmds.delete(hexList)
        
    sphereList = cmds.ls("mySphere*")
    if len(sphereList) > 0:
        cmds.delete(sphereList)
    
    expansionList = cmds.ls("expansion_locator_grp*")
    if len(expansionList) > 0:
        cmds.delete(expansionList)
        
    hexshieldList = cmds.ls("hexshield*")
    if len(hexshieldList) > 0:
        cmds.delete(hexshieldList)
    
    # create sphere and hex        
    sphereResult = cmds.polySphere( r = 1.15, name = "mySphere#")
    result = cmds.polyCylinder( r = 1.15, h = .15, sx = 6, name = "myHex#")
    cmds.polyBevel( fraction = .5, oaf = 1, af = 1, segments = 1, worldSpace = 1, 
    mergeVertexTolerance = 0.0001, miteringAngle = 180, angleTolerance = 180, ch = 1)   
 
    
    transformName=result[0]
    
    instanceGroupName = cmds.group (empty=True, name = transformName + '_instance_grp#')
    
    
    # create number of hexes based on user input
    for i in range (0, n) :
  
        instanceResult=cmds.instance(transformName, name=transformName + '_instance#')  
        
        cmds.parent (instanceResult, instanceGroupName)
        
        x = random.uniform (-10,10)
        y = random.uniform (0,20)
        z = random.uniform (-10,10)
    
        cmds.move (x, y, z, instanceResult)
        
        xRot = random.uniform (0,360)
        yRot = random.uniform (0,360)
        zRot = random.uniform (0,360)
        
        cmds.rotate (xRot,yRot,zRot, instanceResult)
        
        scaling = random.uniform (0.3, 1.5)
        
        cmds.scale(scaling, scaling, instanceResult)
        
        cmds.aimConstraint(sphereResult[0], instanceResult, aimVector=[0,1,0])
        
        
        # give each hex a random color
        new_shader = cmds.shadingNode('lambert', asShader=True)
        new_sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr(new_shader + '.outColor', new_sg + ".surfaceShader", force=True)
 
        r = random.uniform (0,5)
        g = random.uniform (0,5)
        b = random.uniform (0,5)
        
        
        cmds.setAttr(new_shader+'.color', r,g,b)

        
        cmds.select(instanceResult[0])
        cmds.hyperShade(assign=new_shader)

        
         
    cmds.hide (transformName)
    cmds.xform (instanceGroupName, centerPivots=True)
    
    cmds.move(0, 10, 0, 'mySphere1')

    # create selectionList for expansion attribute
    selectionListObj = []

    objList = cmds.ls('myHex1_instance*')

    for i in range (0, len(objList)):
        if (i%2 == 0):
            selectionListObj.append(objList[i])   
    
    
    # expansion attribute 
    locatorGroupName = cmds.group( empty=True, name='expansion_locator_grp#')
    
    maxExpansion = 100
    
    newAttributeName = 'expansion'
    
    targetName = sphereResult[0] 
        
    if not cmds.objExists( '%s.%s' % ( targetName, newAttributeName )):
        cmds.select(targetName)
        cmds.addAttr( longName=newAttributeName, shortName='exp',
                      attributeType='double', min=0, max=maxExpansion,
                      defaultValue=maxExpansion, keyable=True )
    
    for objectName in selectionListObj:
        
        coords = cmds.getAttr( '%s.translate' % ( objectName ) )[0]
        
        locatorName = cmds.spaceLocator( position=coords, name='%s_loc#' % ( objectName ) )[0]
        
        cmds.xform( locatorName, centerPivots=True )
        
        cmds.parent( locatorName, locatorGroupName )
        
        pointConstraintName = cmds.pointConstraint( [ targetName, locatorName ], objectName, name='%s_pointConstraint#' % ( objectName ) )[0]
        
        cmds.expression( alwaysEvaluate=True, 
                         name='%s_attractWeight' % ( objectName ),
                         object=pointConstraintName,
                         string='%sW0=%s-%s.%s' % ( targetName, maxExpansion, targetName, newAttributeName ) )
        
        cmds.connectAttr( '%s.%s' % ( targetName, newAttributeName ), 
                          '%s.%sW1' % ( pointConstraintName, locatorName ) )
             
    cmds.xform( locatorGroupName, centerPivots=True )         
    
    # groups locator and hex groups together
    cmds.group('myHex1_instance_grp1', 'expansion_locator_grp1', n='hexshield')
    
    # Gets all the attributes from user input
    cmds.select('hexshield')
    selectionList = cmds.ls( selection = True, type = 'transform' )

    startTime = cmds.intField( pStartTimeField, query=True, value=True )
    endTime = cmds.intField( pEndTimeField, query=True, value=True )
    targetAttribute = cmds.textField( pTargetAttributeField, query=True, text=True )
    
    cmds.playbackOptions( minTime=startTime, maxTime=endTime)
    cmds.currentTime(startTime)
    
    # sets up the keyframes for the rotation 
    keyFullRotation( selectionList[0], startTime, endTime, targetAttribute)
        
    keyFullRotation( 'mySphere1', startTime, endTime, targetAttribute)    


    # sets up the keyframes for the expansion animation   
    keyExpansion( targetName, startTime, endTime, 'expansion')
    
    cmds.select('hexshield',d=True)          


    # give surface shader to sphere
    mySurf = cmds.shadingNode('surfaceShader',asShader=True)
    cmds.setAttr(mySurf+'.outColor',1, .6359,0) 
    cmds.setAttr(mySurf+'.outGlowColor',.774, .550522,.160218) 
    cmds.select('mySphere1') 
    cmds.hyperShade( assign=mySurf)
    
    # make camera
    
    # delete old camera when rerunning the script
    cameraList = cmds.ls("camera1*")
    if len(cameraList) > 0:
        cmds.delete(cameraList)
    
    cameraName = cmds.camera()
    cameraShape = cameraName[1]
    
    cmds.setAttr('camera1'+'.translateX',-.094)
    cmds.setAttr('camera1'+'.translateY',9.882)
    cmds.setAttr('camera1'+'.translateZ',60)
    cmds.setAttr('camera1'+'.rotateX',0)
    cmds.setAttr('camera1'+'.rotateX',0)
    cmds.setAttr('camera1'+'.rotateX',0)

    cmds.lookThru( 'camera1' )  
    
    
    # delete old directional light when rerunning the script
    
    dlList = cmds.ls("directionalLight1*")
    if len(dlList) > 0:
        cmds.delete(dlList)
     
    # make directional light  
    light = cmds.directionalLight() 
    cmds.setAttr('directionalLight1'+'.translateX',16.845)
    cmds.setAttr('directionalLight1'+'.translateY',20.178)
    cmds.setAttr('directionalLight1'+'.translateZ',-11.09)
    cmds.setAttr('directionalLight1'+'.rotateX',-24.798)
    cmds.setAttr('directionalLight1'+'.rotateX',135.358)
    cmds.setAttr('directionalLight1'+'.rotateX',0)
    
    # delete old point light when rerunning the script
    plList = cmds.ls("pointLight1*")
    if len(plList) > 0:
        cmds.delete(plList)
     
    # make point light  
    plight = cmds.pointLight() 
    cmds.setAttr('pointLight1'+'.translateY', 10)


createUI('Animation Settings', applyCallback)
    






