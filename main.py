class TxtTools:
    def __init__(self, log_file:str='default.txt', del_file:bool=False, date:bool = False) -> None:
        self.log_file = log_file
        self.date = datetime.now() if date else ''
        os.remove(self.log_file) if del_file and os.path.exists(self.log_file) else None

    @staticmethod
    def decimal_default(obj) -> Union[str, TypeError]:
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
    def model_to_dict(instance, include_relationships=False):
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
        model_dict = self.model_to_dict(model_instance,relation)
        self.log_message(model_dict)

    def log_models(self, model_instances, relation,):
        models_dict = [self.model_to_dict(instance,relation) for instance in model_instances]
        self.log_message(models_dict)

    def log_message(self, message: Union[str, dict, list]):
        with open(self.log_file, 'a', encoding='utf-8') as log_file:
            if isinstance(message, (dict, list)):
                log_file.write(json.dumps(message, ensure_ascii=False, indent=4, default=self.decimal_default) + '\n')
            else:
                log_file.write(f"{self.date}{str(message)}\n")
