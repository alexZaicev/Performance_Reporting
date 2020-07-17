from models.errors import RGError


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

    def __init__(self, entities=None, exclusions=None, out_dir=None, images=None, fym=None):
        object.__init__(self)
        self.entities = entities
        self.exclusions = exclusions
        self.out_dir = out_dir
        self.images = images
        self.fym = fym


class RGFile(object):

    def __init__(self, f_type=None, name=None, fym=None, path=None):
        object.__init__(self)
        self.f_type = f_type
        self.name = name
        self.fym = fym
        self.path = path

    def __str__(self):
        return '::FILE INFORMATION::\nTYPE: {}\nNAME: {}\nPATH: {}'.format(self.f_type, self.name, self.path)


class RGFileContainer(object):

    def __init__(self, files=()):
        object.__init__(self)
        for f in files:
            if not isinstance(f, RGFile):
                raise RGError('RGFileContainer cannot contain files of unsupported type [{}]'.format(type(f)))
        self.files = files
        self.files.sort(key=lambda x: (x.f_type, x.fym))

    def find(self, name=None, f_type=None, fym=None):
        if name is not None:
            for file in self.files:
                if file.name == name:
                    return file

        if f_type is not None:
            files = [x for x in self.files if x.f_type == f_type]
            if len(files) > 0:
                if fym is None:
                    return files[len(files) - 1]
                else:
                    files.sort(key=lambda x: x.fym, reverse=True)
                    for file in files:
                        if str(file.fym) <= str(fym):
                            return file
        return None
