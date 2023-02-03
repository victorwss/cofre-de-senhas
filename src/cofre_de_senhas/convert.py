# Converte uma linha em um dicionário.
def row_to_dict(description, row):
    if row is None: return None
    d = {}
    for i in range(0, len(row)):
        d[description[i][0]] = row[i]
    return d

# Converte uma lista de linhas em um lista de dicionários.
def rows_to_dict(description, rows):
    result = []
    for row in rows:
        result.append(row_to_dict(description, row))
    return result

# Fonte: https://stackoverflow.com/a/54769644
def dict_to_class(klass, d):
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})
    except:
        return d # Not a dataclass field

def row_to_class(klass, description, row):
    dict_to_class(klass, row_to_dict(description, row))

def rows_to_classes(klass, description, row):
    result = []
    for row in rows:
        result.append(row_to_class(klass, description, row))
    return result