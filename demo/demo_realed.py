#!/usr/bin/env python3
"""
Demonstration of relational algebra operations using realed
"""

from realed import Relation


def main():
    r1 = Relation("data/palmerpenguins.csv")
    r2 = Relation("data/palmerislands.csv")
    print(r1.naturaljoin(r2).project(["species", "island", "expedition"]))


if __name__ == "__main__":
    main()
