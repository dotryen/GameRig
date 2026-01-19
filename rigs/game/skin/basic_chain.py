import bpy
import math

from .skin_rigs import BaseSkinChainRigWithRotationOption
from rigify.rigs.skin.basic_chain import Rig as basic_chain
from rigify.base_rig import stage

class Rig(BaseSkinChainRigWithRotationOption, basic_chain):
    
    def initialize(self):
        super().initialize()

        self.enable_scale = self.params.enable_scale

    @stage.parent_bones
    def parent_deform_chain(self):
        
        self.set_bone_parent(self.bones.deform[0], self.rig_parent_bone)
        self.parent_bone_chain(self.bones.deform, use_connect=False)

        # This puts the deformation bones into the def hierarchy of its parent rig
        self.clean_def_hierarchy(self.bones.deform[0])

    def rig_deform_bone(self, i, deform, org):
        if self.enable_scale:
            self.make_constraint(deform, 'COPY_TRANSFORMS', org)
        else:
            self.make_constraint(deform, 'COPY_LOCATION', org)
            self.make_constraint(deform, 'COPY_ROTATION', org)

    @classmethod
    def add_parameters(self, params):
        super().add_parameters(params)
        params.enable_scale = bpy.props.BoolProperty(
            name="Scale",
            default=False,
            description="Deformation bones will inherit the scale of their ORG bones. Enable this only if you know what you are doing because scale can break your rig in the game engine"
        )

    @classmethod
    def parameters_ui(self, layout, params):
        super().parameters_ui(layout, params)

        row = layout.row()
        row.prop(params, "enable_scale")


def create_sample(obj):
    from ..basic.copy_chain import create_sample as inner
    obj.pose.bones[inner(obj)["bone.01"]].rigify_type = 'game.skin.basic_chain'
