from oscar.apps.catalogue.models import Category


def categories_json(request):

    for root in Category.get_root_nodes():
        for node in root.get_descendants():
            print node
    return ''


# def dictionary_gen(node):
#     if node.is_leaf():
#         return dict([('', '')])
#     else:
#         return dictionary_gen(node)
