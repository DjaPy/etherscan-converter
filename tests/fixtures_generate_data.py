import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import EnumMeta
from typing import Any, Callable, Dict, Type, TypeVar, Union

import pydantic
import pytest
import rstr
from pydantic import AnyHttpUrl, BaseModel, EmailStr

TestBaseModel = TypeVar('TestBaseModel')


@pytest.fixture
def generator_data(fake):
    def error(field_type_, field_name):
        raise ValueError(f'Type "{field_type_}" not found in generator, field "{field_name}"')

    generator_map = {
        int: lambda *args: fake.pyint(),
        float: lambda *args: fake.pyfloat(),
        str: lambda *args: fake.pystr(),
        bool: lambda *args: fake.pybool(),
        Any: lambda *args: fake.pystr(),
        datetime: lambda *args: fake.date_time(),
        date: lambda *args: fake.date_time().date(),
        uuid.UUID: lambda *args: uuid.uuid4(),
        pydantic.types.UUID4: lambda *args: uuid.uuid4(),
        Decimal: lambda *args: fake.pydecimal(),
        EnumMeta: lambda type_: fake.random.choice(list(type_)).value,
        EmailStr: lambda *args: fake.email(),
        pydantic.types.PositiveInt: lambda *args: fake.pyint(min_value=1),
        pydantic.types.ConstrainedNumberMeta: lambda *args: fake.pyint(min_value=1, max_value=10),
        AnyHttpUrl: lambda *args: fake.url(),
        'List': lambda type_: [generator_map.get(type_, lambda: None)() for _ in range(fake.random.randint(1, 10))],
        'Dict': lambda type_, key_field=None: {
            generator_map.get(key_field)() or fake.pystr(): generator_map.get(type_)() for _ in range(fake.random.randint(1, 10))
        },
        None: lambda: None
    }

    def generator(type_: Any, not_found: Callable) -> Callable:
        result = generator_map.get(type_)
        if result:
            return result

        if type_.__name__ == 'ConstrainedStrValue' and type(type_) is type:
            max_len = getattr(type_, 'max_length', None)
            if getattr(type_, 'regex', None):
                result_regex = rstr.xeger(type_.regex.pattern)
                result_regex = result_regex[:max_len]
                return lambda *args: result_regex
            else:
                result = fake.pystr(max_chars=max_len)
                return lambda *args: result
        return not_found

    def _inner(
            model: Type[TestBaseModel],
            *,
            override: Dict = None,
            return_dict: bool = False
    ) -> Union[Dict[str, Any], TestBaseModel]:
        result = {}
        if override and not isinstance(override, dict):
            raise ValueError('Type override is not dict')
        translate_alias: Dict[str, str] = {}
        for field_name, field_type in model.__fields__.items():
            if field_type.alt_alias:
                translate_alias[field_name] = field_type.alias
                field_name = field_type.alias
            complex_type = hasattr(field_type.outer_type_, '_name')
            if field_type.required or fake.pybool():
                if isinstance(field_type.type_, type) and issubclass(field_type.type_, BaseModel):
                    if complex_type:
                        caller = generator(field_type.outer_type_._name, error)
                        result[field_name] = [
                            _inner(field_type.type_, override=override and override.get(field_name, None),
                                   return_dict=return_dict) for _ in caller(field_type.type_)]
                    else:
                        result[field_name] = _inner(field_type.type_,
                                                    override=override and override.get(field_name, None),
                                                    return_dict=return_dict)
                else:
                    if complex_type:
                        caller = generator(field_type.outer_type_._name, error)
                        if hasattr(field_type, 'key_field') and field_type.key_field:
                            result[field_name] = caller(field_type.type_, field_type.key_field.outer_type_)
                        else:
                            result[field_name] = caller(field_type.type_)
                    else:
                        if type(field_type.type_) is type:
                            type_ = field_type.type_
                        else:
                            type_ = type(field_type.type_)
                        result[field_name] = generator(type_, lambda *args: error(field_type.type_, field_name))(field_type.type_)
        if override:
            translated_override: Dict[str, Any] = {}
            for key, value in override.items():
                translated_override[translate_alias.get(key, key)] = value
            result.update(translated_override or {})
        return result if return_dict else model(**result)

    return _inner
