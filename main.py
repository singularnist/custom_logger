import os
import json
from uuid import UUID
from enum import Enum
from typing import Union,Type
from decimal import Decimal
from datetime import datetime
from sqlalchemy.inspection import inspect



class TxtTools:
    """
    Tool for custom logging

    Attributes:
        log_file (str): Шлях до файлу логів.
        date (datetime): date create message (in the development process)
    """
    def __init__(self, log_file:str='default.txt', del_file:bool=False, date:bool = False) -> None:
        """
        Args:
            log_file (str): The path to the file in which the log will be kept. Defaults to 'default.txt'.
            del_file (bool): If True, the file will be deleted if it exists.
            date (bool):  date create message (in the development process)
        """
        self.log_file = log_file
        self.date = datetime.now() if date else ''
        os.remove(self.log_file) if del_file and os.path.exists(self.log_file) else None

    @staticmethod
    def decimal_default(obj) -> Union[str, TypeError]:
        """
        Converts objects to a string.

        Args:
            obj: The object to convert.

        Returns:
            str: A string representation of an object.

        Raises:
            TypeError: If the object is not JSON serialized.
        """
        if isinstance(obj, Decimal): 
            return str(obj)
        if isinstance(obj, UUID): 
            return str(obj)
        if isinstance(obj, datetime): 
            return str(obj)
        if isinstance(obj, Enum): 
            return str(obj.name)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    @staticmethod
    def model_to_dict(instance, include_relationships=False) -> dict:
        """
        Converts an SQLAlchemy model to a dictionary.

        Args:
            instance: The model object to convert.
            include_relationships (bool): If True, includes the links in the dictionary.

        Returns:
            dict:A dictionary of model attributes.
        """
        data = {c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs}

        if include_relationships:
            relationships = inspect(instance).mapper.relationships
            for key in relationships.keys():
                related_obj = getattr(instance, key)
                if related_obj is not None:
                    if isinstance(related_obj, list):
                        data[key] = [TxtTools.model_to_dict(item, include_relationships=False) for item in related_obj]
                    else:
                        data[key] = TxtTools.model_to_dict(related_obj, include_relationships=False)
        return data

    def log_model(self, model_instance,relation):
        """
        Logs one instance of the model.

        Args:
            model_instance: The instance of the model to log.
            relation: Link to model (used in model_to_dict).
        """
        model_dict = self.model_to_dict(model_instance,relation)
        self.log_message(model_dict)

    def log_models(self, model_instances, relation,):
        """
        Logs multiple instances of models.

        Args:
            model_instances: List of model instances to log.
            relation: Link to model (used in model_to_dict).
        """
        models_dict = [self.model_to_dict(instance,relation) for instance in model_instances]
        self.log_message(models_dict)

    def log_message(self, message: Union[str, dict, list]):
        """
        Writes messages to the log file.

        Args:
            message (Union[str, dict, list]): Message to be logged.
        """
        with open(self.log_file, 'a', encoding='utf-8') as log_file:
            if isinstance(message, (dict, list)):
                log_file.write(json.dumps(message, ensure_ascii=False, indent=4, default=self.decimal_default) + '\n')
            else:
                log_file.write(f"{self.date}{str(message)}\n")
