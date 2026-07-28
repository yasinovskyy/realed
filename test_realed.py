import unittest

from realed import Relation


class TestRelationConstructor(unittest.TestCase):
    def test_init(self):
        r = Relation("menagerie.csv")
        self.assertEqual(r.dim, (10, 5))


class TestRelationCopyConstructor(unittest.TestCase):
    def test_init(self):
        r = Relation("menagerie.csv")
        r2 = Relation(r)
        self.assertEqual(r2.dim, (10, 5))


class TestOperationProject(unittest.TestCase):
    def test_project(self):
        r = Relation("menagerie.csv")
        self.assertEqual(r.project(["name"]).dim, (10, 1))
        self.assertEqual(r.project(["name", "age"]).dim, (10, 2))
        self.assertEqual(r.project(["id", "age", "species"]).dim, (10, 3))

    @unittest.expectedFailure
    def test_project_error(self):
        r = Relation("menagerie.csv")
        r.project(["family"])


class TestOperationSelect(unittest.TestCase):
    def test_select(self):
        r = Relation("menagerie.csv")
        self.assertEqual(r.select("age > 50").dim, (3, 5))
        self.assertEqual(r.select("location == 'Basement' and age > 50").dim, (2, 5))
        self.assertEqual(r.query("species == 'Newt' and age < 50").dim, (1, 5))

    @unittest.expectedFailure
    def test_select_error(self):
        r = Relation("menagerie.csv")
        r.select("family == rodent")


class TestOperationRename(unittest.TestCase):
    def test_rename(self):
        r = Relation("menagerie.csv")
        self.assertEqual(r.rename("location", "place").dim, (10, 5))

    @unittest.expectedFailure
    def test_rename_error(self):
        r = Relation("menagerie.csv")
        r.rename("family", "species")


class TestOperationSort(unittest.TestCase):
    def test_sort(self):
        r = Relation("menagerie.csv")
        self.assertEqual(r.sort(["age"]).dim, (10, 5))
        self.assertEqual(r.sort(["age"], ascending=False).sort(["location"]).dim, (10, 5))

    @unittest.expectedFailure
    def test_sort_error(self):
        r = Relation("menagerie.csv")
        r.sort(["family"])


class TestOperationExtend(unittest.TestCase):
    def test_extend(self):
        r = Relation("menagerie.csv")
        self.assertEqual(r.extend("yob", 2026 - r.age).dim, (10, 6))


class TestOperationGroupBy(unittest.TestCase):
    def test_groupby(self):
        r = Relation("menagerie.csv")
        self.assertEqual(r.groupby(["species"]).count("id").dim, (7, 2))
        self.assertEqual(r.groupby(["location"]).count("id").dim, (4, 2))
        self.assertEqual(r.groupby(["species"]).sum("age").dim, (7, 2))
        self.assertEqual(r.groupby(["location"]).sum("age").dim, (4, 2))
        self.assertEqual(r.groupby(["species"]).min("age").dim, (7, 2))
        self.assertEqual(r.groupby(["location"]).min("age").dim, (4, 2))
        self.assertEqual(r.groupby(["species"]).max("age").dim, (7, 2))
        self.assertEqual(r.groupby(["location"]).max("age").dim, (4, 2))
        self.assertEqual(r.groupby(["species"]).mean("age").dim, (7, 2))
        self.assertEqual(r.groupby(["location"]).mean("age").dim, (4, 2))
        self.assertEqual(r.groupby(["species"]).median("age").dim, (7, 2))
        self.assertEqual(r.groupby(["location"]).median("age").dim, (4, 2))
        self.assertEqual(r.groupby(["location", "species"]).count("name").dim, (8, 3))


if __name__ == "__main__":
    unittest.main()
