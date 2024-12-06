#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ever find yourself juggling constants, wondering whether the value 0x002A
originated as the index to the Comments field or as the protocol version
number from that binary file? The enums module is a simple implementation
of named enumeration types for Python. It is useful for avoiding lots of
globally defined constants that don't remember who they are or where they
came from. With enums, you can define a collection of values as having a
common type and behavior, and the values will remember their original names
and types.

To use enums, define an enumeration class that inherits from Enum, and then
assign values within the class's scope as Const instances. Then call the
close() class method for your enumeration class, and all the Const values
will be converted in-place to unique instances of your enumeration type. If
you want to control the initialization of your enumeration class, define an
__init__ method just as you would for any normal class, and pass the
arguments to Const(). The arguments will be passed on to your __init__
class unchanged.

The enums module also provides a Registry class, which allows multiple
owners to safely reserve name/value pairs within a shared space.


Example usage:

>>> from enums import Enum, Const

>>> class Enumeration(Enum):
>>>     VALUE1 = Const()
>>>     VALUE2 = Const()
>>> Enumeration.close()

>>> class Enumeration2(Enum):
>>>     def __init__(self, int_val):
>>>         assert isinstance(int_val, int)
>>>         self._int_val = int_val
>>>         super(Enumeration2, self).__init__(int_val)
>>>     def __int__(self):
>>>         return self._int_val
>>>     VALUE1 = Const(10)
>>>     VALUE2 = Const(100)
>>>     VALUE3 = Const(1000)
>>> Enumeration2.close()

>>> Enumeration.VALUE1
Enumeration.VALUE1

>>> Enumeration.VALUE2
Enumeration.VALUE2

>>> Enumeration.VALUE1 == Enumeration.VALUE2
False

>>> Enumeration.VALUE1 == Enumeration2.VALUE1
False

>>> isinstance(Enumeration.VALUE1, Enumeration)
True

>>> int(Enumeration2.VALUE3)
1000
"""
# TODO: Provide an example of how to use the Registry class.


__author__ = 'Aaron Hosford'
__version__ = '0.0.2'

__all__ = [
    'Const',
    'Enum',
]


class Const(object):
    """
    The Const class is used to create new values for enumeration types.

    Example usage:

    >>> from enums import Enum, Const

    >>> class Enumeration(Enum):
    >>>     VALUE1 = Const()
    >>>     VALUE2 = Const()
    >>> Enumeration.close()

    >>> class Enumeration2(Enum):
    >>>     def __init__(self, int_val):
    >>>         assert isinstance(int_val, int)
    >>>         self._int_val = int_val
    >>>         super(Enumeration2, self).__init__(int_val)
    >>>     def __int__(self):
    >>>         return self._int_val
    >>>     VALUE1 = Const(10)
    >>>     VALUE2 = Const(100)
    >>>     VALUE3 = Const(1000)
    >>> Enumeration2.close()

    >>> Enumeration.VALUE1
    Enumeration.VALUE1

    >>> Enumeration.VALUE2
    Enumeration.VALUE2

    >>> Enumeration.VALUE1 == Enumeration.VALUE2
    False

    >>> Enumeration.VALUE1 == Enumeration2.VALUE1
    False

    >>> isinstance(Enumeration.VALUE1, Enumeration)
    True

    >>> int(Enumeration2.VALUE3)
    1000
    """

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    @property
    def name(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()


class Enum(object):
    """
    The Enum class is used as the base class for enumeration types.

    Example usage:

    >>> from enums import Enum, Const

    >>> class Enumeration(Enum):
    >>>     VALUE1 = Const()
    >>>     VALUE2 = Const()
    >>> Enumeration.close()

    >>> class Enumeration2(Enum):
    >>>     def __init__(self, int_val):
    >>>         assert isinstance(int_val, int)
    >>>         self._int_val = int_val
    >>>         super(Enumeration2, self).__init__(int_val)
    >>>     def __int__(self):
    >>>         return self._int_val
    >>>     VALUE1 = Const(10)
    >>>     VALUE2 = Const(100)
    >>>     VALUE3 = Const(1000)
    >>> Enumeration2.close()

    >>> Enumeration.VALUE1
    Enumeration.VALUE1

    >>> Enumeration.VALUE2
    Enumeration.VALUE2

    >>> Enumeration.VALUE1 == Enumeration.VALUE2
    False

    >>> Enumeration.VALUE1 == Enumeration2.VALUE1
    False

    >>> isinstance(Enumeration.VALUE1, Enumeration)
    True

    >>> int(Enumeration2.VALUE3)
    1000
    """

    @classmethod
    def close(cls):
        """Must be called after the class definition ends. Causes constants
        defined therein to be replaced with values of the appropriate type.
        """
        cls._values = []
        for name in dir(cls):
            value = getattr(cls, name)
            if not isinstance(value, Const):
                continue
            replacement = cls(*value._args, **value._kwargs)
            replacement._name = name
            setattr(cls, name, replacement)
            cls._values.append(replacement)

    @classmethod
    def each(cls):
        """Return an iterator over the values in the enumeration."""
        return iter(cls._values)

    @classmethod
    def count(cls):
        """The numer of values in the enumeration."""
        return len(cls._values)

    def __init__(self, *args, **kwargs):
        self._name = ' unnamed '  # Placeholder; overwritten by close()

    @property
    def name(self):
        """The value's name."""
        return self._name

    def __str__(self):
        return self._name

    def __repr__(self):
        return type(self).__name__ + '.' + self._name


class Registry(object):
    """A class for managing a space of unique name/value pairs that could
    potentially be reserved by multiple owners that are not necessarily
    aware of each other's existence or needs. Useful in large software
    systems where disparate modules need to allocate named resources for
    use by the same consumer(s) and it is possible they could accidentally
    allocate the same names for different resources."""

    def __init__(self):
        self._values = {}
        self._owners = {}

    def reserve(self, name, value, owner):
        """Reserve a name in the registry, associating it with a particular
        value and an owner."""
        if name in self._values:
            # This is for situations where a module has to be reloaded.
            if self._values[name] != value or self._owners[name] != owner:
                raise NameError(
                    "This name has already been reserved by " +
                    repr(self._owners[name]) + "."
                )
        self._values[name] = value
        self._owners[name] = owner

    def get_value(self, name):
        """Get the value associated with the given name."""
        if name not in self._values:
            raise NameError("This name is undefined.")
        return self._values[name]

    def get_owner(self, name):
        """Get the owner that reserved the given name."""
        if name not in self._owners:
            raise NameError("This name is undefined.")
        return self._owners[name]

    def is_reserved(self, name):
        """Return a Boolean value indicating whether the given name has
        already been reserved."""
        return name in self._values

    def __getitem__(self, name):
        return self.get_value(name)

    def __contains__(self, name):
        return self.is_reserved(name)


def test():
    """Runs a test to verify that the module contents work as advertised.
    """

    class Enumeration(Enum):
        VALUE1 = Const()
        VALUE2 = Const()
    Enumeration.close()

    class Enumeration2(Enum):
        def __init__(self, int_val):
            assert isinstance(int_val, int)
            self._int_val = int_val
            super(Enumeration2, self).__init__(int_val)

        def __int__(self):
            return self._int_val

        VALUE1 = Const(10)
        VALUE2 = Const(100)
        VALUE3 = Const(1000)
    Enumeration2.close()

    assert repr(Enumeration.VALUE1) == 'Enumeration.VALUE1'
    assert repr(Enumeration.VALUE2) == 'Enumeration.VALUE2'
    assert Enumeration.VALUE1 != Enumeration.VALUE2
    assert Enumeration.VALUE1 != Enumeration2.VALUE1
    assert isinstance(Enumeration.VALUE1, Enumeration)
    assert int(Enumeration2.VALUE3) == 1000
    assert (set(Enumeration.each()) ==
            {Enumeration.VALUE1, Enumeration.VALUE2})

    # TODO: Test cases for Registry class.


if __name__ == "__main__":
    test()
