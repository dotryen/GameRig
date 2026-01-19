import bpy

from rigify.rigs.spines.basic_spine import Rig as basic_spine
from rigify.rigs.spines.basic_spine import create_sample as orig_create_sample
from .spine_rigs import BaseSpineRig


class Rig(BaseSpineRig, basic_spine):
    """
    Spine rig with fixed pivot, hip/chest controls and tweaks.
    """
    
    def rig_mch_control_bones(self):
        mch = self.bones.mch
        # do nothing...
        # self.make_constraint(mch.pivot, 'COPY_TRANSFORMS', self.fk_result.hips[-1], influence=0.5)


def create_sample(obj):
    """ Create a sample metarig for this rig type.
    """
    bones = orig_create_sample(obj)

    pbone = obj.pose.bones[bones['spine']]
    pbone.rigify_type = 'game.spines.basic_spine'

    return bones