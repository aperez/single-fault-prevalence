from unidiff import PatchSet

def get_modified_components(diff, source, target):
    modified_components = set()
    for p in PatchSet(diff.split('\n')):
        for hunk in p:
            for line in hunk:
                if line.is_removed:
                    temp = source.match_location(p.path, line.source_line_no)
                    temp = list(filter(target.match_name, temp))
                    modified_components |= set(temp)
                elif line.is_added:
                    temp = target.match_location(p.path, line.target_line_no)
                    temp = list(filter(source.match_name, temp))
                    modified_components |= set(temp)
    return modified_components
