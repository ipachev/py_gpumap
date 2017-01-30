from data_model import ClassRepresentation, primitive_map
from util import time_func
from collections import deque

import struct
import pickle

class ListSerializer:
    def __init__(self, class_repr, _list=None, length=None):
        self._list = deque(_list)
        self.class_repr = class_repr
        self.length = len(_list) if _list is not None else length
        self.format = self.get_format(class_repr, self.length)

    def get_format(self, class_repr, length):
        if not isinstance(class_repr, ClassRepresentation):
            format = primitive_map[class_repr]
        else:
            format = class_repr.get_format()
        return format * length

    @staticmethod
    def get_data_items(_list, class_repr):
        if not isinstance(class_repr, ClassRepresentation):
            return _list
        else:
            data_items = []
            for item in _list:
                ListSerializer._extract_inner_data(item, class_repr, data_items)
            return data_items

    @staticmethod
    def _extract_inner_data(item, class_repr, data_items):
        for field, _type in zip(class_repr.field_names, class_repr.field_types):
            if isinstance(_type, ClassRepresentation):
                ListSerializer._extract_inner_data(item.__dict__[field], _type, data_items)
            else:
                data_items.append(item.__dict__[field])

    def to_bytes(self):
        data_items = time_func("get data items", self.get_data_items, self._list, self.class_repr)
        return time_func("struct pack", struct.pack, self.format, *data_items)

    @staticmethod
    def project_size(class_repr, candidate_obj, list_length):
        data_items = ListSerializer.get_data_items([candidate_obj], class_repr)
        format = primitive_map[class_repr] if class_repr in primitive_map else class_repr.get_format()
        return len(struct.pack(format, *data_items)) * list_length

    def from_bytes(self, _bytes):
        # unpacks into the same objects
        data_items = list(struct.unpack(self.format, _bytes))
        if not isinstance(self.class_repr, ClassRepresentation):
            return data_items
        else:
            output_list = self._list
            self.data_items_unpacked = 0
            for item in output_list:
                self._insert_data(item, self.class_repr, data_items)
            return output_list

    def create_output_list(self, _bytes, sample_object):
        # unpacks into a new list
        format = self.get_format(self.class_repr, self.length)
        data_items = list(struct.unpack(format, _bytes))
        if not isinstance(self.class_repr, ClassRepresentation):
            return data_items
        else:
            output_list = []
            self.data_items_unpacked = 0
            sample_obj_str = pickle.dumps(sample_object)
            for i in range(self.length):
                new_obj = pickle.loads(sample_obj_str)
                self._insert_data(new_obj, self.class_repr, data_items)
                output_list.append(new_obj)
            return output_list

    def _insert_data(self, object, class_repr, data_items):
        for field, _type in zip(class_repr.field_names, class_repr.field_types):
            if isinstance(_type, ClassRepresentation):
                self._insert_data(object.__dict__[field], _type, data_items)
            else:
                object.__dict__[field] = data_items[self.data_items_unpacked]
                self.data_items_unpacked += 1