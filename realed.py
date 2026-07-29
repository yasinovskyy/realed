#!/usr/bin/env python3
"""
Implementation of relational algebra operations using pandas

@author: Roman Yasinovskyy
@version: 2026.7
"""

import pathlib

import pandas as pd


class Relation(pd.DataFrame):
    """Relation that stores tabular data"""

    @property
    def _constructor(self):
        return Relation

    def __init__(self, data_src: str | pd.DataFrame | None, *args, **kwargs):
        """Create a new relation either from a CSV file or from another Relation

        :param data: data source
        :raises ValueError: if the source is empty
        :raises TypeError: if the source cannot be processed
        """
        if isinstance(data_src, str) and pathlib.Path(data_src).suffix == ".csv":
            if not pathlib.Path(data_src).exists():
                raise FileNotFoundError(f"Check the path to {data_src}.")
            super().__init__(pd.read_csv(data_src), *args, **kwargs)  # type: ignore
        elif isinstance(data_src, (pd.DataFrame, Relation)):
            super().__init__(data_src, *args, **kwargs)  # type: ignore
        elif data_src is None:
            raise ValueError("A relation can only be created from a valid source.")
        else:
            raise TypeError(f"Unknown data source: {data_src}")

    @property
    def dim(self):
        """Return the dimensions (rows x columns) of the relation"""
        return len(self), len(self.columns)

    @property
    def first(self):
        """Return the first record of the relation"""
        if len(self) == 0:
            raise ValueError("The relation is empty")
        return self.iloc[0].to_dict()

    def cleanup(self):
        """Remove empty (all NA) records from the relation"""
        return Relation(self.dropna(how="all"))

    def select(self, expr: str) -> "Relation":
        """Selection operation of the relational algebra

        :param expr: query string
        :return: a new relation
        """
        return Relation(super().query(expr).drop_duplicates())

    def project(self, attributes: list[str]) -> "Relation":
        """Projection operation of the relational algebra

        :param attributes: a list of attributes to extract
        :raises TypeError: if the argument is not a list
        :raises ValueError: if any attribute is not a valid column name
        :return: a new relation
        """
        if not isinstance(attributes, list):
            raise TypeError("Projection uses a list of attributes as an argument.")
        missing_attributes = set(attributes).difference(set(self.columns))
        if len(missing_attributes) > 0:
            raise ValueError(
                f"There are no attributes {', '.join(sorted(missing_attributes))} in this relation"
            )
        return Relation(self[attributes].drop_duplicates())

    def rename(self, old_name: str, new_name: str) -> "Relation":  # type: ignore
        """Rename operation of the relational algebra

        :param old_name: old name of an attribute
        :param new_name: new name of an attribute
        :return: a new relation
        """
        if old_name not in self.columns:
            raise ValueError(f"There is no attribute {old_name} in this relation")
        return Relation(super().rename(columns={old_name: new_name}).drop_duplicates())

    def sort(self, attributes: list[str], *args, **kwargs) -> "Relation":
        """Sorting operation of the relational algebra

        :param query: attributes to sort by
        :param ascending: default True
        :return: a new relation
        """
        return Relation(super().sort_values(attributes, *args, **kwargs))

    def extend(self, new_attribute: str, new_values: pd.Series) -> "Relation":
        """Extending operation of the relational algebra

        :param new_attribute: name of the new attribute
        :param new_values: series of values
        :return: a new relation
        """
        new_relation = Relation(self)
        new_relation[new_attribute] = new_values
        return new_relation.drop_duplicates()

    def groupby(self, attributes: list[str]) -> "RelationGroupBy":  # type: ignore
        """GroupBy operation of the relational algebra

        :param query: attributes to group by
        :return: a new relation group by object

        """
        return self.RelationGroupBy(super().groupby(attributes))

    class RelationGroupBy(pd.api.typing.DataFrameGroupBy):
        """An intermediate grouping object"""

        def __init__(self, grouping: pd.api.typing.DataFrameGroupBy):
            self.grouping = grouping

        def count(self, attribute: str):  # type: ignore
            """Compute count of group"""
            return Relation(
                self.grouping[attribute].count().to_frame(name=f"count_{attribute}").reset_index()
            )

        def sum(self, attribute: str):  # type: ignore
            """Compute sum of group values"""
            return Relation(
                self.grouping[attribute].sum().to_frame(name=f"sum_{attribute}").reset_index()
            )

        def min(self, attribute: str):  # type: ignore
            """Compute min of group values"""
            return Relation(
                self.grouping[attribute].min().to_frame(name=f"min_{attribute}").reset_index()
            )

        def max(self, attribute: str):  # type: ignore
            """Compute max of group values"""
            return Relation(
                self.grouping[attribute].max().to_frame(name=f"max_{attribute}").reset_index()
            )

        def avg(self, attribute: str):  # type: ignore
            """Compute average of group values"""
            return Relation(
                self.grouping[attribute].mean().to_frame(name=f"avg_{attribute}").reset_index()
            )

        def mean(self, attribute: str):  # type: ignore
            """Compute mean of group values"""
            return Relation(
                self.grouping[attribute].mean().to_frame(name=f"mean_{attribute}").reset_index()
            )

        def median(self, attribute: str):  # type: ignore
            """Compute median of group values"""
            return Relation(
                self.grouping[attribute].median().to_frame(name=f"median_{attribute}").reset_index()
            )

    def product(self, other: "Relation") -> "Relation":
        """Cartesian product operation of the relational algebra

        :param other: another relation
        :raises TypeError: if the argument is not a relation
        :return: a new relation
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only find a product of two relations.")
        if set(self.columns).intersection(set(other.columns)):
            raise ValueError(
                "Two relations must have disjoint attributes for cartesian product to work."
            )
        return Relation(self.merge(other, how="cross").drop_duplicates())

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
        return Relation(pd.concat([self, other]).drop_duplicates())

    def naturaljoin(self, other: "Relation") -> "Relation":  # type: ignore
        """Natural join operation of the relational algebra

        :param other: another relation
        :raises TypeError: if the argument is not a relation
        :raises ValueError: if there are no matching attributes
        :return: a new relation
        :alias: njoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        if not set(self.columns).intersection(set(other.columns)):
            raise ValueError("There are no common attributes between these relations to join them.")
        return Relation(self.merge(other, how="inner").drop_duplicates())

    njoin = naturaljoin

    def equijoin(self, other: "Relation", left_attrib, right_attrib) -> "Relation":  # type: ignore
        """Equijoin operation of the relational algebra

        :param other: another relation
        :param left_attrib: attribute in the left relation
        :param right_attrib: attribute in the right relation
        :raises TypeError: if the argument is not a relation
        :raises ValueError: if the provided left attribute is not found in the left relation
        :raises ValueError: if the provided right attribute is not found in the right relation
        :return: a new relation
        :alias: ejoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        if left_attrib not in self.columns:
            raise ValueError(f"There is no attribute {left_attrib} in the left relation.")
        if right_attrib not in other.columns:
            raise ValueError(f"There is no attribute {right_attrib} in the right relation.")
        return Relation(
            self.merge(
                other, how="inner", left_on=left_attrib, right_on=right_attrib
            ).drop_duplicates()
        )

    ejoin = equijoin

    def semijoin(self, other: "Relation", left_attrib, right_attrib) -> "Relation":  # type: ignore
        """Semijoin operation of the relational algebra

        :param other: another relation
        :param left_attrib: attribute in the left relation
        :param right_attrib: attribute in the right relation
        :raises TypeError: if the argument is not a relation
        :raises ValueError: if the provided left attribute is not found in the left relation
        :raises ValueError: if the provided right attribute is not found in the right relation
        :return: a new relation
        :alias: sjoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        if left_attrib not in self.columns:
            raise ValueError(f"There is no attribute {left_attrib} in the left relation.")
        if right_attrib not in other.columns:
            raise ValueError(f"There is no attribute {right_attrib} in the right relation.")
        return Relation(self[self[left_attrib].isin(other[right_attrib])].drop_duplicates())

    sjoin = semijoin

    def antijoin(self, other: "Relation", left_attrib, right_attrib) -> "Relation":  # type: ignore
        """Antijoin operation of the relational algebra

        :param other: another relation
        :param left_attrib: attribute in the left relation
        :param right_attrib: attribute in the right relation
        :raises TypeError: if the argument is not a relation
        :raises ValueError: if the provided left attribute is not found in the left relation
        :raises ValueError: if the provided right attribute is not found in the right relation
        :return: a new relation
        :alias: ajoin
        """
        if not isinstance(other, Relation):
            raise TypeError("Can only join two relations.")
        return Relation(self[~self[left_attrib].isin(other[right_attrib])].drop_duplicates())

    ajoin = antijoin

    def outerjoin(self, other: "Relation") -> "Relation":  # type: ignore
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
        return Relation(self.merge(other, how="outer").drop_duplicates())

    ojoin = outerjoin

    def minus(self, other):
        if not isinstance(other, Relation):
            raise TypeError("Can only find the difference of two relations.")
        return Relation(self[~self.isin(other)]).cleanup()

    def intersection(self, other):
        if not isinstance(other, Relation):
            raise TypeError("Can only find the intersection of two relations.")
        return Relation(self[self.isin(other)].cleanup())
