import collections
import itertools

class ParameterNameGenerator(object):
    """Class that counts each time a value is looked up."""
    def __init__(self):
        self.d = collections.defaultdict(itertools.count)

    def __getitem__(self, key):
        """Returns a k:v in d equal to key:the number of times that key has come up.
           Used for creating parameter names"""
        return "{}_{}".format(key, next(self.d[key]))