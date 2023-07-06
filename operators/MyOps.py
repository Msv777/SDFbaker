import bpy # type: ignore
from ..operators import UV_Triangle_Pixel_Fill as uFill
import math
from mathutils import Vector # type: ignore
from mathutils.interpolate import poly_3d_calc # type: ignore

def debugFunc():
    print("debug success")
    print("changed success")
class testClass(bpy.types.Operator):
    bl_idname = "testclass.testidname"
    bl_label = "testFunc_msv"
    bl_description = "Align object origin to the bottom of its bounding box"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.context.mode != 'OBJECT':
            self.report({"WARNING"}, "msv:Please switch to ObjectMode")
            return {"CANCELLED"}
        else:
            debugFunc()
        return {"FINISHED"}

def new_GeometryNodes_group():
    ''' Create a new empty node group that can be used in a GeometryNodes modifier.
    '''
    node_group = bpy.data.node_groups.new('GeometryNodes_VMV', 'GeometryNodeTree')
    inNode = node_group.nodes.new('NodeGroupInput')
    ##inNode.outputs.new('NodeSocketGeometry', 'Mesh')
    #Extrude Mesh
    ExtrNode = node_group.nodes.new('GeometryNodeExtrudeMesh')
    ExtrNode.name = "VMV_ExtrudeNode"
    ExtrNode.inputs['Offset Scale'].default_value = 0.5
    ExtrNode.inputs['Individual'].default_value = False
    node_group.links.new(inNode.outputs[0], ExtrNode.inputs['Mesh'])
    
    M2Vnode = node_group.nodes.new('GeometryNodeMeshToVolume')
    M2Vnode.inputs['Voxel Amount'].default_value = 32 #Voxel Amount
    node_group.links.new(ExtrNode.outputs["Mesh"], M2Vnode.inputs['Mesh'])
    
    V2Mnode = node_group.nodes.new('GeometryNodeVolumeToMesh')
    node_group.links.new(M2Vnode.outputs['Volume'], V2Mnode.inputs['Volume'])
    
    outNode = node_group.nodes.new('NodeGroupOutput')
    #outNode.inputs.new('NodeSocketGeometry', 'Mesh')
    node_group.links.new(V2Mnode.outputs['Mesh'], outNode.inputs[0])
    
    #inNode.location = Vector((0, 0))
    #outNode.location = Vector((3*outNode.width, 0))
    return node_group

def GetVMVGeoNodeGroup():
    VMVnodegroup = bpy.data.node_groups.get('GeometryNodes_VMV')
    if VMVnodegroup:
        return VMVnodegroup
    else:
        return new_GeometryNodes_group()
    
def bakeNormal_genWrapmesh():
    obj_original = bpy.context.view_layer.objects.active
    bpy.ops.object.duplicate(linked=False)
    obj_mod = bpy.context.active_object
    obj_mod.select_set(True)
    obj_mod.name = obj_original.name+"_WrapMesh"


# 添加Solidify修饰器以处理开放面
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    mod_solidify = obj_mod.modifiers[-1]#取修改器末尾
    mod_solidify.name = 'VMVPre_Solidify'

    bpy.ops.object.modifier_add(type='NODES')
    if obj_mod.modifiers[-1].node_group:
        node_group = obj_mod.modifiers[-1].node_group    
    else:
        node_group = GetVMVGeoNodeGroup()
        obj_mod.modifiers[-1].node_group = node_group
        obj_mod.modifiers[-1].name = "VMV_GeoNode"
    
    #Add Smooth modifier &
    bpy.ops.object.modifier_add(type='SMOOTH')
    mod_smooth = obj_mod.modifiers[-1]
    mod_smooth.name = 'VMVPost_Smooth'
    mod_smooth.iterations = 25
    
    #Deselected ALL  then  Select Original mesh
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = obj_original
    obj_original.select_set(True)
    return obj_mod,node_group.nodes["VMV_ExtrudeNode"]
   
def dataTransfer():
    #找到这对物体(保证obj_original.select_set(True)!)
    obj_original = bpy.context.view_layer.objects.active
    WrapMeshName = obj_original.name+"_WrapMesh"
    try:
        obj_mod = bpy.data.objects[WrapMeshName]
    except:
        raise TypeError("Active does not have a wrapmesh!!")
     #Add Data transfer modifier 
    obj_original.data.use_auto_smooth = True
    bpy.ops.object.modifier_add(type='DATA_TRANSFER')
    mod_datatrans = obj_original.modifiers[-1]
    mod_datatrans.name = 'Post_datatrans'
    mod_datatrans.use_loop_data = True
    mod_datatrans.data_types_loops = {'CUSTOM_NORMAL'}
    mod_datatrans.loop_mapping = 'POLYINTERP_NEAREST'
    mod_datatrans.object = obj_mod


    #Hide modified mesh
    # obj_mod.hide_viewport = True
    #下面是隐藏当前视图层
    obj_mod.hide_set(True)

def clearWrapmesh001():
    WrapMesh1Name = bpy.context.view_layer.objects.active.name+"_WrapMesh.001"
    obj_warpmesh1 = None
    try:
        obj_warpmesh1 = bpy.data.objects[WrapMesh1Name]
    except KeyError as e:
        print(e)
    finally:   
        if obj_warpmesh1:
            bpy.data.objects.remove(obj_warpmesh1, do_unlink=True)   
class BakeNormal_OT_operators(bpy.types.Operator):
    bl_idname = "bakeops.bakenormal"
    bl_label = "SDFbake_BakeNormal"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj_original = bpy.context.view_layer.objects.active
        selected_objects = bpy.context.selected_objects
        if bpy.context.mode != 'OBJECT':
            self.report({"WARNING"}, "msv:Please switch to ObjectMode")
            return {"CANCELLED"}
        if not obj_original or not selected_objects:
            self.report({"WARNING"}, "Nothing Active!!")
            return {"CANCELLED"}
        else:
            self.extrudeNode.inputs['Offset Scale'].default_value = self.value 
        return {'RUNNING_MODAL'}
        return {'FINISHED'}
        return {'RUNNING_MODAL'}
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            self.value = (event.mouse_x-self.init_mouse_pos_x)/400*self.init_value
            self.execute(context)
        elif event.type == 'LEFTMOUSE':  # Confirm
            print("modal")
            clearWrapmesh001()
            dataTransfer()
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            self.value = self.init_value
            bpy.ops.ed.undo_push(message="push_normal_undoevent_for_next_undo")#bugfixed
            bpy.ops.ed.undo()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        #move mouse to center for better move
        region = context.region
        cx = region.width // 2
        cy = region.height // 2
        context.window.cursor_warp(cx, cy)

        self.init_value = 0.5
        self.init_mouse_pos_x = cx
        self.value = 0.5
        print("invoke")
        self.wrapMesh, self.extrudeNode = bakeNormal_genWrapmesh()
        self.extrudeNode.inputs['Offset Scale'].default_value = self.value
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}      

def getRayCastDirections():
    #Using an IsoSphere vertex to get the raycast directions for each point
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, enter_editmode=False, location=(0, 0, 0))
    Sphere = bpy.context.object
    Sphere.name = "RaycastSphere"
    
    raycastDirs = [vert.co for vert in Sphere.data.vertices]
    #Vector.normalize()
    #we are going to use the verts.co as raycast direction for 360 coverage
    bpy.data.objects.remove(Sphere, do_unlink=True)
    return raycastDirs
    #RCDirs = getRayCastDirections()
    
def raycastAllDirection(obj, vetPos, rcDirs, rcLength):
    # Cast  rays
    ray_origin = vetPos
    valueSignDist = 99999999
    for dir in rcDirs:
        success, location, normal, poly_index = obj.ray_cast(ray_origin, dir, distance = rcLength)
        if(success):
            value = (location-vetPos).length
            value = math.copysign(value,-Vector.dot(dir, normal))
            if(abs(value)<abs(valueSignDist)):
                valueSignDist = value
    return valueSignDist

def saveSDasVertexColor(obj, signDists, wm):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mesh = obj.data
    bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
    for vertindex in range(len(signDists)):
        for polygon in mesh.polygons:
            for i, index in enumerate(polygon.vertices):
                if vertindex == index:
                    loop_index = polygon.loop_indices[i]
                    r = signDists[vertindex]
                    mesh.vertex_colors.active.data[loop_index].color = [r,r,r,1.0]
        wm.progress_update(int((vertindex/len(signDists)) * 45) + 55)
    bpy.ops.object.mode_set(mode = 'OBJECT')

def BakeAOUsingWrapMesh():
    context = bpy.context
    wm = bpy.context.window_manager
    wm.progress_begin(0, 100)

    obj_original = bpy.context.view_layer.objects.active
    # make sure in object mode
    bpy.ops.object.mode_set(mode = 'OBJECT')

    if not obj_original:
        print("Nothing Active!!")

    #Select Target mesh
    obj_original.select_set(True)

    WrapMeshName = obj_original.name+"_WrapMesh"
    try:
        obj_warpmesh = bpy.data.objects[WrapMeshName]
    except:
        obj_warpmesh, node = bakeNormal_genWrapmesh()

    #get all vertex position
    vetPoss = [vert.co for vert in obj_original.data.vertices]

    #get raycast directions for each vert
    rcDirs = getRayCastDirections()

    #raycastlength
    rcLength = max(max(obj_warpmesh.dimensions.x, obj_warpmesh.dimensions.y),obj_warpmesh.dimensions.z)
    
    #depsgraph = context.evaluated_depsgraph_get()
    #depsgraph.update()  # just in case
    #obj = obj_warpmesh.evaluated_get(depsgraph)
    obj_warpmesh.hide_viewport = False

    #get Sign distance for All vert using raycast(percent 0%~45%)
    signDist = []
    for i in range(len(vetPoss)):
        signDist.append(raycastAllDirection(obj_warpmesh, vetPoss[i], rcDirs, rcLength))
        wm.progress_update(int(i/len(vetPoss) * 45))

    #normalize SDF value to 0~1 (percent 45%~55%)
    obj_warpmesh.hide_viewport = True
    maxDist = max(signDist)
    minDist = min(signDist)
    for i in range(len(vetPoss)):
        signDist[i] = (signDist[i]-minDist)/(maxDist-minDist)
        signDist[i] = signDist[i]*signDist[i]
    wm.progress_update(55)
    
    #Save SDF AO to Vertex Color(percent 55%~100%)
    saveSDasVertexColor(obj_original, signDist, wm)



class BakeSDFao_OT_operators(bpy.types.Operator):
    bl_idname = "bakeops.bakesdfao"
    bl_label = "SDFbake_BakeSDFao"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj_original = bpy.context.view_layer.objects.active
        selected_objects = bpy.context.selected_objects
        if bpy.context.mode != 'OBJECT':
            self.report({"WARNING"}, "msv:Please switch to ObjectMode")
            return {"CANCELLED"}
        if not obj_original or not selected_objects:
            self.report({"WARNING"}, "Nothing Active!!")
            return {"CANCELLED"}
        else:
            self.extrudeNode.inputs['Offset Scale'].default_value = self.value 
        return {'RUNNING_MODAL'}
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            self.value = (event.mouse_x-self.init_mouse_pos_x)/400*self.init_value
            self.execute(context)
        elif event.type == 'LEFTMOUSE':  # Confirm
            print("modal")
            clearWrapmesh001()
            BakeAOUsingWrapMesh() 
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            self.value = self.init_value
            bpy.ops.ed.undo_push(message="push_normal_undoevent_for_next_undo")#bugfixed
            bpy.ops.ed.undo()
            return {'CANCELLED'} 
        return {'RUNNING_MODAL'}
    def invoke(self, context, event):
        #move mouse to center for better move
        region = context.region
        cx = region.width // 2
        cy = region.height // 2
        context.window.cursor_warp(cx, cy)

        self.init_value = 0.5
        self.init_mouse_pos_x = cx
        self.value = 0.5
        print("invoke")
        self.wrapMesh, self.extrudeNode = bakeNormal_genWrapmesh()
        self.extrudeNode.inputs['Offset Scale'].default_value = self.value
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}      
    
def ExportVertexColorAs_img():
    img_size = 1024
    uFill.pointColorSaveToTex(img_size)
class BakeSDFao_OT_tomap_operators(bpy.types.Operator):
    bl_idname = "bakeops.vertexcolortomap"
    bl_label = "SDFbake_VertexColorToMap"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj_original = bpy.context.view_layer.objects.active
        selected_objects = bpy.context.selected_objects
        if bpy.context.mode != 'OBJECT':
            self.report({"WARNING"}, "msv:Please switch to ObjectMode")
            return {"CANCELLED"}
        if not obj_original or not selected_objects:
            self.report({"WARNING"}, "Nothing Active!!")
            return {"CANCELLED"}
        else:
            ExportVertexColorAs_img()
        return {"FINISHED"}

