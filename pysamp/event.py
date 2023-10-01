import functools
import io
import traceback
import warnings

from .callbacks import registry


def event(callback_name):
    def named_event(args_converter):
        @functools.wraps(args_converter)
        def register(cls, handler):
            @functools.wraps(handler)
            def wrapper(*args):
                return handler(*args_converter(cls, *args))

            if handler.__name__ == callback_name:
                message = io.StringIO()
                traceback.print_stack(file=message, limit=2)
                location = message.getvalue().rsplit('\n', 4)[0].lstrip()
                warnings.warn(
                    f'Handler {handler} has the same name as callback '
                    f'"{callback_name}", this is probably not what you want.\n'
                    f'{location}',
                    stacklevel=2,
                )

            registry.register_callback(
                callback_name,
                wrapper,
                args_converter.__name__,
            )
            return handler

        return classmethod(register)

    return named_event
