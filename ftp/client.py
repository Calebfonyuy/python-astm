from ftplib import FTP
import xml.etree.ElementTree as ET
import re
import time
from os import remove
import sys
sys.path.insert(1, "../")
from astm.logging import ftp_log
from orm.models import get_automates_ftp, ResultatAutomate
from orm.result_params import get_param_id


class FTPClient:
    """
    This class represents the instance of each FTP connection and takes care of
    all the operations related to data collection, parsing and saving to the
    common database.
    """
    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.files = None
        self.ftp = None

    def start(self):
        try:
            ftp_log("Creating ftp client for "+self.host)
            self.ftp = FTP(host=self.host, user=self.user, passwd=self.passwd)
            ftp_log("FTP client successfully connected ")
            self.ftp.cwd('upload')
            ftp_log("Successfully switched to upload folder")
            return True
        except Exception as error:
            ftp_log("Error creating ftp client: "+error)
            return False

    def retrieve_files(self):
        self.files = self.ftp.nlst()
        ftp_log("Retrieving files from server")
        for file in self.files:
            ftp_log("Collecting "+file)
            self.ftp.retrbinary("RETR " + file, open("files/"+file, 'wb').write)
            ftp_log(file+" Collected successfully ")

        self.ftp.close()
        ftp_log("FTP connection successfuly closed")

    def parse_files(self, automate_id):
        for file in self.files:
            ftp_log("Paring "+file)
            file_name = "files/"+file
            try:
                tree = ET.parse(file_name)
            except Exception as error:
                ftp_log("Error parsing file "+file)
                continue

            code = tree.find('requestResult/patientInformation/patientIdentifier').text
            examen_id = tree.find('requestResult/testOrder/test/universalIdentifier/testIdentifier').text
            examen = tree.find('requestResult/testOrder/test/universalIdentifier/testName').text
            valeur = re.findall('[0-9\.]+', tree.find('requestResult/testOrder/test/result/value').text)[0]
            unit = tree.find('requestResult/testOrder/test/result/unit').text
            ftp_log(f"File parsing complete: {code} {examen_id} {examen} {valeur} {unit}")

            result = ResultatAutomate(
                automate=automate_id,
                code_bar=code,
                code_rendu=get_param_id(examen),
                nom_rendu=examen_id+", "+examen,
                valeur=valeur
            )

            if result.save():
                ftp_log("Result succesfully saved: "+str(result))
            else:
                ftp_log("Error saving result: " + str(result))
            # remove(file_name)


class FTPClientManager:
    """
    this class takes care of launching ftp clients and coordinating the
    order of execution of the various tasks from result collection to
    parsing and saving.
    """
    def run(self):
        while True:
            automates = get_automates_ftp()
            for automate in automates:
                ftp_log("Handing automate: "+automate)
                client = FTPClient(automate.ip_address, automate.username, automate.password)
                if client.start():
                    client.retrieve_files()
                    client.parse_files(automate.id)
            # sleep for five minutes
            time.sleep(300)
