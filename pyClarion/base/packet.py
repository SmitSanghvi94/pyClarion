'''
Tools for representing activation patterns in pyClarion.

Activation Packets
==================

The ``ActivationPacket`` class represents collections of node activations.

Basic Behavior
--------------

An ``ActivationPacket`` instance behaves mostly like a ``dict`` object.

>>> n1, n2 = Node(), Node()
>>> p = ActivationPacket({n1 : 0.3}) 
>>> p[n1]
0.3
>>> p[n1] = 0.6
>>> p[n1]
0.6
>>> p[n2] = 0.2
>>> p[n2]
0.2

In fact, almost all methods available to ``dict`` are also available to 
``ActivationPacket``.

Default Behavior
----------------

The ``ActivationPacket`` class provides a ``default_activation`` method, which 
may be overridden to capture assumptions about default activation values. 

>>> class MyPacket(ActivationPacket):
...     def default_activation(self, key):
...         return 0.0
...
>>> MyPacket()
MyPacket({})
>>> MyPacket()[Node()]
0.0

When a default value is provided by ``default_activation``, ``ActivationPacket`` 
objects handle unknown keys like ``collections.defaultdict`` objects: they 
output a default value and record the new ``(key, value)`` pair.

>>> p = MyPacket()
>>> n3 = Node()
>>> n3 in p
False
>>> p[n3]
0.0
>>> n3 in p
True

The ``default_activation`` method can be set to return different default values 
for different nodes.

>>> from pyClarion.base.node import Microfeature, Chunk
>>> class MySubtlePacket(ActivationPacket[float]):
...     def default_activation(self, key):
...         if isinstance(key, Microfeature):
...             return 0.5
...         elif isinstance(key, Chunk):
...             return 0.0
... 
>>> mf = Microfeature("color", "red")
>>> ch = Chunk(1234)
>>> p = MySubtlePacket()
>>> mf in p
False
>>> ch in p
False
>>> p[mf]
0.5
>>> p[ch]
0.0

Value Types
-----------

``ActivationPacket`` is implemented as a generic class taking one type variable. 
This type variable specifies the expected value type. Its use is optional.

Packet Types
------------

The type of an ``ActivationPacket`` is meaningful. Different activation sources 
may output packets of different types. For instance, a top-down activation cycle 
may output an instance of ``TopDownPacket``, as illustrated in the example 
below.

>>> class MyTopDownPacket(MyPacket):
...     """Represents the output of a top-down activation cycle.
...     """
...     pass
... 
>>> def my_top_down_activation_cycle(packet):
...     """A dummy top-down activation cycle for demonstration purposes""" 
...     val = max(packet.values())
...     return MyTopDownPacket({n3 : val})
... 
>>> packet = MyPacket({n1 : .2, n2 : .6})
>>> output = my_top_down_activation_cycle(packet)
>>> output == MyPacket({n3 : .6})
True
>>> isinstance(output, MyPacket)
True
>>> isinstance(output, MyTopDownPacket)
True

Selector Packets
================

The ``SelectorPacket`` class serves to capture the result of an action selection 
cycle.

In addition to activation strengths, action selection results in action choices.  
The ``SelectorPacket`` class is a subclass of ``ActivationPacket``, but it has 
one additional attribute called ``chosen``, which may be used to represent 
chosen action chunks.

>>> ch1, ch2 = Chunk(1), Chunk(2)
>>> SelectorPacket({ch1 : .78, ch2 : .24}, chosen={ch1})
SelectorPacket({Chunk(id=1): 0.78, Chunk(id=2): 0.24}, chosen={Chunk(id=1)})
'''

from abc import abstractmethod
from typing import MutableMapping, TypeVar, Hashable, Mapping, Set, Any
from collections import UserDict
from pyClarion.base.node import Node, Chunk


At = TypeVar("At")


class ActivationPacket(UserDict, MutableMapping[Node, At]):
    """A class for representing node activations.

    Has type ``MutableMapping[pyClarion.base.node.Node, At]``, where ``At`` is 
    an unrestricted type variable denoting the expected type for activation 
    values. It is expected that ``At`` will be some numerical type such as 
    ``float``, however this expectation is not enforced.

    By default, ``ActivationPacket`` objects raise an exception when given an 
    unknown key. However, a default activation can be implemented by overriding 
    the ``default_activation`` method. Default activations are handled 
    similarly to ``collections.defaultdict``.

    The precise type of an ``ActivationPacket`` instance may encode important 
    metadata, such as information about the source of the packet. 

    See module documentation for further details and examples.
    """

    def __init__(self, kvpairs : Mapping[Node, At] = None) -> None:

        super().__init__(kvpairs)

    def __repr__(self) -> str:
        
        repr_ = ''.join(
            [
                type(self).__name__,
                '(',
                super().__repr__(),
                ')'
            ]
        )
        return repr_

    def __missing__(self, key : Node) -> At:

        self[key] = value = self.default_activation(key)
        return value

    def default_activation(self, key : Node) -> At:
        '''Return designated default value for the given input.
        '''
        
        raise KeyError

class SelectorPacket(ActivationPacket[At]):
    '''
    Represents the output of an action selection routine.

    Contains information about the selected actions and strengths of actionable 
    chunks. 
    '''

    def __init__(
        self, 
        kvpairs : Mapping[Node, At] = None, 
        chosen : Set[Chunk] = None
    ) -> None:
        '''
        Initialize a ``SelectorPacket`` instance.

        :param kvpairs: Strengths of actionable chunks.
        :param chosen: The set of actions to be fired.
        '''

        super().__init__(kvpairs)
        self.chosen = chosen

    def __eq__(self, other : Any) -> bool:

        if (
            isinstance(other, SelectorPacket) and
            super().__eq__(other) and
            self.chosen == other.chosen
        ):
            return True
        else:
            return False

    def __repr__(self) -> str:
        
        repr_ = ''.join(
            [
                type(self).__name__, 
                '(',
                super(ActivationPacket, self).__repr__(),
                ', ',
                'chosen=' + repr(self.chosen),
                ')'
            ]
        )
        return repr_


if __name__ == '__main__':
    import doctest
    doctest.testmod()