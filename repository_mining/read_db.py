import argparse
import unqlite
import glob2
import os
import csv
import sys
import operator
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + \
                '/../fault_cardinality_classifier/')
import classifier

def div(a, b):
    return a / b if b != 0.0 else 0

def avg(lst):
    return div(sum(lst), len(lst))

def search_dbs(base_path='../database'):
    for dbpath in glob2.glob(base_path+'/*.db'):
        yield dbpath

def write_fix(csvwriter, url, fix):
    obj = {'URL': url,
           'Buggy_sha1': fix['faulty'],
           'Fixing_sha1': fix['fixing'],
           'Classification': fix['classification'],
           'Same_Tests': fix['same-tests']}

    spectrum = classifier.Spectrum()
    spectrum.read_string(fix['spectrum'])
    mhs = fix['mhs']
    heuristics = [('Ochiai',    classifier.ochiai),
                  ('Naish',     classifier.naish),
                  ('O',         classifier.o),
                  ('Tarantula', classifier.tarantula),
                  ('DStar2',    classifier.dstar(2))]

    ranker = classifier.SimilarityRanker()
    ranks = ranker.rank_multiple(spectrum, [x[1] for x in heuristics])
    for i, rank in enumerate(ranks):
        name = heuristics[i][0]
        for candidate in mhs:
            temp = [classifier.normalized_cd(rank, component) for component in candidate]
            efforts = [x[0] for x in temp]
            heuristic_values = [x[1] for x in temp]
            for suffix, e_f, v_f in [("_Best", min, max), ("_Avg", avg, avg), ("_Worst", max, min)]:
                qualified_name = name+suffix+"_cd"
                value = e_f(efforts)
                h_value = v_f(heuristic_values)
                if qualified_name in obj and obj[qualified_name] < value:
                    break
                else:
                    obj[qualified_name] = value
                    obj[name+suffix] = h_value

    spectrum_filter = classifier.SpectrumFilter(spectrum)
    spectrum_filter.components_filter = mhs[0]
    collapsed_scores = ranker.collapsed_score(spectrum, spectrum_filter, [x[1] for x in heuristics])
    for i, score in enumerate(collapsed_scores):
        obj[heuristics[i][0]+'_Collapsed'] = score
        obj[heuristics[i][0]+'_Collapsed_cd'] = classifier.normalized_cd_from_score(rank, score)
    obj['Failing_Coverage'] = spectrum.get_failing_transactions_coverage()

    csvwriter.writerow(obj)

def read_db(dbpath, csvwriter_fixes):
    print("DB: ", dbpath)
    if not os.path.exists(dbpath):
        print("File {} not found.".format(dbpath))
        return
    db = unqlite.UnQLite(dbpath)
    if 'URL' not in db:
        return
    try:
        url = db['URL']
        commits_collection = db.collection('commits')
        if commits_collection.exists():
            all_commits = len(commits_collection)
            classifications = {}
            regressions = {}
            all_fixes = 0
            if all_commits:
                fixes_collection = db.collection('fixes')
                if fixes_collection.exists():
                    for fix_id in range(len(fixes_collection)):
                        fix = fixes_collection.fetch(fix_id)
                        if fix['classification'] != 'not-a-fix':
                            write_fix(csvwriter_fixes, url, fix)

    except Exception as e:
        print("Could not read from database:", e)
        pass

if __name__ == '__main__':
    fieldnames_fixes = ['URL','Buggy_sha1','Fixing_sha1',
                        'Classification', 'Same_Tests',
                        'Ochiai_Best_cd','Ochiai_Avg_cd','Ochiai_Worst_cd',
                        'DStar2_Best_cd','DStar2_Avg_cd','DStar2_Worst_cd',
                        'Naish_Best_cd','Naish_Avg_cd','Naish_Worst_cd',
                        'Tarantula_Best_cd','Tarantula_Avg_cd','Tarantula_Worst_cd',
                        'O_Best_cd', 'O_Avg_cd', 'O_Worst_cd',
                        'Ochiai_Best','Ochiai_Avg','Ochiai_Worst',
                        'DStar2_Best','DStar2_Avg','DStar2_Worst',
                        'Naish_Best','Naish_Avg','Naish_Worst',
                        'Tarantula_Best','Tarantula_Avg','Tarantula_Worst',
                        'O_Best', 'O_Avg', 'O_Worst',
                        'Failing_Coverage',
                        'Ochiai_Collapsed_cd', 'Ochiai_Collapsed',
                        'DStar2_Collapsed_cd', 'DStar2_Collapsed',
                        'Naish_Collapsed_cd', 'Naish_Collapsed',
                        'Tarantula_Collapsed_cd', 'Tarantula_Collapsed',
                        'O_Collapsed_cd', 'O_Collapsed']

    csvfile_fixes = open('fixes.csv', 'w')
    csvwriter_fixes = csv.DictWriter(csvfile_fixes, fieldnames=fieldnames_fixes, delimiter=';')
    csvwriter_fixes.writeheader()

    for dbpath in search_dbs():
        read_db(dbpath, csvwriter_fixes)

    csvfile_fixes.close()
