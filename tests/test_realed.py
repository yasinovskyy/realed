#!/usr/bin/env python3
"""
Testing the implementation of realed
"""

import pathlib
import unittest

import pandas as pd

from src.realed import Relation

penguins_data = pathlib.Path("data") / pathlib.Path("palmerpenguins.csv")
islands_data = pathlib.Path("data") / pathlib.Path("palmerislands.csv")


class TestRelationConstructor(unittest.TestCase):
    def test_init_str(self):
        """Create a relation from the filename as a string"""
        rel = Relation("data/palmerpenguins.csv")
        self.assertEqual(rel.dim, (344, 9))
        rel = Relation("data/palmerislands.csv")
        self.assertEqual(rel.dim, (6, 5))

    def test_init_path(self):
        """Create a relatyion from the filename as a Path"""
        rel = Relation(pathlib.Path("data") / pathlib.Path("palmerpenguins.csv"))
        self.assertEqual(rel.dim, (344, 9))
        rel = Relation(pathlib.Path("data") / pathlib.Path("palmerislands.csv"))
        self.assertEqual(rel.dim, (6, 5))

    def test_init_copy(self):
        """Create a relation from another relation"""
        rel_penguins = Relation(penguins_data)
        rel_penguins_copy = Relation(rel_penguins)
        self.assertEqual(rel_penguins_copy.dim, (344, 9))
        rel_islands = Relation(islands_data)
        rel_islands_copy = Relation(rel_islands)
        self.assertEqual(rel_islands_copy.dim, (6, 5))

    def test_init_dataframe(self):
        """Create a relation from a dataframe"""
        df_penguins = pd.read_csv(penguins_data)
        rel_penguins = Relation(df_penguins)
        self.assertEqual(rel_penguins.dim, (344, 9))
        df_islands = pd.read_csv(islands_data)
        rel_islands = Relation(df_islands)
        self.assertEqual(rel_islands.dim, (6, 5))

    def test_init_chunks(self):
        """Create a relation from multiplle chunks"""
        rel = Relation(penguins_data, chunksize=4)
        self.assertEqual(rel.dim, (344, 9))
        rel = Relation(islands_data, chunksize=4)
        self.assertEqual(rel.dim, (6, 5))

    @unittest.expectedFailure
    def test_init_error(self):
        Relation("unknown source")


class TestRelationOperations(unittest.TestCase):
    def test_equals(self):
        """Compare two relations for equality"""
        rel_penguins = Relation(penguins_data)
        rel_penguins_copy = Relation(rel_penguins)
        self.assertTrue(rel_penguins.equals(rel_penguins_copy))
        rel_islands = Relation(penguins_data)
        rel_islands_copy = Relation(rel_penguins)
        self.assertTrue(rel_islands.equals(rel_islands_copy))

    def test_one(self):
        """Retrieve a single record"""
        rel_penguins = Relation(penguins_data)
        self.assertTrue(
            rel_penguins.one
            == {
                "rowid": 1,
                "species": "Adelie",
                "island": "Torgersen",
                "bill_length_mm": 39.1,
                "bill_depth_mm": 18.7,
                "flipper_length_mm": 181,
                "body_mass_g": 3750,
                "sex": "male",
                "year": 2007,
            }
        )


class TestOperationSelect(unittest.TestCase):
    def test_select(self):
        rel = Relation(penguins_data)
        self.assertEqual(rel.select("species == 'Adelie'").dim, (152, 9))
        self.assertEqual(rel.select("species == 'Gentoo' and year == 2007").dim, (34, 9))
        self.assertEqual(rel.select("species == 'Gentoo'").select("year == 2007").dim, (34, 9))
        self.assertEqual(rel.select("island == 'Biscoe'").dim, (168, 9))
        self.assertEqual(rel.select("island == 'Dream' and body_mass_g > 4000").dim, (28, 9))
        self.assertEqual(rel.select("island == 'Dream'").select("body_mass_g > 4000").dim, (28, 9))

    @unittest.expectedFailure
    def test_select_error(self):
        rel = Relation(penguins_data)
        rel.select("continent == 'Antarctica'")


class TestOperationProject(unittest.TestCase):
    def test_project(self):
        rel = Relation(penguins_data)
        self.assertEqual(rel.project(["rowid"]).dim, (344, 1))
        self.assertEqual(rel.project(["species", "island"]).dim, (5, 2))
        self.assertEqual(rel.project(["species", "island", "sex"]).dim, (13, 3))

    @unittest.expectedFailure
    def test_project_error(self):
        rel = Relation(penguins_data)
        rel.project(["family"])


class TestOperationRename(unittest.TestCase):
    def test_rename(self):
        rel = Relation(penguins_data)
        self.assertTrue("location" in rel.rename("island", "location").columns)

    @unittest.expectedFailure
    def test_rename_error(self):
        rel = Relation(penguins_data)
        rel.rename("location", "place")


class TestOperationSort(unittest.TestCase):
    def test_sort(self):
        rel = Relation(penguins_data)
        self.assertEqual(rel.sort(["body_mass_g"]).dim, (344, 9))
        self.assertEqual(rel.sort(["body_mass_g"], ascending=False).sort(["species"]).dim, (344, 9))
        self.assertEqual(rel.sort(["body_mass_g"]).one["rowid"], 315)
        self.assertEqual(rel.sort(["body_mass_g"], ascending=False).one["rowid"], 170)

    @unittest.expectedFailure
    def test_sort_error(self):
        rel = Relation(penguins_data)
        rel.sort(["family"])


class TestOperationExtend(unittest.TestCase):
    def test_extend(self):
        rel = Relation(penguins_data)
        self.assertEqual(rel.extend("year_since_found", 2026 - rel["year"]).dim, (344, 10))


class TestOperationGroupBy(unittest.TestCase):
    def test_groupby(self):
        rel = Relation(penguins_data)
        self.assertEqual(rel.groupby(["species"]).count("rowid").dim, (3, 2))
        self.assertEqual(rel.groupby(["island"]).count("rowid").dim, (3, 2))
        self.assertEqual(rel.groupby(["species"]).sum("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["island"]).sum("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["species"]).min("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["island"]).min("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["species"]).max("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["island"]).max("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["species"]).mean("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["island"]).mean("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["species"]).median("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["island"]).median("body_mass_g").dim, (3, 2))
        self.assertEqual(rel.groupby(["island", "species"]).count("rowid").dim, (5, 3))


class TestOperationProduct(unittest.TestCase):
    def test_product(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        self.assertEqual(rel1.product(rel2.rename("island", "island_name")).dim, (2064, 14))
        self.assertEqual(rel2.product(rel1.rename("island", "island_name")).dim, (2064, 14))

    @unittest.expectedFailure
    def test_product_error(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        rel1.product(rel2)


class TestOperationUnion(unittest.TestCase):
    def test_union(self):
        rel1 = Relation(penguins_data).select("species == 'Adelie'")
        rel2 = Relation(penguins_data).select("species == 'Chinstrap'")
        rel3 = Relation(penguins_data).select("species == 'Gentoo'")
        self.assertEqual(rel1.union(rel2).dim, (220, 9))
        self.assertEqual(rel2.union(rel3).dim, (192, 9))
        self.assertEqual(rel3.union(rel1).dim, (276, 9))

    @unittest.expectedFailure
    def test_union_error(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        rel1.union(rel2)


class TestOperationNaturalJoin(unittest.TestCase):
    def test_njoin(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        self.assertEqual(rel1.njoin(rel2).dim, (344, 13))
        self.assertEqual(rel2.naturaljoin(rel1).dim, (344, 13))

    @unittest.expectedFailure
    def test_njoin_error(self):
        rel1 = Relation(penguins_data).project(["species"])
        rel2 = Relation(islands_data).project(["island"])
        rel1.njoin(rel2)


class TestOperationEquiJoin(unittest.TestCase):
    def test_ejoin(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data).rename("island", "location")
        self.assertEqual(rel1.ejoin(rel2, "island", "location").dim, (344, 14))
        self.assertEqual(rel2.equijoin(rel1, "location", "island").dim, (344, 14))

    @unittest.expectedFailure
    def test_ejoin_error(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        rel1.ejoin(rel2, "island", "location")


class TestOperationSemiJoin(unittest.TestCase):
    def test_sjoin(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        self.assertEqual(rel1.sjoin(rel2, "island", "island").dim, (344, 9))
        self.assertEqual(rel2.semijoin(rel1, "island", "island").dim, (3, 5))

    @unittest.expectedFailure
    def test_sjoin_error(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        rel1.sjoin(rel2, "island", "location")


class TestOperationAntiJoin(unittest.TestCase):
    def test_ajoin(self):
        rel1 = Relation(penguins_data).select("species == 'Gentoo'")
        rel2 = Relation(islands_data).select("island == 'Torgersen'")
        rel3 = Relation(islands_data)
        self.assertEqual(rel1.ajoin(rel2, "island", "island").dim, (124, 9))
        self.assertEqual(rel2.antijoin(rel1, "island", "island").dim, (1, 5))
        self.assertEqual(rel3.ajoin(rel1, "island", "island").dim, (5, 5))

    @unittest.expectedFailure
    def test_ajoin_error(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(islands_data)
        rel1.ajoin(rel2, "island", "location")


class TestOperationOuterJoin(unittest.TestCase):
    def test_ojoin(self):
        rel1 = Relation(penguins_data).select("species == 'Gentoo'")
        rel2 = Relation(islands_data).select("island == 'Torgersen'")
        rel3 = Relation(islands_data)
        self.assertEqual(rel1.ojoin(rel2).dim, (125, 13))
        self.assertEqual(rel2.outerjoin(rel1).dim, (125, 13))
        self.assertEqual(rel3.ojoin(rel1).dim, (129, 13))


class TestOperationMinus(unittest.TestCase):
    def test_minus(self):
        rel1 = Relation(penguins_data)
        rel2 = Relation(penguins_data).select("species == 'Adelie'")
        rel3 = Relation(penguins_data).select("species == 'Chinstrap'")
        rel4 = Relation(penguins_data).select("species == 'Gentoo'")
        self.assertEqual(rel1.minus(rel2).dim, (192, 9))
        self.assertEqual(rel1.minus(rel3).dim, (276, 9))
        self.assertEqual(rel1.minus(rel4).dim, (220, 9))


class TestOperationIntersection(unittest.TestCase):
    def test_intersection(self):
        rel1 = Relation(penguins_data).select("species == 'Adelie'")
        rel2 = Relation(penguins_data).select("island == 'Biscoe'")
        rel3 = Relation(penguins_data).select("island == 'Dream'")
        rel4 = Relation(penguins_data).select("island == 'Torgersen'")
        self.assertEqual(rel1.intersection(rel2).dim, (44, 9))
        self.assertEqual(rel1.intersection(rel3).dim, (56, 9))
        self.assertEqual(rel1.intersection(rel4).dim, (52, 9))


if __name__ == "__main__":
    unittest.main(verbosity=2)
