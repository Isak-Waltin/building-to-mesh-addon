bl_info = {
    "name": "Convert Building To Mesh",
    "blender": (3, 2, 0),
    "category": "Object",
    "location": "3D View > Sidebar > Procedural Building Generator",
    "doc_url": "https://docs.google.com/document/d/1wbCt9YCebh9JzLt9eaB1hSANKaGamncC9HwSPx2G6zM/edit#",
}


import bpy


class PrepareForExport(bpy.types.Operator):
    """Apply generated building and fix UV maps"""
    bl_idname = "object.prepare_for_export"
    bl_label = "Convert Building To Mesh"
    bl_options = {'REGISTER','INTERNAL'}

    def execute(self, context):
        ob = context.active_object
        modifier = ob.modifiers.active
        ng = modifier.node_group
        
        for input in ng.inputs:
            if input.name == "Realize all instances":
                inp = input
                break
        else:
            return {'CANCELLED'} #Couldn't find the correct input
        
        modifier[inp.identifier] = 1 #Set realize instances to 1
        bpy.ops.object.convert(target='MESH', merge_customdata=False)
        
        new_uv = ob.data.uv_layers.new()
        attr_uv = ob.data.attributes["UVMap"]
        for i, elem in enumerate(new_uv.data):
            elem.uv = attr_uv.data[i].vector
        ob.data.attributes.remove(attr_uv)
        
        bpy.ops.ed.undo_push(message="Convert to mesh")
        
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        if context.active_object.type == 'MESH' and context.active_object.modifiers:
            act_mod = context.active_object.modifiers.active
            
            if act_mod.type == 'NODES': #Check if correct geo node group is selected
                if act_mod.node_group:
                    ng = act_mod.node_group
                    return any((input.name == "Realize all instances") for input in ng.inputs)    
        return False


class VIEW3D_PT_export(bpy.types.Panel):
    """"""
    bl_label = "Export Preparations"
    bl_idname = "VIEW3D_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Procedural Building Generator'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        
        if not bpy.ops.object.prepare_for_export.poll():
            row.label(text="\"Building from mesh\" modifier not selected", icon='ERROR')
            row = layout.row()
            row.active = False
        row.operator("object.prepare_for_export")
            
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.mode == 'OBJECT'
        

def register():
    bpy.utils.register_class(VIEW3D_PT_export)
    bpy.utils.register_class(PrepareForExport)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_export)
    bpy.utils.unregister_class(PrepareForExport)


if __name__ == "__main__":
    register()
