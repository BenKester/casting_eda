def match_lists(a, b, f, no_dupes=False):
    # tries to match elements from the two lists
    # f is a function that can simplify the elements of the lists to try to get a match. for instance, str.lower
    # will return dictionaries containing the matches (using the original elements) as well as lists of mismatches
    # no_dupes=True will throw an exception one element matched duplicate elements of another list
    # matches will be in a list, unless no_dupes=True
    # tip: try running with no_dupes=True, then adjust if there are dupes
    default_val = None if no_dupes else []
    dic_a = {x:f(x) for x in a}
    dic_b = {x:f(x) for x in b}
    ret_a = {x:default_val for x in a}
    ret_b = {x:default_val for x in b}
    
    for ka, va in dic_a.items():
        for kb, vb in dic_b.items():
            if va == vb:
                if no_dupes:
                    if ret_a[ka] != default_val:
                        raise ValueError(f'duplicate matches for first list key {ka}')
                    if ret_b[kb] != default_val:
                        raise ValueError(f'duplicate matches for second list key {ka}')
                    ret_a[ka] = kb
                    ret_b[kb] = ka
                else:
                    ret_a[ka].append(kb)
                    ret_b[kb].append(ka)
    
    return [ret_a, ret_b, [x for x in ret_a if ret_a[x]==default_val], [x for x in ret_b if ret_b[x]==default_val]]

def full_matcher(a, b, functions, no_dupes=False):
    # see match_lists for documention
    # runs off a list of functions -- runs functions after the first only on mismatches
    ret = match_lists(a, b, functions[0], no_dupes)
    for f in functions[1:]:
        updated = match_lists(ret[2], ret[3], f, no_dupes)
        ret[0].update(updated[0])
        ret[1].update(updated[1])
        ret[2] = updated[2]
        ret[3] = updated[3]
    return ret

## functions that might be helpful
def get_chr_remover_function(forbid_list:str):
    def ret_fn(s:str):
        ret = s
        for c in forbid_list:
            ret = ret.replace(c, '')
        return ret
    return ret_fn