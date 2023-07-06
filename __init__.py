# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "SdfBaker",
    "description": "form sdf to ao",
    "author": "Msv",
    "version": (0, 1),
    "blender": (3, 00, 0),
    "category": "Object",
}


# if "bpy" in locals():
#     import importlib
#     importlib.reload(operators.BakeOps)
#     importlib.reload(operators.ViewOps)
#     importlib.reload(operators.test)
#     importlib.reload(Panels.Panel)
#     print("reloaded")
# else:
#     import bpy # type: ignore
#     from .operators import BakeOps 
#     from .operators import ViewOps 
#     from .operators import test
#     from .Panels import Panel
#     print("imported")
if "bpy" in locals():
        import importlib
        importlib.reload(operators.MyOps)
        importlib.reload(Panels.Panel)
        print("reloaded")
else:
        import bpy # type: ignore
        from .operators import MyOps
        from .Panels import Panel
        print("imported")

def register():
        bpy.utils.register_class(Panel.Msv_Panel_PT_sdfBaker)
        bpy.utils.register_class(MyOps.testClass)
        bpy.utils.register_class(MyOps.BakeSDFao_OT_operators)
        bpy.utils.register_class(MyOps.BakeNormal_OT_operators)
        bpy.utils.register_class(MyOps.BakeSDFao_OT_tomap_operators)
        print("--")
        print("register suc_sdf")
        print("--")
def unregister():
        bpy.utils.unregister_class(Panel.Msv_Panel_PT_sdfBaker)
        bpy.utils.unregister_class(MyOps.testClass)
        bpy.utils.unregister_class(MyOps.BakeSDFao_OT_operators)
        bpy.utils.unregister_class(MyOps.BakeNormal_OT_operators)
        bpy.utils.unregister_class(MyOps.BakeSDFao_OT_tomap_operators)
        print("--")
        print("unregister suc_sdf")
        print("--")

if __name__ == "__main__":
    register()
