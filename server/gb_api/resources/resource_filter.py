from typing import Optional, Union, Type

FilterValueType = Type[Union[int, str, bool]]


class ResourceFilter:
    def __init__(self, name: str, value_type: FilterValueType):
        self.name = name
        self.type: FilterValueType = value_type
        self._value: Optional[FilterValueType] = None

    @property
    def value(self) -> Optional[FilterValueType]:
        """The current value of this filter."""
        return self._value

    def set(self, value):
        """Sets the value of this filter."""
        self._value = self.type(value)

    def clear(self):
        self._value = None


class ResourceFilterList(list[ResourceFilter]):
    def get(self, filter_name: str) -> Optional[ResourceFilter]:
        """Gets the filter with the given name."""
        return next((f for f in self if f.name == filter_name), None)

    def get_value(self, filter_name: str) -> Optional[FilterValueType]:
        """The current value of this filter."""
        return self.get(filter_name).value

    def set(self, filter_name: str, value):
        """Sets the value of the filter with the given name."""
        f = self.get(filter_name)
        if f is None:
            raise ValueError(f'Invalid filter name "{filter_name}". Available filters are '
                             f'{str.join(",", [f.name for f in self])}.')
        f.set(value)

    def clear_filter(self, filter_name: str):
        """Clears the value of the filter with the given name."""
        self.get(filter_name).clear()

    def applied(self) -> list[ResourceFilter]:
        return [f for f in self if f.value is not None]
