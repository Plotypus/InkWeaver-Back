class FieldType:
    pass


class RequiredField(FieldType):
    def __repr__(self):
        return 'RequiredField'

    def __str__(self):
        return repr(self)


class OptionalField(FieldType):
    def __repr__(self):
        return 'OptionalField'

    def __str__(self):
        return repr(self)
