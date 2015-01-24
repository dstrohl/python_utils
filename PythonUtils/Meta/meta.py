__author__ = 'dstrohl'


# ===============================================================================
# Generic Meta Object
#===============================================================================

class GenericMeta(object):

    def get_meta_attrs(self, parent_obj, skip_list = [], skip_startswith = '_', overwrite = True):
        for attr, value in iter(self.__dict__.items()):
            if not attr.startswith(skip_startswith) and attr not in skip_list:
                if not hasattr(parent_obj,attr) or overwrite:
                    setattr(parent_obj,attr,value)

def get_meta_attrs(meta, parent_obj, skip_list = [], skip_startswith = '_', overwrite = True):
    for attr in dir(meta):
        if not attr.startswith(skip_startswith) and attr not in skip_list:
            if not hasattr(parent_obj,attr) or overwrite:
                tmp_value = getattr(meta,attr)
                setattr(parent_obj,attr,tmp_value)


def get_meta_attrs2(meta, parent_obj, skip_list = [], skip_startswith = '_', overwrite = True):
    for attr, value in iter(meta.__dict__.items()):
        if not attr.startswith(skip_startswith) and attr not in skip_list:
            if not hasattr(parent_obj,attr) or overwrite:
                setattr(parent_obj,attr,value)

