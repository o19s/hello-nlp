from .interfaces import Text_to_Text_PipelineInterface

import re

# --------------------------------------
from io import StringIO
from html import unescape
from html.parser import HTMLParser

#Strips HTML tags and entities
class stdlib_strip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_html(html,strip):
    html = unescape(html)
    strip.feed(html)
    text = strip.get_data()
    text = text.strip()
    text = re.sub(r'\s+',' ',text)
    return text

# --------------------------------------
from bs4 import BeautifulSoup
def strip_html_bs4(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    text = text.strip()
    text = re.sub(r'\s+',' ',text)
    return text

# --------------------------------------
def strip_html_lxml(html):
    soup = BeautifulSoup(html, 'lxml')
    text = soup.get_text(separator=' ')
    text = text.strip()
    text = re.sub(r'\s+',' ',text)
    return text

class HTML_Strip(Text_to_Text_PipelineInterface):
    def analyze(self,text:str,context:dict=None) -> str:
        if isinstance(text,list):
            text = ' '.join(text)
        if self.parser == "lxml":
            text = strip_html_lxml(text)
        elif self.parser == "bs4":
            text = strip_html_bs4(text)
        elif self.parser == "html":
            text = strip_html(text,self.strip)
        return text

    def debug(self,text:str,context:dict=None) -> str:
        return "<em>[PARSER="+self.parser+"]</em><br>" + text

    def __init__(self,metadata):
        self.name="html_strip"
        self.pipeline = metadata
        self.pipeline[self.name] = True
        if "html_parser" not in self.pipeline.keys():
            self.pipeline["html_parser"]="lxml"
        self.parser = self.pipeline["html_parser"]
        if self.parser == "html":
            self.strip = stdlib_strip()