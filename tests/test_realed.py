#!/usr/bin/env python3
"""
Testing the implementation of realed
"""

import pathlib
import unittest

from src.realed import Relation

penguins_data = pathlib.Path("data") / pathlib.Path("palmerpenguins.csv")
islands_data = pathlib.Path("data") / pathlib.Path("palmerislands.csv")


class TestRelationConstructor(unittest.TestCase):
    def test_init(self):
        r = Relation(penguins_data)
        self.assertEqual(r.dim, (344, 9))

    @unittest.expectedFailure
    def test_init_error(self):
        Relation("unknown source")

    def test_init_copy(self):
        r1 = Relation(penguins_data)
        r2 = Relation(r1)
        self.assertTrue(r1.equals(r2))


class TestOperationSelect(unittest.TestCase):
    def test_select(self):
        r = Relation(penguins_data)
        self.assertEqual(r.select("species == 'Adelie'").dim, (152, 9))
        self.assertEqual(r.select("species == 'Gentoo' and year == 2007").dim, (34, 9))
        self.assertEqual(r.select("species == 'Gentoo'").select("year == 2007").dim, (34, 9))
        self.assertEqual(r.select("island == 'Biscoe'").dim, (168, 9))
        self.assertEqual(r.select("island == 'Dream' and body_mass_g > 4000").dim, (28, 9))
        self.assertEqual(r.select("island == 'Dream'").select("body_mass_g > 4000").dim, (28, 9))

    @unittest.expectedFailure
    def test_select_error(self):
        r = Relation(penguins_data)
        r.select("continent == 'Antarctica'")


class TestOperationProject(unittest.TestCase):
    def test_project(self):
        r = Relation(penguins_data)
        self.assertEqual(r.project(["rowid"]).dim, (344, 1))
        self.assertEqual(r.project(["species", "island"]).dim, (5, 2))
        self.assertEqual(r.project(["species", "island", "sex"]).dim, (13, 3))

    @unittest.expectedFailure
    def test_project_error(self):
        r = Relation(penguins_data)
        r.project(["family"])


class TestOperationRename(unittest.TestCase):
    def test_rename(self):
        r = Relation(penguins_data)
        self.assertTrue("location" in r.rename("island", "location").columns)

    @unittest.expectedFailure
    def test_rename_error(self):
        r = Relation(penguins_data)
        r.rename("location", "place")


class TestOperationSort(unittest.TestCase):
    def test_sort(self):
        r = Relation(penguins_data)
        self.assertEqual(r.sort(["body_mass_g"]).dim, (344, 9))
        self.assertEqual(r.sort(["body_mass_g"], ascending=False).sort(["species"]).dim, (344, 9))
        self.assertEqual(r.sort(["body_mass_g"]).one["rowid"], 315)
        self.assertEqual(r.sort(["body_mass_g"], ascending=False).one["rowid"], 170)

    @unittest.expectedFailure
    def test_sort_error(self):
        r = Relation(penguins_data)
        r.sort(["family"])


class TestOperationExtend(unittest.TestCase):
    def test_extend(self):
        r = Relation(penguins_data)
        self.assertEqual(r.extend("year_since_found", 2026 - r["year"]).dim, (344, 10))


class TestOperationGroupBy(unittest.TestCase):
    def test_groupby(self):
        r = Relation(penguins_data)
        self.assertEqual(r.groupby(["species"]).count("rowid").dim, (3, 2))
        self.assertEqual(r.groupby(["island"]).count("rowid").dim, (3, 2))
        self.assertEqual(r.groupby(["species"]).sum("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["island"]).sum("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["species"]).min("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["island"]).min("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["species"]).max("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["island"]).max("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["species"]).mean("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["island"]).mean("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["species"]).median("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["island"]).median("body_mass_g").dim, (3, 2))
        self.assertEqual(r.groupby(["island", "species"]).count("rowid").dim, (5, 3))


class TestOperationProduct(unittest.TestCase):
    def test_product(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        self.assertEqual(r1.product(r2.rename("island", "island_name")).dim, (2064, 14))
        self.assertEqual(r2.product(r1.rename("island", "island_name")).dim, (2064, 14))

    @unittest.expectedFailure
    def test_product_error(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        r1.product(r2)


class TestOperationUnion(unittest.TestCase):
    def test_union(self):
        r1 = Relation(penguins_data).select("species == 'Adelie'")
        r2 = Relation(penguins_data).select("species == 'Chinstrap'")
        r3 = Relation(penguins_data).select("species == 'Gentoo'")
        self.assertEqual(r1.union(r2).dim, (220, 9))
        self.assertEqual(r2.union(r3).dim, (192, 9))
        self.assertEqual(r3.union(r1).dim, (276, 9))

    @unittest.expectedFailure
    def test_union_error(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        r1.union(r2)


class TestOperationNaturalJoin(unittest.TestCase):
    def test_njoin(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        self.assertEqual(r1.njoin(r2).dim, (344, 13))
        self.assertEqual(r2.njoin(r1).dim, (344, 13))

    @unittest.expectedFailure
    def test_njoin_error(self):
        r1 = Relation(penguins_data).project(["species"])
        r2 = Relation(islands_data).project(["island"])
        r1.njoin(r2)


class TestOperationEquiJoin(unittest.TestCase):
    def test_ejoin(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data).rename("island", "location")
        self.assertEqual(r1.ejoin(r2, "island", "location").dim, (344, 14))
        self.assertEqual(r2.ejoin(r1, "location", "island").dim, (344, 14))

    @unittest.expectedFailure
    def test_ejoin_error(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        r1.ejoin(r2, "island", "location")


class TestOperationSemiJoin(unittest.TestCase):
    def test_sjoin(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        self.assertEqual(r1.sjoin(r2, "island", "island").dim, (344, 9))
        self.assertEqual(r2.sjoin(r1, "island", "island").dim, (3, 5))

    @unittest.expectedFailure
    def test_sjoin_error(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        r1.sjoin(r2, "island", "location")


class TestOperationAntiJoin(unittest.TestCase):
    def test_ajoin(self):
        r1 = Relation(penguins_data).select("species == 'Gentoo'")
        r2 = Relation(islands_data).select("island == 'Torgersen'")
        r3 = Relation(islands_data)
        self.assertEqual(r1.ajoin(r2, "island", "island").dim, (124, 9))
        self.assertEqual(r2.ajoin(r1, "island", "island").dim, (1, 5))
        self.assertEqual(r3.ajoin(r1, "island", "island").dim, (5, 5))

    @unittest.expectedFailure
    def test_ajoin_error(self):
        r1 = Relation(penguins_data)
        r2 = Relation(islands_data)
        r1.ajoin(r2, "island", "location")


class TestOperationOuterJoin(unittest.TestCase):
    def test_ojoin(self):
        r1 = Relation(penguins_data).select("species == 'Gentoo'")
        r2 = Relation(islands_data).select("island == 'Torgersen'")
        r3 = Relation(islands_data)
        self.assertEqual(r1.ojoin(r2).dim, (125, 13))
        self.assertEqual(r2.ojoin(r1).dim, (125, 13))
        self.assertEqual(r3.ojoin(r1).dim, (129, 13))


class TestOperationMinus(unittest.TestCase):
    def test_minus(self):
        r1 = Relation(penguins_data)
        r2 = Relation(penguins_data).select("species == 'Adelie'")
        r3 = Relation(penguins_data).select("species == 'Chinstrap'")
        r4 = Relation(penguins_data).select("species == 'Gentoo'")
        self.assertEqual(r1.minus(r2).dim, (192, 9))
        self.assertEqual(r1.minus(r3).dim, (276, 9))
        self.assertEqual(r1.minus(r4).dim, (220, 9))


class TestOperationIngtersection(unittest.TestCase):
    def test_intersection(self):
        r1 = Relation(penguins_data).select("species == 'Adelie'")
        r2 = Relation(penguins_data).select("island == 'Biscoe'")
        r3 = Relation(penguins_data).select("island == 'Dream'")
        r4 = Relation(penguins_data).select("island == 'Torgersen'")
        self.assertEqual(r1.intersection(r2).dim, (44, 9))
        self.assertEqual(r1.intersection(r3).dim, (56, 9))
        self.assertEqual(r1.intersection(r4).dim, (52, 9))


if __name__ == "__main__":
    unittest.main(verbosity=2)
