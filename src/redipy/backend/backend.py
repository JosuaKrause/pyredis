"""This module defines the base class for redipy backends. The backend defined
here handles script compilation. For redis functionality look at the runtime.
"""
from typing import Generic, Protocol, TYPE_CHECKING, TypeVar

from redipy.graph.cmd import CommandObj
from redipy.graph.expr import ExprObj, JSONType
from redipy.graph.seq import SequenceObj


if TYPE_CHECKING:
    from redipy.backend.runtime import Runtime


T = TypeVar('T')
ET = TypeVar('ET')
CC = TypeVar('CC')
EC = TypeVar('EC')
R = TypeVar('R', bound='Runtime')


class ExecFunction(Protocol):  # pylint: disable=too-few-public-methods
    """
    A redis script. Calling this function executes the script.
    """
    def __call__(
            self,
            keys: dict[str, str],
            args: dict[str, JSONType]) -> JSONType:
        """
        Executes the redis script.

        Args:
            keys (dict[str, str]): A dictionary of keys registered in the
            script. It is common convention to pass keys used in the script via
            this parameter but it is not necessary to do so. Importantly, keys
            can also be generated inside the script. The keys of this
            dictionary are the names of the redis keys as registered in the
            script.

            args (dict[str, JSONType]): Arguments to the script. The keys of
            this dictionary are the names of the arguments as registered in the
            script.

        Returns:
            JSONType: The result of the script.
        """
        raise NotImplementedError()


class Backend(Generic[T, ET, CC, EC, R]):
    """
    This class handles compilation of redis scripts.
    """
    def translate(self, seq: SequenceObj) -> T:
        """
        Translate a script into the backends internal type.

        Args:
            seq (SequenceObj): The root sequence object.

        Returns:
            T: The internal representation of the script.
        """
        ctx = self.create_command_context()
        res = self.compile_sequence(ctx, seq)
        return self.finish(ctx, res)

    def create_command_context(self) -> CC:
        """
        Creates a script context.

        Returns:
            CC: The newly created script context.
        """
        raise NotImplementedError()

    def finish(self, ctx: CC, script: T) -> T:
        """
        Finalize the generated script.

        Args:
            ctx (CC): The script context.
            script (T): The internal representation of the script.

        Returns:
            T: The final internal representation of the script.
        """
        raise NotImplementedError()

    def compile_sequence(self, ctx: CC, seq: SequenceObj) -> T:
        """
        Compiles a sequence object.

        Args:
            ctx (CC): The script context.
            seq (SequenceObj): The sequence object.

        Returns:
            T: The internal representation of the sequence object.
        """
        raise NotImplementedError()

    def compile_command(self, ctx: CC, cmd: CommandObj) -> T:
        """
        Compiles a statemement.

        Args:
            ctx (CC): The script context.
            cmd (CommandObj): The statement object.

        Returns:
            T: The internal representation of the statement.
        """
        raise NotImplementedError()

    def compile_expr(self, ctx: EC, expr: ExprObj) -> ET:
        """
        Compiles an expression.

        Args:
            ctx (EC): The script context.
            expr (ExprObj): The expression object.

        Returns:
            ET: The internal representation of the statement.
        """
        raise NotImplementedError()

    def create_executable(
            self,
            code: T,
            runtime: R) -> ExecFunction:
        """
        Create an executable function from an internal representation of the
        script.

        Args:
            code (T): The internal representation of the script.
            runtime (R): The associated runtime.

        Returns:
            ExecFunction: A function that executes the script when called.
        """
        raise NotImplementedError()
