class RGColor(object):

    def __init__(self, r=0, g=0, b=0):
        object.__init__(self)
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return '#{}{}{}'.format(
            self.__ff(self.r),
            self.__ff(self.g),
            self.__ff(self.b)
        )

    @staticmethod
    def __ff(val):
        h = hex(val)[2:]
        if len(h) == 1:
            h = '0{}'.format(h)
        return h


class RGReporterOptions(object):

    def __init__(self, entities=None, exclusions=None, out_dir=None, images=None):
        object.__init__(self)
        self.entities = entities
        self.exclusions = exclusions
        self.out_dir = out_dir
        self.images = images
