from .utils import ANALYZED_STRING_MAPPING


def richtext_mapping(context):
    return ANALYZED_STRING_MAPPING
    
    
def richtext_index(context):
    richtext = context.text
    if richtext:
        return richtext.output
    else:
        return u''