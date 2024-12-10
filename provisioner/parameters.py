from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Tuple
import geni.portal as portal

@dataclass
class Parameter:
    name: str
    description: str
    typ: str
    longDescription: Optional[str] = None
    defaultValue: Optional[Any] = None
    legalValues: list[Tuple[str, Any]] = []
    advanced: bool = False


class ParameterGroup(ABC):
    parameters: list[Parameter]

    def __init__(self, parameters: list[Parameter]):
        self.parameters = parameters

    def bind(self) -> None:
        portal.context.defineParameterGroup(
            groupId=self.id(),
            groupName=self.name()
        )
        for parameter in self.parameters:
            portal.context.defineParameter(
                name=parameter.name,
                description=parameter.description,
                typ=parameter.typ,
                defaultValue=parameter.defaultValue,
                legalValues=parameter.legalValues,
                longDescription=parameter.longDescription,
                advanced=parameter.advanced,
                groupId=self.id()
            )

    @abstractmethod
    @classmethod
    def id(cls) -> str:
        pass

    @abstractmethod
    @classmethod
    def name(cls) -> str:
        pass

    @abstractmethod
    def validate(self) -> None:
        pass
