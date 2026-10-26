#!/usr/bin/env python3
"""
Implementation of relational algebra operations using pandas
"""

import pathlib

import pandas as pd


class Relation:
    """Relation that stores tabular data"""

    def __init__(
        self, data_src: "str | pathlib.Path | Relation | pd.DataFrame | None", *args, **kwargs
    ):
        """Create a new relation either from a CSV file or from another Relation

        :param data: data source
        :raises ValueError: if the source is empty
        :raises TypeError: if the source cannot be processed
        """
        self._data: pd.DataFrame = pd.DataFrame()
        if isinstance(data_src, str) and pathlib.Path(data_src).suffix == ".csv":
            if not pathlib.Path(data_src).exists():
                raise FileNotFoundError(f"Check the path to {data_src}.")
            data = pd.read_csv(data_src, *args, **kwargs)
            if isinstance(data, pd.DataFrame):
                self._data = data
            else:  # TextFileReader
                self._data = pd.concat([chunk for chunk in data], ignore_index=True)
        elif isinstance(data_src, pathlib.Path) and data_src.suffix == ".csv":
            if not data_src.exists():
                raise FileNotFoundError(f"Check the path to {data_src}.")
            data = pd.read_csv(data_src, *args, **kwargs)
            if isinstance(data, pd.DataFrame):
                self._data = data
            else:  # TextFileReader
                self._data = pd.concat([chunk for chunk in data], ignore_index=True)
        elif isinstance(data_src, pd.DataFrame):
            self._data = data_src.drop_duplicates()
        elif isinstance(data_src, Relation):
            self._data = data_src.data.drop_duplicates()
        elif data_src is None:
            raise ValueError(
                "A relation can only be created from a valid source but none was provided."
            )
        else:
            raise TypeError(
                f"A relation can not be created from the provided data source >>{data_src}<<."
            )
        assert isinstance(self._data, pd.DataFrame)

    @property
    def data(self):
        """Data as a property"""
        return self._data

    @property
    def columns(self):
        """Names of the attributes"""
        return self._data.columns

    @property
    def dim(self):
        """Return dimensions (rows x columns) of the relation"""
        return len(self._data), len(self._data.columns)

    @property
    def one(self) -> dict:
        """Return one (first) record of the relation"""
        if len(self._data) == 0:
            raise ValueError("The relation is empty")
        return self._data.iloc[0].to_dict()

    def __getitem__(self, key):
        """Allow getting a specific attribute"""
        return self._data[key]

    def __setitem__(self, key, value) -> None:
        """Allow setting a specific attribute"""
        self._data[key] = value

    def __bool__(self) -> bool:
        """Evaluate the relation as a boolean"""
        return bool(self._data)

    def __repr__(self) -> str:
        """Represent the relation"""
        return repr(self._data)

    def _repr_html_(self) -> str:
        """Represent the relation as an HTML table"""
        return self._data.to_html()

    def _repr_latex_(self) -> str:
        """Represent the relation as LaTeX"""
        return self._data.to_latex()

    def __str__(self) -> str:
        """Convert the relation to a string"""
        return str(self._data)

    def __len__(self) -> int:
        """Get the length of the relation"""
        return len(self._data)

    def __add__(self, other) -> "Relation":
        """Add two relations"""
        return self.union(other)

    def __sub__(self, other) -> "Relation":
        """Subtract two relations"""
        return self.minus(other)

    def __mul__(self, other) -> "Relation":
        """Multiply two relations"""
        return self.product(other)

    def head(self, n: int = 5) -> "Relation":
        """Return the first couple records"""
        return Relation(self._data.head(n))

    def tail(self, n: int = 5) -> "Relation":
        """Return the last couple records"""
        return Relation(self._data.tail(n))

    def to_csv(self, filepath: str | pathlib.Path):
        """Save the relation to a CSV file"""
        self._data.to_csv(filepath, index=False)

    def to_html(self) -> str:
        """Represent the relation as an HTML table"""
        return self._data.to_html()

    def to_latex(self) -> str:
        """Represent the relation as LaTeX"""
        return self._data.to_latex()

    def copy(self) -> "Relation":
        """Return a deep copy of the relation"""
        return Relation(self._data.copy())

    def cleanup(self):
        """Remove empty (all NA) records from the relation"""
        return Relation(self._data.dropna(how="all"))

    def drop_duplicates(self) -> "Relation":
        """Remove duplicate records from the relation"""
        return Relation(self._data.drop_duplicates())

    def equals(self, other: "Relation", exact: bool = False) -> bool:
        """Compare two relations for equality

        :param exact: consider index when comparing relations
        """
        if exact:
            return self._data.equals(other.data)
        return self._data.reset_index(drop=True).equals(other.data.reset_index(drop=True))

    def minus(self, other: "Relation") -> "Relation":
        """Find the difference between two relations"""
        if not isinstance(other, Relation):
            raise TypeError("Can only find the difference between two relations.")
        return Relation(self._data[~self._data.isin(other.data)]).cleanup()

    def intersection(self, other: "Relation") -> "Relation":
        """Find the intersection of two relations"""
        if not isinstance(other, Relation):
            raise TypeError("Can only find the intersection of two relations.")
        return Relation(self._data[self._data.isin(other.data)]).cleanup()

    def query(self, expr, *args, **kwargs) -> "Relation":
        """A simple pass-through to the pandas query"""
        return Relation(self._data.query(expr, *args, **kwargs))

    def select(self, expr: str) -> "Relation":
        """Selection operation of the relational algebra

        :param expr: query string
        :return: a new relation
        """
        return Relation(self._data.query(expr))

    def project(self, attributes: list[str]) -> "Relation":
        """Projection operation of the relational algebra

        :param attributes: a list of attributes to extract
        :raises TypeError: if the argument is not a list
        :raises ValueError: if any attribute is not a valid column name
        :return: a new relation
        """
        if not isinstance(attributes, list):
            raise TypeError("Projection uses a list of attributes as an argument.")
        missing_attributes = set(attributes).difference(set(self._data.columns))
        if len(missing_attributes) > 0:
            raise ValueError(
                f"There are no attributes >>{', '.join(sorted(missing_attributes))}<< in this relation."
            )
        return Relation(self._data[attributes])

    def rename(self, old_name: str, new_name: str) -> "Relation":
        """Rename operation of the relational algebra

        :param old_name: old name of an attribute
        :param new_name: new name of an attribute
        :raises ValueError: if the old name is not a valid column name
        :raises ValueError: if the new name is a name of an existing attribute
        :return: a new relation
        """
        if old_name not in self._data.columns:
            raise ValueError(f"There is no attribute >>{old_name}<< in this relation.")
        if new_name in self._data.columns:
            raise ValueError(f"There is already an attribute >>{new_name}<< in this relation.")
        return Relation(self._data.rename(columns={old_name: new_name}))

    def sort(self, attributes: list[str], *args, **kwargs) -> "Relation":
        """Sorting operation of the relational algebra

        :param query: attributes to sort by
        :param ascending: default True
        :return: a new relation
        """
        return Relation(self._data.sort_values(attributes, *args, **kwargs))

    def extend(self, new_attribute: str, new_values: pd.Series) -> "Relation":
        """Extending operation of the relational algebra

        :param new_attribute: name of the new attribute
        :param new_values: series of values
        :raises ValueError: if the new name is a name of an existing attribute
        :return: a new relation
        """
        if new_attribute in self._data.columns:
            raise ValueError(f"There is already an attribute >>{new_attribute}<< in this relation.")
        new_values.name = new_attribute
        return Relation(pd.concat([self._data, new_values], axis=1))

    def groupby(self, attributes: list[str]) -> "RelationGroupBy":
        """GroupBy operation of the relational algebra

        :param query: attributes to group by
        :raises TypeError: if the argument is not a list
        :return: a new relation group by object

        """
        if not isinstance(attributes, list):
            raise TypeError("Grouping uses a list of attributes as an argument.")
        return self.RelationGroupBy(self._data.groupby(attributes), attributes)

    class RelationGroupBy:
        """An intermediate grouping object"""

        def __init__(self, grouping: pd.api.typing.DataFrameGroupBy, attributes: list[str]):
            self.grouping = grouping
            self.attributes = attributes

        def __repr__(self) -> str:
            """Represent the grouping"""
            return repr(pd.DataFrame(list(self.grouping.groups.keys()), columns=self.attributes))

        def __str__(self) -> str:
            """Convert the grouping to a string"""
            return str(pd.DataFrame(list(self.grouping.groups.keys()), columns=self.attributes))

        def count(self, attribute: str) -> "Relation":
            """Compute count of group"""
            return Relation(
                self.grouping[attribute].count().to_frame(name=f"count_{attribute}").reset_index()
            )

        def sum(self, attribute: str) -> "Relation":
            """Compute sum of group values"""
            return Relation(
                self.grouping[attribute].sum().to_frame(name=f"sum_{attribute}").reset_index()
            )

        def min(self, attribute: str) -> "Relation":
            """Compute min of group values"""
            return Relation(
                self.grouping[attribute].min().to_frame(name=f"min_{attribute}").reset_index()
            )

        def max(self, attribute: str) -> "Relation":
            """Compute max of group values"""
            return Relation(
                self.grouping[attribute].max().to_frame(name=f"max_{attribute}").reset_index()
            )

        def avg(self, attribute: str) -> "Relation":
            """Compute average of group values"""
            return Relation(
                self.grouping[attribute].mean().to_frame(name=f"avg_{attribute}").reset_index()
            )

        def mean(self, attribute: str) -> "Relation":
            """Compute mean of group values"""
            return Relation(
                self.grouping[attribute].mean().to_frame(name=f"mean_{attribute}").reset_index()
            )

        def median(self, attribute: str) -> "Relation":
            """Compute median of group values"""
            return Relation(
                self.grouping[attribute].median().to_frame(name=f"median_{attribute}").reset_index()
            )

    def product(self, other: "Relation") -> "Relation":
        """Cartesian product operation of the relational algebra

        :param other: another relation
        :raises TypeError: if the argument is not a relation
        :raises ValueError: if the attributes are not disjoint
        :return: a new relation
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only find a product of two relations.")
        if set(self.columns).intersection(set(other.columns)):
            raise ValueError(
                "Two relations must have disjoint attributes for cartesian product to work."
            )
        return Relation(self._data.merge(other.data, how="cross"))

    def union(self, other: "Relation") -> "Relation":
        """Union operation of the relational algebra

        :param other: another relation
        :raises TypeError: if the argument is not a relation
        :raises ValueError: if attributes do not match
        :return: a new relation
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only find a union of two relations.")
        if not self.columns.equals(other.columns):
            raise ValueError("Names of the attributes must be the same in both relations.")
        return Relation(pd.concat([self._data, other.data]))

    def naturaljoin(self, other: "Relation") -> "Relation":
        """Natural join operation of the relational algebra

        :param other: another relation
        :raises TypeError: if the argument is not a relation
        :raises TypeError: if either of the provided attributes is not a string
        :raises ValueError: if there are no matching attributes
        :return: a new relation
        :alias: njoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        if not set(self.columns).intersection(set(other.columns)):
            raise ValueError("There are no common attributes between these relations to join them.")
        return Relation(self._data.merge(other.data, how="inner"))

    njoin = naturaljoin

    def equijoin(self, other: "Relation", left_attrib: str, right_attrib: str) -> "Relation":
        """Equijoin operation of the relational algebra

        :param other: another relation
        :param left_attrib: attribute in the left relation
        :param right_attrib: attribute in the right relation
        :raises TypeError: if the argument is not a relation
        :raises TypeError: if either of the provided attributes is not a string
        :raises ValueError: if the provided left attribute is not found in the left relation
        :raises ValueError: if the provided right attribute is not found in the right relation
        :return: a new relation
        :alias: ejoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        if not isinstance(left_attrib, str) or not isinstance(right_attrib, str):
            raise TypeError("Attributes must be strings.")
        if left_attrib not in self.columns:
            raise ValueError(f"There is no attribute >>{left_attrib}<< in the left relation.")
        if right_attrib not in other.columns:
            raise ValueError(f"There is no attribute >>{right_attrib}<< in the right relation.")
        return Relation(
            self._data.merge(other.data, how="inner", left_on=left_attrib, right_on=right_attrib)
        )

    ejoin = equijoin

    def semijoin(self, other: "Relation", left_attrib: str, right_attrib: str) -> "Relation":
        """Semijoin operation of the relational algebra

        :param other: another relation
        :param left_attrib: attribute in the left relation
        :param right_attrib: attribute in the right relation
        :raises TypeError: if the argument is not a relation
        :raises TypeError: if either of the provided attributes is not a string
        :raises ValueError: if the provided left attribute is not found in the left relation
        :raises ValueError: if the provided right attribute is not found in the right relation
        :return: a new relation
        :alias: sjoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        if not isinstance(left_attrib, str) or not isinstance(right_attrib, str):
            raise TypeError("Attributes must be strings.")
        if left_attrib not in self.columns:
            raise ValueError(f"There is no attribute >>{left_attrib}<< in the left relation.")
        if right_attrib not in other.columns:
            raise ValueError(f"There is no attribute >>{right_attrib}<< in the right relation.")
        return Relation(self[self[left_attrib].isin(other[right_attrib])])

    sjoin = semijoin

    def antijoin(self, other: "Relation", left_attrib: str, right_attrib: str) -> "Relation":
        """Antijoin operation of the relational algebra

        :param other: another relation
        :param left_attrib: attribute in the left relation
        :param right_attrib: attribute in the right relation
        :raises TypeError: if the argument is not a relation
        :raises TypeError: if either of the provided attributes is not a string
        :return: a new relation
        :alias: ajoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        if not isinstance(left_attrib, str) or not isinstance(right_attrib, str):
            raise TypeError("Attributes must be strings.")
        return Relation(self[~self[left_attrib].isin(other[right_attrib])])

    ajoin = antijoin

    def outerjoin(self, other: "Relation") -> "Relation":
        """Full outer join operation of the relational algebra

        :param other: another relation
        :param left_attrib: attribute in the left relation
        :param right_attrib: attribute in the right relation
        :raises TypeError: if the argument is not a relation
        :raises ValueError: if the provided left attribute is not found in the left relation
        :raises ValueError: if the provided right attribute is not found in the right relation
        :return: a new relation
        :alias: ojoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        return Relation(self._data.merge(other.data, how="outer"))

    ojoin = outerjoin
