import unittest

from realed import Relation


class TestRelationConstructor(unittest.TestCase):
    def test_init(self):
        r = Relation("palmerpenguins.csv")
        self.assertEqual(r.dim, (344, 9))


class TestRelationCopyConstructor(unittest.TestCase):
    def test_init(self):
        r = Relation("palmerpenguins.csv")
        r2 = Relation(r)
        self.assertEqual(r2.dim, (344, 9))


class TestOperationSelect(unittest.TestCase):
    def test_select(self):
        r = Relation("palmerpenguins.csv")
        self.assertEqual(r.select("species == 'Adelie'").dim, (152, 9))
        self.assertEqual(r.select("species == 'Gentoo' and year == 2007").dim, (34, 9))
        self.assertEqual(r.select("species == 'Gentoo'").select("year == 2007").dim, (34, 9))

    def test_query(self):
        r = Relation("palmerpenguins.csv")
        self.assertEqual(r.query("island == 'Biscoe'").dim, (168, 9))
        self.assertEqual(r.query("island == 'Dream' and body_mass_g > 4000").dim, (28, 9))
        self.assertEqual(r.query("island == 'Dream'").select("body_mass_g > 4000").dim, (28, 9))

    @unittest.expectedFailure
    def test_select_error(self):
        r = Relation("palmerpenguins.csv")
        r.select("continent == 'Antarctica'")

    @unittest.expectedFailure
    def test_query_error(self):
        r = Relation("palmerpenguins.csv")
        r.query("family == 'Penguin'")


class TestOperationProject(unittest.TestCase):
    def test_project(self):
        r = Relation("palmerpenguins.csv")
        self.assertEqual(r.project(["rowid"]).dim, (344, 1))
        self.assertEqual(r.project(["species", "island"]).dim, (5, 2))
        self.assertEqual(r.project(["species", "island", "sex"]).dim, (13, 3))

    @unittest.expectedFailure
    def test_project_error(self):
        r = Relation("palmerpenguins.csv")
        r.project(["family"])


class TestOperationRename(unittest.TestCase):
    def test_rename(self):
        r = Relation("palmerpenguins.csv")
        self.assertTrue("location" in r.rename("island", "location").columns)

    @unittest.expectedFailure
    def test_rename_error(self):
        r = Relation("palmerpenguins.csv")
        r.rename("location", "place")


class TestOperationSort(unittest.TestCase):
    def test_sort(self):
        r = Relation("palmerpenguins.csv")
        self.assertEqual(r.sort(["body_mass_g"]).dim, (344, 9))
        self.assertEqual(r.sort(["body_mass_g"], ascending=False).sort(["species"]).dim, (344, 9))

    @unittest.expectedFailure
    def test_sort_error(self):
        r = Relation("palmerpenguins.csv")
        r.sort(["family"])


class TestOperationExtend(unittest.TestCase):
    def test_extend(self):
        r = Relation("palmerpenguins.csv")
        self.assertEqual(r.extend("year_since_found", 2026 - r.year).dim, (344, 10))


class TestOperationGroupBy(unittest.TestCase):
    def test_groupby(self):
        r = Relation("palmerpenguins.csv")
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
