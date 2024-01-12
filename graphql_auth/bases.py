import graphene

from .shortcuts import OutputErrorType


class SuccessOutput:
    success = graphene.Boolean(default_value=True)


class ErrorsOutput:
    errors = graphene.Field(OutputErrorType)


class SuccessErrorsOutput(SuccessOutput, ErrorsOutput):
    pass


class MutationMixin:
    """
    All mutations should extend this class
    """

    @classmethod
    def mutate(cls, root, info, **input):
        return cls.resolve_mutation(root, info, **input)  # type: ignore

    @classmethod
    def parent_resolve(cls, root, info, **kwargs):
        return super().mutate(root, info, **kwargs)  # type: ignore


class RelayMutationMixin:
    """
    All relay mutations should extend this class
    """

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        return cls.resolve_mutation(root, info, **kwargs)  # type: ignore

    @classmethod
    def parent_resolve(cls, root, info, **kwargs):
        return super().mutate_and_get_payload(root, info, **kwargs)  # type: ignore


class DynamicArgsMixin:
    """
    A class that knows how to initialize graphene arguments

    get args from
        cls._args
        cls._required_args
    args is dict { arg_name: arg_type }
    or list [arg_name,] -> defaults to String
    """

    _args: dict | list = {}
    _required_args: dict | list = {}

    @classmethod
    def Field(cls, *args, **kwargs):
        if isinstance(cls._args, dict):
            for key in cls._args:
                cls._meta.arguments.update({key: graphene.Argument(getattr(graphene, cls._args[key]))})  # type: ignore
        elif isinstance(cls._args, list):
            for key in cls._args:
                cls._meta.arguments.update({key: graphene.String()})  # type: ignore

        if isinstance(cls._required_args, dict):
            for key in cls._required_args:
                cls._meta.arguments.update(  # type: ignore
                    {key: graphene.Argument(getattr(graphene, cls._required_args[key]), required=True)}
                )
        elif isinstance(cls._required_args, list):
            for key in cls._required_args:
                cls._meta.arguments.update({key: graphene.String(required=True)})  # type: ignore
        return super().Field(*args, **kwargs)  # type: ignore


class DynamicInputMixin:
    """
    A class that knows how to initialize graphene relay input

    get inputs from
        cls._inputs
        cls._required_inputs
    inputs is dict { input_name: input_type }
    or list [input_name,] -> defaults to String
    """

    _inputs: dict | list = {}
    _required_inputs: dict | list = {}

    @classmethod
    def Field(cls, *args, **kwargs):
        if isinstance(cls._inputs, dict):
            for key in cls._inputs:
                cls._meta.arguments["input"]._meta.fields.update(  # type: ignore
                    {key: graphene.InputField(getattr(graphene, cls._inputs[key]))}
                )
        elif isinstance(cls._inputs, list):
            for key in cls._inputs:
                cls._meta.arguments["input"]._meta.fields.update({key: graphene.InputField(graphene.String)})  # type: ignore

        if isinstance(cls._required_inputs, dict):
            for key in cls._required_inputs:
                cls._meta.arguments["input"]._meta.fields.update(  # type: ignore
                    {key: graphene.InputField(getattr(graphene, cls._required_inputs[key]), required=True)}
                )
        elif isinstance(cls._required_inputs, list):
            for key in cls._required_inputs:
                cls._meta.arguments["input"]._meta.fields.update(  # type: ignore
                    {key: graphene.InputField(graphene.String, required=True)}
                )
        return super().Field(*args, **kwargs)  # type: ignore
