from typing import Union, List, Tuple, Dict, Any

ObjectIndex = Union[Dict[str, Any], str]
ObjectID = Union[Dict[str, Any], str]
Object = Dict[str, Any]
Collection = List[Union[Object, str]]
Mapping = Dict[str, Object]
Meta = Dict[str, Any]
CollectionMeta = Tuple[Collection, Meta]
ObjectMeta = Tuple[Object, Meta]
