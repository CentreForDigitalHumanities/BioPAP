import csv
import random
import re
import string
from datetime import datetime
from pathlib import Path
from biopap.modules.helpers import (get_logger)

logger = get_logger()

class PseudoCodes:

    F_SEP = '\t'
    V_SEP = ';'
    OUTFILE = 'pseudocodes_{timestamp}{suffix}.tsv'
    REGEX_MATCH = '^_[A-Z]{{{code_length}}}$'

    @staticmethod
    def generate_pseudocode(code_length):
        return ''.join([random.choice(string.ascii_letters[26:]) for x in range(code_length)])

    def get_pseudocoded_file_list(self, files, code_length=4):

        p_regex = re.compile(self.REGEX_MATCH.format(code_length=code_length))
        p_files = []

        for file in files:
            postfix = Path(file).stem[-code_length:]

            if p_regex.match('_' + postfix):
                p_code = postfix
                logger.info(f"'{Path(file).name}': using implied pseudocode {p_code}")
            else:
                p_code = self.generate_pseudocode(code_length=code_length)
                logger.warning(f"'{Path(file).name}': using new pseudocode {p_code}")

            p_files.append({
                'input_file': file,
                'pseudocode': p_code
            })

        return p_files

    def get_pseudocodes_filepath(self, do_not_share_dir, suffix=''):
        while True:
            ts = datetime.strftime(datetime.now(), '%Y%m%d-%H%M%S')
            new_pseudocode_file = do_not_share_dir / self.OUTFILE.format(timestamp=ts, suffix=suffix)
            if not new_pseudocode_file.exists():
                break

        return new_pseudocode_file

    def write_pseudocode_file(self, results, file):
        with open(file, 'w+') as f:
            f.write(f"{self.F_SEP.join(['input_file', 'pseudocode', 'saved_files', 'exit_code'])}\n")
            for result in results:
                fields = [
                    result['input_file'],
                    result['pseudocode'],
                    self.V_SEP.join(map(str, result['saved_files'])),
                    self.V_SEP.join(map(str, result['exit_code']))]
                f.write(f"{self.F_SEP.join(fields)}\n")

            
