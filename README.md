# *ReAlEd*: Relational Algebra for Education

A simple wrapper around `pandas` to demonstrate common relation algebra operations:

- projection
- selection
- renaming
- sorting
- grouping
- joining relations

## Initialization

```python
>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r
   id                name  age               species   location
0   1               Chunk   34                Jaguar      Attic
1   2                Wind   99                  Newt   Basement
2   3  Underrated Thunder   74      Macaroni Penguin   Basement
3   4                 Axe   23        Long-Eared Owl     Garage
4   5        Wild Isotope   28      Humboldt Penguin      Attic
5   6          Night Star   26                  Newt     Garage
6   7        Random Bully   52             Armadillo  Back yard
7   8        Cunning Fury   38  Pink Fairy Armadillo  Back yard
8   9       Evening Chunk   50                  Newt   Basement
9  10             Thunder   38                Jaguar      Attic
>>>
```

## Selection

Both `select` and `query` filter records by some criteria.

```python
>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r.select("name == 'Wild Isotope'")
   id          name  age           species location
4   5  Wild Isotope   28  Humboldt Penguin    Attic
>>>
```

```python
>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r.query("name == 'Underrated Thunder'")
   id                name  age           species  location
2   3  Underrated Thunder   74  Macaroni Penguin  Basement
>>>
```

## Projection

```python
>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r.project(["name", "species"]).head(3)
                 name           species
0               Chunk            Jaguar
1                Wind              Newt
2  Underrated Thunder  Macaroni Penguin
>>>
```

## Renaming

```python

>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r.rename("location", "place").project(["name", "place"]).head(3)
                 name     place
0               Chunk     Attic
1                Wind  Basement
2  Underrated Thunder  Basement
>>>
```

## Sorting

```python
>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r.sort(["location"]).head(3)
   id          name  age           species location
0   1         Chunk   34            Jaguar    Attic
4   5  Wild Isotope   28  Humboldt Penguin    Attic
9  10       Thunder   38            Jaguar    Attic
>>>
```

## Extending

```python
>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r.extend("yob", 2026-r.age).head(3)
   id                name  age           species  location   yob
0   1               Chunk   34            Jaguar     Attic  1992
1   2                Wind   99              Newt  Basement  1927
2   3  Underrated Thunder   74  Macaroni Penguin  Basement  1952
>>>
```

## Grouping and aggregation

```python
>>> from realed import Relation
>>> r = Relation("menagerie.csv")
>>> r.groupby(["species"]).count("id")
                species  count_id
0             Armadillo         1
1      Humboldt Penguin         1
2                Jaguar         2
3        Long-Eared Owl         1
4      Macaroni Penguin         1
5                  Newt         3
6  Pink Fairy Armadillo         1
>>> r.groupby(["location"]).count("id")
    location  count_id
0      Attic         3
1  Back yard         2
2   Basement         3
3     Garage         2
>>> r.groupby(["location"]).sum("age")
    location  sum_age
0      Attic      100
1  Back yard       90
2   Basement      223
3     Garage       49
>>> r.groupby(["location"]).min("age")
    location  min_age
0      Attic       28
1  Back yard       38
2   Basement       50
3     Garage       23
>>> r.groupby(["location"]).max("age")
    location  max_age
0      Attic       38
1  Back yard       52
2   Basement       99
3     Garage       26
>>> r.groupby(["location"]).mean("age")
    location   mean_age
0      Attic  33.333333
1  Back yard  45.000000
2   Basement  74.333333
3     Garage  24.500000
>>> r.groupby(["location"]).median("age")
    location  median_age
0      Attic        34.0
1  Back yard        45.0
2   Basement        74.0
3     Garage        24.5
>>> r.groupby(["location", "species"]).count("name")
    location               species  count_name
0      Attic      Humboldt Penguin           1
1      Attic                Jaguar           2
2  Back yard             Armadillo           1
3  Back yard  Pink Fairy Armadillo           1
4   Basement      Macaroni Penguin           1
5   Basement                  Newt           2
6     Garage        Long-Eared Owl           1
7     Garage                  Newt           1
```
