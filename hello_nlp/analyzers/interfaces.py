# -*- coding: utf-8 -*-

"""
Interfaces.

These Interfaces are used to reliably join pipeline stages together
  Each pipeline analyze method accepts one input param and returns one output param
  Defining these classes allows us to declare what can come in and what can go out
"""

from abc import ABC, abstractmethod
from spacy.tokens import Doc, Span

class Text_to_Text_PipelineInterface(ABC):
    @abstractmethod
    def analyze(self,text:str,context:dict=None)->str:
        pass
    @abstractmethod
    def debug(self,text:str,context:dict=None)->str:
        pass


class Text_to_Doc_PipelineInterface(ABC):
    @abstractmethod
    def analyze(self,text:str,context:dict=None)->Doc:
        pass
    @abstractmethod
    def debug(self,doc:Doc,context:dict=None)->str:
        pass

class Doc_to_Doc_PipelineInterface(ABC):
    @abstractmethod
    def analyze(self,doc:Doc,context:dict=None)->Doc:
        pass
    @abstractmethod
    def debug(self,doc:Doc,context:dict=None)->str:
        pass


class Doc_to_Text_PipelineInterface(ABC):
    @abstractmethod
    def analyze(self,doc:Doc,context:dict=None)->str:
        pass
    @abstractmethod
    def debug(self,text:str,context:dict=None)->str:
        pass
