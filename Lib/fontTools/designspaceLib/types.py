# pyright: strict

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Union


@dataclass
class Range:
    __slots__ = "start", "end"

    start: float
    """Inclusive start of the range."""
    end: float
    """Inclusive end of the range."""

    def __contains__(self, value: Union[float, Range, Stops]) -> bool:
        if isinstance(value, Range):
            start, end = sorted((value.start, value.end))
            return self.start <= start <= self.end and self.start <= end <= self.end
        if isinstance(value, Stops):
            return all(self.start <= stop <= self.end for stop in value.stops)
        return self.start <= value <= self.end

    def intersection(self, other: Range) -> Optional[Range]:
        self_start, self_end = sorted((self.start, self.end))
        other_start, other_end = sorted((other.start, other.end))
        if self_end < other_start or self_start > other_end:
            return None
        else:
            return Range(max(self_start, other_start), min(self_end, other_end))


@dataclass
class Stops:
    __slots__ = "stops"

    stops: set[float]

    def __contains__(self, value: Union[float, Range, Stops]) -> bool:
        if isinstance(value, Range):
            return value.start == value.end and value.start in self.stops
        if isinstance(value, Stops):
            return all(stop in self.stops for stop in value.stops)
        return value in self.stops


Location = Mapping[str, float]
Region = Mapping[str, Union[Range, Stops]]


# A region selection is either a range or a single value, as a Designspace v5
# axis-subset element only allows a single discrete value or a range for a
# variable-font element.
RegionSelection = Mapping[str, Union[Range, float]]

# A conditionset is a set of named ranges.
ConditionSet = Mapping[str, Range]

# A rule is a list of conditionsets where any has to be relevant for the whole rule to be relevant.
Rule = List[ConditionSet]
Rules = Dict[str, Rule]


def in_region(value: Union[Location, RegionSelection, Region], region: Region) -> bool:
    return value.keys() == region.keys() and all(
        value in region[name] for name, value in value.items()
    )


def location_in_selection(location: Location, selection: RegionSelection) -> bool:
    if location.keys() != selection.keys():
        return False
    for name, value in location.items():
        selection_value = selection[name]
        if isinstance(selection_value, (float, int)):
            if value != selection_value:
                return False
        else:
            if value not in selection_value:
                return False
    return True
