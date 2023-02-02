import csv
import os
import random
import uuid
import xml.etree.ElementTree as ET
import zipfile
from multiprocessing import Pool
from typing import List

from src.helpers.string_handling import create_random_string
from src.schemas.data_models import TestData, TestObject

__all__ = ('TestXmlManager',)


class TestXml:

    def __init__(self, tree: ET.ElementTree = None):
        if tree is None:
            self.doc: ET.ElementTree = self.__create_test_xml()
            self.data = None
        else:
            self.doc: ET.ElementTree = tree
            self.data: TestData = self.__parse_elements()

    @staticmethod
    def __create_test_xml():
        """
        Сгенерировать xml документ согласно заданному правилу:

            <root>
            <var name=’id’ value=’<случайное уникальное строковое значение>’/>
            <var name=’level’ value=’<случайное число от 1 до 100>’/>
            <objects>
            <object name=’<случайное строковое значение>’/>
            <object name=’<случайное строковое значение>’/>
            ...
            </objects>
            </root>
            В тэге objects случайное число (от 1 до 10) вложенных тэгов object.
        :return: ET.ElementTree
        """
        root = ET.Element("root")
        ET.SubElement(root, "id", {"name": "id", "value": str(uuid.uuid4())})
        ET.SubElement(root, "level", {"name": "level", "value": str(random.randint(1, 100))})
        objects = ET.SubElement(root, "objects")
        for object_number in range(1, random.randint(1, 10)):
            ET.SubElement(objects, "object", {"name": f"{create_random_string(4)}_{object_number}"})

        return ET.ElementTree(root)

    def __parse_elements(self):
        """
        Распаковать элементы xml документа в модель данных TestData.
        :return: TestData
        """
        root = self.doc.getroot()
        return TestData(id=root.find("id").get("value"),
                        level=root.find("level").get("value"),
                        objects=[TestObject(name=_object.get("name")) for _object in root.find("objects")])


class TestXmlManager:
    def __init__(self):
        self.docs: List[TestXml] = []

    @staticmethod
    def save_xml_to_zip(zip_file: str, files_in_zip: int):
        """
        Сгенерировать и записать xml документ в ZIP архив.
        :param zip_file: полный путь к архиву.
        :param files_in_zip: количество файлов в архиве.
        """
        with zipfile.ZipFile(zip_file, 'w') as cur_zip:
            for i in range(files_in_zip):
                with cur_zip.open(f"{create_random_string(8)}.xml", 'w') as file:
                    TestXml().doc.write(file, encoding='UTF-8', xml_declaration=True)

    @staticmethod
    def upload_xml_from_zip(zip_file: str):
        """
        Считать xml документ из ZIP архива.
        :param zip_file: полный путь к архиву.
        :return: List[TestXml]
        """
        with zipfile.ZipFile(zip_file, 'r') as cur_zip:
            return [TestXml(ET.ElementTree(ET.fromstring(cur_zip.read(file)))) for file in cur_zip.namelist()]

    @staticmethod
    def save_data_in_csv(save_file: str, data: list):
        """
        Записать данные в csv файл.
        :param save_file: полный путь к сохраняемому файлу.
        :param data: массив данных, который требуется сохранить.
        """
        with open(save_file, 'w+', newline='') as csv_file:
            data_writer = csv.writer(csv_file, delimiter=' ', quotechar='|')
            for row in data:
                data_writer.writerow(row)

    def generate_files(self, number_of_zips: int, files_in_zip: int, save_dir: str, processes: int = 4):
        """
        Сгенерировать ZIP архивы с заданным количеством xml файлов в них.
        :param number_of_zips: количество архивов.
        :param files_in_zip: xml файлов в архиве.
        :param save_dir: путь к каталогу, в которому требуется сохранить архивы.
        :param processes: количество процессов для распараллеливания.
        """
        pool = Pool(processes=processes)
        for zip_file_number in range(1, number_of_zips + 1):
            name = save_dir + str(zip_file_number) + ".zip"
            pool.apply(self.save_xml_to_zip, args=(name, files_in_zip,))

    def upload_from_files(self, zip_files_dir: str, processes: int = 4):
        """
        Загрузить xml документы из каталога с архивами в хранилище docs экземпляра класса TestXmlManager.
        :param zip_files_dir: путь к каталогу с архивами.
        :param processes: количество процессов для распараллеливания.
        """
        pool = Pool(processes=processes)
        os.chdir(zip_files_dir)
        files_in_dir = os.listdir()
        for file in files_in_dir:
            if zipfile.is_zipfile(zip_files_dir + file):
                res = pool.apply(self.upload_xml_from_zip, (zip_files_dir + file,))
                self.docs += res

    def save_xml_data_to_csv(self, save_dir: str):
        """
        Сохранить данные из документов в хранилище docs в требуемом формате в файлах csv.

        Первый: id, level - по одной строке на каждый xml файл
        Второй: id, object_name - по отдельной строке для каждого тэга object
        :param save_dir: путь к каталогу, в которому требуется сохранить csv.
        """
        self.save_data_in_csv(save_file=save_dir + "files.csv",
                              data=[["id", "level"]] +
                                   [[doc.data.id, doc.data.level] for doc in self.docs])

        self.save_data_in_csv(save_file=save_dir + "objects.csv",
                              data=[["id", "object_name"]] +
                                   [[doc.data.id, obj.name] for doc in self.docs for obj in doc.data.objects]
                              )
