
def extract_id(obj):
    if hasattr(obj, 'id'):
        return obj.id
    return obj
