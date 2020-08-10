import re
from .db_conn import get_conn


def _camel_to_snake(value):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()


def find_automate(model, serial_number, software_version):
    with get_conn() as conn:
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM automates_automate where model='"+model+"' and serial_number='"+serial_number
                       + "' and software_version='"+software_version+"'")
        return cursor.fetchone()[0]


class Model:

    def __init__(self):
        pass

    def _get_db_table(self):
        return ("automates_"+self.__class__.__name__).lower()

    def save(self):
        conn = get_conn()
        if not conn:
            return False
        else:
            cursor = conn.cursor()
        query = ""
        if not self.id:
            query = "INSERT INTO "+self._get_db_table()+self._create_save_string()
        else:
            query = "UPDATE "+self._get_db_table()+" SET "
            query += self._create_update_string()+" WHERE id="+self.__dict__['id']

        try:
            cursor.execute(query)
            conn.close()
            return True
        except Exception as ex:
            print(ex)
            return False

    def _create_save_string(self):
        query = "("
        values = " VALUES("
        for key in self.__dict__.keys():
            if key == "id":
                continue
            query += key+","
            if self.__dict__[key]:
                if not isinstance(self.__dict__[key], str):
                    values += str(self.__dict__[key]) + ","
                else:
                    values += "'" + self.__dict__[key] + "',"
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


class ResultatAutomate(Model):

    def __init__(self, automate, code_bar, code_rendu, nom_rendu, valeur, id=None, created_at=None):
        self.automate_id = automate
        self.code_bar = code_bar
        self.code_rendu = code_rendu
        self.nom_rendu = nom_rendu
        self.valeur = valeur
        self.id = id
        self.statut = 1
        self.created_at = created_at
        self.updated_at = created_at

    def __str__(self):
        return self.nom_rendu
