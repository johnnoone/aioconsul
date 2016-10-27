from enum import Enum
from datetime import timedelta
from typing import ByteString, NamedTuple, Union
from typing import List, Tuple, Dict, Any, Pattern

Object = Dict[str, Any]
ObjectID = Union[Dict[str, Any], str]
ObjectIndex = Union[Dict[str, Any], int]
Collection = List[Union[Object, str]]
Mapping = Dict[str, Object]
Meta = Dict[str, Any]
CollectionMeta = Tuple[Collection, Meta]
ObjectMeta = Tuple[Object, Meta]
Filter = Union[Pattern, str]
Payload = ByteString
Duration = Union[str, timedelta]


class Consistency(Enum):
    default = "default"
    stale = "stale"
    consistent = "consistent"

# TODO better definition of blocking
BlockWait = NamedTuple('BlockWait', [('index', ObjectIndex), ('wait', Any)])
Blocking = Union[ObjectIndex, BlockWait]
