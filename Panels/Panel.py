import bpy  # type: ignore

class Msv_Panel_PT_sdfBaker(bpy.types.Panel):

    bl_label = 'SDFbaker'
    bl_idname = 'msvpanel_sdfbaker'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    

    def draw(self, context):
        layout = self.layout
        split = layout.split(factor=0.5, align=True)  # 创建水平分割布局，将窗口分为左右两部分
        split.operator("bakeops.bakesdfao", text="BakeAO")  # 左边的按钮
        split.operator("bakeops.bakenormal", text="Convert Normal")  # 右边的按钮
        row = layout.row(align=False)
        split2 = row.split(factor=1, align=True)  # 创建水平分割布局，将窗口分为左右两部分
        split2.operator("bakeops.vertexcolortomap", text="Output SDFaomap")  # 左边的按钮
        # split2.operator("bakeops.bakenormal", text="Convert Normal")  # 右边的按钮
        

