import csv
import random
import string
from datetime import datetime
from pathlib import Path

class PseudoCodes:

    F_SEP = '\t'
    V_SEP = ';'
    OUTFILE = 'pseudocodes_{timestamp}{suffix}.tsv'

    @staticmethod
    def get_pseudocoded_file_list(files, filecode_list=None, code_length=4, include_date=True):

        pseudo = []

        if filecode_list:
            to_be_processed = []
            for file in files:
                f_name = Path(file).name
                if f_name in filecode_list:
                    pseudo.append({
                        'input_file': filecode_list[f_name][1],
                        'pseudocode': filecode_list[f_name][0]
                    })
                else:
                    to_be_processed.append(file)
        else:
            to_be_processed = files

        for file in to_be_processed:
            while True:
                p = ''.join([random.choice(string.ascii_letters[26:]) for x in range(code_length)])
                if p not in [x['pseudocode'] for x in pseudo]:
                    pseudo.append({'input_file': file, 'pseudocode': p})
                    break

        return pseudo

    def read_pseudocoded_file_list(self, file):
        if not file:
            return {}

        reader = csv.DictReader(open(file), delimiter=self.F_SEP)
        p_list = {}
        for item in [x for x in reader]:
            for file in item['saved_files'].split(self.V_SEP):
                p_list[Path(file).name] = (item['pseudocode'], file)

        return p_list

    def get_pseudocode_filename(self, do_not_share_dir, suffix=''):
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

            
