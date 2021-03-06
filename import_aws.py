import sys
import common
from import_base import BaseImporter
import datetime


# This implementation is incomplete:
# TODO: validate implementation with test data
# TODO: verify protocol is TCP
# TODO: parse timestamp into dictionary['Timestamp']


class AWSImporter(BaseImporter):
    def translate(self, line, line_num, dictionary):
        """
        Converts a given syslog line into a dictionary of (ip, port, ip, port)
        Args:
            line: The syslog line to parse
            line_num: The line number, for error printouts
            dictionary: The dictionary to write key/values pairs into

        Returns:
            0 on success and non-zero on error.
        """
        awsLog = line.split(" ")

        dictionary['src'] = common.IPtoInt(*(awsLog[3].split(".")))
        dictionary['srcport'] = awsLog[5]
        dictionary['dst'] = common.IPtoInt(*(awsLog[4].split(".")))
        dictionary['dstport'] = awsLog[6]
        dictionary['timestamp'] = datetime.datetime.fromtimestamp((int(awsLog[10]))).strftime(self.mysql_time_format)
        dictionary['protocol'] = 'TCP'.upper()
        dictionary['duration'] = '1'
        dictionary['bytes_received'] = '1'
        dictionary['bytes_sent'] = '1'
        dictionary['packets_received'] = '1'
        dictionary['packets_sent'] = '1'
        return 0


# If running as a script, begin by executing main.
if __name__ == "__main__":
    importer = AWSImporter()
    importer.main(sys.argv)
