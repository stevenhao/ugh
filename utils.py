from collections import defaultdict
nested_dict = nested_dict_factory = lambda: defaultdict(nested_dict_factory)