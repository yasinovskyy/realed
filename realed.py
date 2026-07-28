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
            raise ValueError("A relation must be created from a valid source.")
        else:
            raise TypeError(f"Unknown data source: {data_src}")

    @property
    def dim(self):
        """Return the dimensions (rows x columns) of the relation"""
        return len(self), len(self.columns)

    def query(self, expr: str) -> "Relation":  # type: ignore
        """Selection operation of the relational algebra

        :param expr: query string
        :return: a new relation
        """
        return Relation(super().query(expr).drop_duplicates())

    def select(self, expr: str) -> "Relation":
        """Selection operation of the relational algebra

        :param expr: query string
        :return: a new relation
        """
        return self.query(expr)

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


def main():
    r = Relation("palmerpenguins.csv")
    print(r)


if __name__ == "__main__":
    main()
