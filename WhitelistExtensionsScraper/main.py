from typing import TextIO, Union
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup, Comment


class EXPORT_MODE:
    CSV = 0
    HUMAN = 1

class ExtensionDetailExtractor(object):


    def __init__(self, export_mode: EXPORT_MODE, output_file: str):
        self.header = {"User-Agnet": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"}

        self.export_mode: EXPORT_MODE = export_mode
        self.output_file : TextIO = open(output_file, "w", encoding="utf-8")
        self.csv_first_write = True

    def get_id_from_file(self, fileName):
        with open(fileName, "r") as file:
            self.ext_ids = file.read().split(",")

    def process_all_id(self):
        for i, ext_id in enumerate(self.ext_ids):
            print(f"Processing: {i}/{len(self.ext_ids)} ({round(i / len(self.ext_ids) * 100, 2)}%). Current ID: {ext_id}", end="\r")
            info = self.get_ext_info(ext_id)
            self.save_info_to_file(info)
        print("\nProcessing Completed\n")

    def get_ext_info(self, ext_id: str):
        r = requests.get("https://chrome.google.com/webstore/detail/{}".format(ext_id), headers=self.header)
        if r.status_code >= 400:
            return {"error": True, "error_code": r.status_code, "id": ext_id}
        return self.parse_ext_info(r.content, ext_id)

    def parse_ng_directive(self, raw_directive: str) -> dict:
        """
        Sample Directive
        <PageMap><DataObject type="document"><Attribute name="page_lang_safe">en_US</Attribute><Attribute name="item_category">PLATFORM_APP</Attribute><Attribute name="container">CHROME</Attribute><Attribute name="family_unsafe">false</Attribute><Attribute name="user_count">29632</Attribute><Attribute name="supported_regions">AE,AR,AT,AU,BE,BG,BR,CA,CH,CL</Attribute><Attribute name="supported_regions">CN,CO,CU,CZ,DE,DK,EC,EE,EG,ES</Attribute><Attribute name="supported_regions">FI,FR,GB,GR,HK,HU,ID,IE,IL,IN</Attribute><Attribute name="supported_regions">IT,JP,LT,MA,MX,MY,NL,NO,NZ,PA</Attribute><Attribute name="supported_regions">PE,PH,PL,PT,RO,RU,SA,SE,SG,SK</Attribute><Attribute name="supported_regions">TH,TR,TW,UA,US,VE,VN,ZA,001</Attribute><Attribute name="payment_type">free</Attribute><Attribute name="canonical">true</Attribute><Attribute name="kiosk">false</Attribute><Attribute name="by_google">false</Attribute><Attribute name="works_offline">false</Attribute><Attribute name="available_on_android">false</Attribute><Attribute name="autogen">false</Attribute><Attribute name="stars2">true</Attribute><Attribute name="stars3">true</Attribute><Attribute name="stars4">false</Attribute><Attribute name="stars5">false</Attribute><Attribute name="category">69_office_applications,7_productivity</Attribute></DataObject></PageMap>
        """
        directives = ElementTree.fromstring(raw_directive)[0]
        data = {}
        for directive in directives:
            data.update({directive.attrib["name"]: directive.text})
        return data

    def parse_ext_info(self, page_source: Union[bytes, str], ext_id: str):
        soup = BeautifulSoup(page_source, "lxml")
        ext_title = soup.find("title").contents 
        ext_descip = soup.find("meta", attrs={"property": "og:description"})["content"]
        title_parsed = "-".join(ext_title[0].split("-")[:-1])

        # get Angular Directive from comment
        raw_directive = soup.find(text=lambda text: isinstance(text, Comment))
        ext_extended_info = self.parse_ng_directive(raw_directive)
        ext_extended_info.pop("curation", None)
        ext_extended_info.pop("canonical", None)
        info = {
            "error": False,
            "error_code": -1,
            "id": ext_id,
            "title": title_parsed,
            "description": ext_descip,
        }
        info.update(ext_extended_info)
        return info

    def save_info_to_file(self, info: dict):
        if self.export_mode == EXPORT_MODE.CSV:
            self.write_csv(info)
        elif self.export_mode == EXPORT_MODE.HUMAN:
            self.write_human(info)

    def write_csv(self, info: dict):
        if self.csv_first_write:
            self.output_file.write(",".join([str(i).replace(",", " ") for i in info.keys()]) + "\n")
            self.csv_first_write = False
        self.output_file.write(",".join([str(i).replace(",", " ").replace("\n", "\t") for i in info.values()]) + "\n")

    def write_human(self, info: dict):
        if (info["error"]):
            self.output_file.write("ERROR: Failed to get details for Addon with ID: {}. HTTP Status: {} has been Returned from target server.", info["id"], info["error_code"])
        else:
            self.output_file.write(f"ID: {info['id']}\nName: {info['title']}\nDescription: {info['description']}\nType: {info['item_category']}\n\n")

    def __del__(self):
        self.output_file.close()


ext_extract = ExtensionDetailExtractor(EXPORT_MODE.CSV, "ext_info.csv")
ext_extract.get_id_from_file("ext.txt")
ext_extract.process_all_id()
