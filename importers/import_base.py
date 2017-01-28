import sys
import os
dbaccess = None
common = None

class BaseImporter:
    mysql_time_format = '%Y-%m-%d %H:%M:%S'
    keys = [
        "src",
        "srcport",
        "dst",
        "dstport",
        "timestamp",
        "protocol",
        "bytes_sent",
        "bytes_received",
        "packets_sent",
        "packets_received",
        "duration",
    ]

    def __init__(self):
        self.instructions = """
This program imports a syslog dump into the database.
It extracts IP addresses and ports and discards other data. Only TCP traffic data is used.
Optionally, include the name of the datasource to import in to. Default uses currently selected data source.

Usage:
    python {0} <input-file> <data source>

""".format(sys.argv[0])
        self.datasource = None
        self.settings = None
        self.ds = None

    @staticmethod
    def ip_to_int(a, b, c, d):
        """
        Converts a number from a sequence of dotted decimals into a single unsigned int.
        Args:
            a: IP address segment 1 ###.0.0.0
            b: IP address segment 2 0.###.0.0
            c: IP address segment 3 0.0.###.0
            d: IP address segment 4 0.0.0.###

        Returns: The IP address as a simple 32-bit unsigned integer

        """
        return (int(a) << 24) + (int(b) << 16) + (int(c) << 8) + int(d)

    def main(self, argv):
        if not (1 < len(argv) < 4):
            print(self.instructions)
            return

        try:
            self.datasource = self.determine_datasource(argv)
        except ValueError:
            print(self.instructions)
            return

        if self.validate_file(argv[1]):
            self.import_file(argv[1])
        else:
            print(self.instructions)
            return

    @staticmethod
    def determine_datasource(argv):
        if len(argv) >= 3 and len(argv[2]) > 1:
            requested_ds = argv[2]
        else:
            raise ValueError("Cannot determine datasource. Argv is {0}".format(repr(argv)))

        return requested_ds

    @staticmethod
    def validate_file(path):
        """
        Check whether a given path is a file.
        Args:
            path: The path to verify is a file

        Returns:
            True or False
        """
        if os.path.isfile(path):
            return True
        else:
            print("File not found: {0}".format(path))
            return False

    def translate(self, line, line_num, dictionary):
        """
        Converts a given syslog line into a dictionary of (ip, port, ip, port, timestamp)
        Args:
            line: The syslog line to parse
            line_num: The line number, for error printouts
            dictionary: The dictionary to write key/values pairs into

        Returns:
            0 on success and non-zero on error.
        """
        return 1

    def import_string(self, s):
        """
        Takes a string containing one or more lines and attempts to import it into the database staging table.
        Args:
            s: One or more syslog lines

        Returns:
            None
        """
        all_lines = s.splitlines()
        line_num = 0
        lines_inserted = 0
        counter = 0
        rows = [dict.fromkeys(self.keys, '') for _ in range(1000)]
        for line in all_lines:
            line_num += 1

            if self.translate(line, line_num, rows[counter]) != 0:
                continue

            counter += 1

            # Perform the actual insertion in batches of 1000
            if counter == 1000:
                self.insert_data(rows, counter)
                lines_inserted += counter
                counter = 0
        if counter != 0:
            self.insert_data(rows, counter)
            lines_inserted += counter
        print("Done. {0} lines processed, {1} rows inserted".format(line_num, lines_inserted))
        return lines_inserted

    def import_file(self, path_in):
        """
        Takes a file path and attempts to import it into the database staging table.
        Args:
            path_in: The path to a log file to read/import

        Returns:
            None
        """
        with open(path_in) as fin:
            line_num = 0
            lines_inserted = 0
            counter = 0
            rows = [dict.fromkeys(self.keys, '') for _ in range(1000)]
            for line in fin:
                line_num += 1

                if self.translate(line, line_num, rows[counter]) != 0:
                    continue

                counter += 1

                # Perform the actual insertion in batches of 1000
                if counter == 1000:
                    self.insert_data(rows, counter)
                    lines_inserted += counter
                    counter = 0
        if counter != 0:
            self.insert_data(rows, counter)
            lines_inserted += counter
        print("Done. {0} lines processed, {1} rows inserted".format(line_num, lines_inserted))
        return lines_inserted

    def insert_data(self, rows, count):
        """
        Attempt to insert the first 'count' items in 'rows' into the database table `samapper`.`Syslog`.
        Exits script on critical failure.
        Args:
            rows: The iterable containing dictionaries to insert
                (dictionaries must all have the same keys, matching column names)
            count: The number of items from rows to insert

        Returns:
            None
        """
        if self.datasource is None:
            raise ValueError("No data source specified. Import aborted.")

        global dbaccess
        global common
        if not self.ds:
            try:
                import dbaccess
                import common
                self.settings = dbaccess.get_settings(all=True)
                for datasource in self.settings['datasources']:
                    if datasource['name'] == self.datasource:
                        self.ds = datasource['id']
                        break
                    if datasource['id'] == self.datasource:
                        self.ds = datasource['id']
                        break
                if self.ds == None:
                    raise ValueError()
            except ValueError:
                print("No data source matches name {0}.".format(self.datasource))
                if self.settings:
                    print("Data sources include: {0}".format(repr([ds['name'] for ds in self.settings['datasources']])))
                sys.exit(5)
            except:
                print("Cannot connect to database.")
                sys.exit(4)

        table_name = "ds_{ds}_Syslog".format(ds=self.ds)

        try:
            truncated_rows = rows[:count]
            if count > 0 and len(rows[0].keys()) != len(self.keys):
                print("Database key length doesn't match. Check that your importer's translate function "
                      "fills all the dictionary keys in import_base.keys exactly.")
                print("Expected keys: {0}".format(repr(self.keys)))
                print("Received keys: {0}".format(repr(rows[0].keys())))
                sys.exit(3)

            # >>> values = [{"name": "foo", "email": "foo@example.com"}, {"name": "bar", "email": "bar@example.com"}]
            # >>> db.multiple_insert('person', values=values, _test=True)
            common.db_quiet.multiple_insert(table_name, values=truncated_rows)
        except Exception as e:
            print("Error inserting into database:")
            print("\t{0}".format(e))
            import integrity
            if integrity.check_and_fix_db_access() == 0:
                print("Resuming...")
                self.insert_data(rows, count)
            else:
                print("Critical failure. Aborting.")
                sys.exit(2)


_class = BaseImporter