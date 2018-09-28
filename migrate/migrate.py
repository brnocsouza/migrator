import os
import sys
import typing
import psycopg2
from psycopg2.extras import DictCursor

import migrate.helpers.config as config
from migrate.exception.Exception import NoDataBaseFinded
from migrate.models.DatabaseConfig import DatabaseConfig


class Migrate:
    def __enter__(self):
        self.__conn = psycopg2.connect(
            host=self.db['host'],
            database=self.db['database'],
            port=self.db['port'],
            user=self.db['user'],
            password=self.db['password']
        )

        return self

    def __exit__(self, type, value, traceback):
        if self.dev:
            print('Deleted with params')
            print(type)
            print(value)
            print(traceback)

        if self.__conn and self.__conn.closed == 0:
            self.__conn.close()

    def __init__(self, table, dev=False):
        """
        Creates new connection to DB
        based on env.ini
        """
        parser = config.Config()

        self.table = table
        self.references = {}
        self.relations: typing.Dict[str, dict] = {}
        self.queryList = []
        self.alterList = []
        self.exec_query = False
        self.dev = dev

        self.db: DatabaseConfig = parser.item(section='database')

        if self.db is None:
            raise NoDataBaseFinded()

    def exec_in_db(self, exec_query_in_db=False):
        self.exec_query = exec_query_in_db

        return self

    def create_column(self, relations: typing.Dict[str, dict]):
        self.relations = relations

        if len(self.relations.keys()) > 0:
            with self.__conn.cursor() as cur:
                for key in self.relations:
                    column = self.relations[key]['relations'][1]

                    query = (
                        '''
                            ALTER TABLE {table} DROP COLUMN IF EXISTS {column}; 
                            ALTER TABLE {table} ADD {column} BIGINT NULL;
                        '''.format(
                            table=self.table,
                            column=column
                        )
                    )

                    if self.dev:
                        print(f"CREATE COLUMN {column}")
                        print(query)

                    if self.exec_query:
                        cur.execute(query)
                        self.__conn.commit()
                    else:
                        self.alterList.append(query)

        return self

    def prepare(self):
        if len(self.relations.keys()) > 0:
            cur = self.__conn.cursor(cursor_factory=DictCursor)

            columns = []
            joins = []
            for table in self.relations:
                val = self.relations[table]
                columns.append("{table}.{primary} AS {asKey}".format(table=table, primary=val['primary'],
                                                                     asKey=val['relations'][1]))

                joins.append("LEFT JOIN {fTable} ON {fTable}.{fk} = {table}.{key}".format(
                    fTable=table,
                    fk=val['references'][1],
                    table=self.table,
                    key=val['relations'][0]
                )
                )

            begin = "SELECT {table}.id, ".format(table=self.table)
            end = "FROM {table}".format(table=self.table)

            sql = " ".join([begin, ", ".join(columns), end, " ".join(joins)])

            if self.dev:
                print(f"SELECT REFS")
                print(sql)

            cur.execute(sql)

            for row in cur.fetchall():
                columns_update = []

                for table, value in self.relations.items():
                    relation = value['relations'][1]
                    column = "{} = {}".format(relation, self._prepare_column(row[relation]))
                    columns_update.append(column)

                if len(columns_update) > 0:
                    query = "UPDATE {table} SET {updates} WHERE id = {id};".format(
                        table=self.table,
                        updates=", ".join(columns_update),
                        id=row[0]
                    )
                    self.queryList.append(query)

        return self

    def create_foreign_key(self):
        if len(self.relations.keys()) > 0:
            for key in self.relations:
                query = 'ALTER TABLE {table} ADD CONSTRAINT {table}_{fk_key}_fk FOREIGN KEY ({fk_key}) REFERENCES {fk_table} ({pk_key});'.format(
                    table=self.table,
                    fk_key=self.relations[key]['relations'][0],
                    fk_table=key,
                    pk_key=self.relations[key]['primary'],
                )

                if self.dev:
                    print('CREATE FK')
                    print(query)

                self.alterList.append(query)

        return self

    def remove_column(self):
        query = 'ALTER TABLE {table} DROP _id;'.format(table=self.table, )

        if self.dev:
            print('REMOVE _id')
            print(query)

        self.alterList.append(query)

        if len(self.relations.keys()) > 0:
            for key in self.relations:
                query = 'ALTER TABLE {table} DROP {column};'.format(
                    table=self.table,
                    column=self.relations[key]['relations'][0]
                )

                self.alterList.append(query)

                if self.dev:
                    print('DROP TEMP COLUMNS')
                    print(query)

                query = 'ALTER TABLE {table} RENAME COLUMN {column_before} TO {column_after};'.format(
                    table=self.table,
                    column_before=self.relations[key]['relations'][1],
                    column_after=self.relations[key]['relations'][0]
                )

                if self.dev:
                    print('RENAME COLUMNS')
                    print(query)

                self.alterList.append(query)

        return self

    def write(self, folder_name=None):
        if folder_name is None:
            folder_name = "."
        else:
            if folder_name.endswith('/'):
                folder_name = folder_name[:-1]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        if not os.path.exists(folder_name + os.altsep + 'updates'):
            os.makedirs(folder_name + os.altsep + 'updates')

        if not os.path.exists(folder_name + os.altsep + 'alters'):
            os.makedirs(folder_name + os.altsep + 'alters')

        if len(self.queryList) > 0:
            name = "{}/updates/{}-updates.sql".format(folder_name, self.table)
            with open(name, 'w') as file:
                file.write('\n'.join(self.queryList))

        if len(self.alterList) > 0:
            name = "{}/alters/{}-alters.sql".format(folder_name, self.table)
            with open(name, 'w') as file:
                file.write('\n'.join(self.alterList))

        sys.stdout.write(
            "Task {} ended with file {}{}-*.sql{}".format(self.table, folder_name + os.altsep, self.table, os.linesep))
        sys.stdout.flush()

    def exec(self):
        for query in self.queryList:
            cur = self.__conn.cursor()
            cur.execute(query)

        for query in self.alterList:
            cur = self.__conn.cursor()
            cur.execute(query)

        sys.stdout.write("Task {} ended with {} imports {}".format(self.table, len(self.queryList), os.linesep))
        sys.stdout.flush()

        return self

    def _prepare_column(self, key):
        if key is None:
            return 'NULL'

        return key
