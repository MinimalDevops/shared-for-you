---
tags:
  - Database
  - SQL
---


# SQL Index or Indexing

**Indexes** are vital tools in [[../Databases|databases]], primarily used to speed up query performance by creating pointers to where data is stored. In MySQL, indexes serve three main purposes: finding rows quickly, sorting data efficiently, and reading data directly from the index without accessing the row data itself. MySQL primarily uses **BTREE indexes**, which are efficient for range queries but have limitations when dealing with interval ranges.

In SQL, there are two types of indexes: clustered and non-clustered. Clustered indexes, usually tied to the primary key, store data in the order of the key, optimizing searches on that key. Non-clustered indexes, on the other hand, create pointers to data in the main table, allowing for faster searches on non-primary key columns.

Indexes are especially beneficial for large databases, as they reduce the number of comparisons required to find data. However, they can also slow down write operations because the index must be updated with every change to the database. Proper indexing can dramatically enhance query performance, but it’s essential to carefully consider when and how to use them to avoid unnecessary overhead.

[How Indexing works](https://www.atlassian.com/data/sql/how-indexing-works)

{% if pdf == "true" %}
??? note "Checkout the PDF"

      ![PDF](pdf/atlassian.com-Indexing Essentials in SQL  Atlassian.pdf){ type=application/pdf style="min-height:100vh;width:100%" }
{% endif %}

[Three ways to use indexes](https://www.percona.com/blog/3-ways-mysql-uses-indexes/).

{% if pdf == "true" %}
??? note "Checkout the PDF"

      ![PDF](pdf/percona.com-3 ways MySQL uses indexes.pdf){ type=application/pdf style="min-height:100vh;width:100%" }
{% endif %}


