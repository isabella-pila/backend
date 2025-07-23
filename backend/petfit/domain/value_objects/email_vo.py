import re
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Self # Necessário para type hinting do retorno do validador

class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise ValueError("e-mail inválido")
        self._value = value

    def _is_valid(self, email: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    # Alterado para 'get_value' ou manter como 'value' mas com parênteses na chamada
    # Manter como 'value()' para consistência com o que você já tinha se for um método
    def value(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self._value == other._value
        if isinstance(other, str): # Permite Email("test@a.com") == "test@a.com"
            return self._value == other
        return NotImplemented

    def __str__(self) -> str:
        return self._value

    def __hash__(self) -> int: # Adicionado: Bom ter __hash__ se você define __eq__
        return hash(self._value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler) -> CoreSchema:
        """
        Define como o Pydantic deve lidar com a validação e serialização do tipo Email.
        """
        def validate_from_str(value: str) -> Self:
            """Valida uma string e cria uma instância de Email."""
            return cls(value) # Chama o __init__ do Email com a string validada

        string_schema = core_schema.str_schema() # Esquema para garantir que o input é uma string
        email_instance_schema = core_schema.is_instance_schema(cls) # Esquema para verificar se já é uma instância de Email
        plain_validator = core_schema.no_info_plain_validator_function(validate_from_str) # Validador principal

        # Retorna um esquema union que tenta validar:
        # 1. Se o valor já é uma instância de Email
        # 2. Se o valor é uma string que pode ser convertida em Email
        return core_schema.union_schema(
            [
                email_instance_schema,
                core_schema.chain_schema([string_schema, plain_validator])
            ],
            # Define como o Email deve ser serializado de volta para uma string
            serialization=core_schema.to_string_ser_schema()
        )