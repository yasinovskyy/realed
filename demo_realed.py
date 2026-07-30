#!/usr/bin/env python3
"""
Demonstration of relational algebra operations using realed

@author: Roman Yasinovskyy
@version: 2026.7
"""

from realed import Relation


def main():
    r1 = Relation("palmerpenguins.csv")
    r2 = Relation("palmerislands.csv")
    print(r1.naturaljoin(r2).project(["species", "island", "expedition"]))


if __name__ == "__main__":
    main()
