from collections import defaultdict


def encode_sent(j, skip):
    """Encode a single sentence."""
    root = {}
    new_dict = defaultdict(dict)
    for x in j['tokens']:
        s, e = x['start'], x['end']

        stripped = {k: v for k, v in x.items()
                    if k and k not in skip}
        stripped['text'] = j['text'][s:e]
        new_dict[x['id']].update(stripped)
        if x["dep"] == "ROOT":
            root = new_dict[x["id"]]
        elif x["dep"]:
            try:
                new_dict[x["head"]][x["dep"]].append(new_dict[x["id"]])
            except KeyError:
                new_dict[x["head"]][x["dep"]] = new_dict[x["id"]]
                # new_dict[x["head"]][x["dep"]] = [new_dict[x["id"]]]

    return root


def tree_to_dict(j, skip=None):
    if skip is None:
        skip = set()
    else:
        skip = set(skip)

    for idx, x in enumerate(j['sents']):
        new_j = {}
        s, e = x['start'], x['end']
        new_j["tokens"] = []
        for tok in j["tokens"]:
            # end characters are inclusive
            if tok["start"] >= s and tok["end"] <= e:
                # Align the tokens with the new text
                tok["end"] -= s
                tok["start"] -= s
                new_j["tokens"].append(tok)
        new_j['text'] = j['text'][s:e]
        yield encode_sent(new_j, skip)
