from .db_conn import get_conn

params = {
    'WBC': 1121,
    'RBC': 2852,
    'HGB': 1112,
    'HCT': 1114,
    'MCV': 1115,
    'MCH': None,
    'MCHC': 1111,
    'RDW-CV': 0,
    'RDW-SD': 0,
    'PLT': 1113,
    'PDW': None,
    'PCT': None,
    'P-LCC': None,
    'PLCR': None,
    'MPV': None,
    'LYM#': None,
    'LYM%': 1122,
    'MON#': 1118,
    'MON%': 1756,
    'NEU#': 1123,
    'NEU%': 1746,
    'EOS#': 1120,
    'EOS%': 1747,
    'BAS#': 1124,
    'BAS%': 1748,
    'LIC#': None,
    'LIC%': None
}


def get_param_id(param):
    conn = get_conn()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("select id from rendus where automate_rendu='"+param+"' limit 1")
    id = cursor.fetchone()
    if not id:
        return None
    else:
        return id[0]
