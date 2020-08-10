import re
from .db_conn import get_conn


def _camel_to_snake(value):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()


class Model:

    def __init__(self):
        pass

    def _get_db_table(self):
        return _camel_to_snake(self.__class__.__name__)

    def save(self):
        conn = get_conn()
        if not conn:
            return False
        else:
            cursor = conn.cursor()
        query = ""
        if not self.id:
            query = "INSERT INTO "+self._get_db_table()
        else:
            query = "UPDATE "+self._get_db_table()+" SET "
            query += self._create_update_string()+" WHERE id="+self.__dict__['id']

        try:
            cursor.execute(query)
            conn.close()
            return True
        except:
            return False

    def _create_save_string(self):
        query = "("
        values = " VALUES("
        for key in self.__dict__.keys():
            query += key+","
            if self.__dict__[key]:
                values += self.__dict__[key]+","
            else:
                values += "NULL,"

        return query[:-1]+")" + values[:-1]+")"

    def _create_update_string(self):
        value = ""
        for key in self.__dict__.keys():
            if key == "id":
                continue
            if self.__dict__[key]:
                value += " "+key+"="+self.__dict__[key]+","
            else:
                value += " " + key + "=NULL,"
        if len(value) < 1:
            return None
        return value[:-1]

    def test(self):
        print(self._create_save_string())


def find_automate(port):
    return 1


class Automate(Model):

    def __init__(self, nom, address_ip, port, id=None, bidirectional=False, document=False, image=False):
        self.id = id
        self.address_ip = address_ip
        self.port = port
        self.bidirectional = bidirectional
        self.document = document
        self.image = image


class ResultatAutomate(Model):

    def __init__(self, automate, code, id_rendu, valeur, id=None, nom_rendu=None):
        self.automate = automate
        self.code = code
        self.id_rendu = id_rendu
        self.valeur = valeur
        self.id = id
        self.nom_rendu = nom_rendu


class Header:

    def __init__(self, record, addr=['192.168,1', 20]):
        self.host = addr[0],
        self.port = addr[1],
        self.name = record[4][0],
        self.serial = record[4][0],
        self.protocol = record[12],
        self.date = record[13]
        self.automate = find_automate(addr)

    def log(self):
        return self.__dict__
