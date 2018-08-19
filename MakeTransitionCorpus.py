import copy, argparse, os, time, sys

def checkReduce(i, relations):
    result = False
    for _, _, t in relations:
        if i == t:
            result = True
            break
    return result

def checkChildren(target, head_info, relation):
    relation_c = [(a, b) for _, a, b in relation]
    result = True
    govern_childrens = [(b, a) for a, b in head_info.items() if b == target]
    #print(govern_childrens)
    for key in govern_childrens:
        if key not in relation_c:
            result = False
            break
    return result

def arcstandard(data):
    head_info = {a: b[1] for a, b in sorted(data.items(), key=lambda x: x[0])}
    size = len(data)
    stack = []
    buffer = [x + 1 for x in range(0, size-1)] + [0]
    relation = []

    arc_data = ["{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]), " ".join([str(x) for x in copy.copy(buffer)]), "_")]

    stack.append(buffer[0])
    del buffer[0]
    #arc_data.append("{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]), " ".join([str(x) for x in copy.copy(buffer)]), "_"))
    #print(head_info)
    while len(stack) != 1 or  stack[-1] != 0:
        # print("STACK: {}".format(stack))
        # print("BUFFER: {}".format(buffer))
        # print("RELATION: {}".format(relation))
        if len(stack) > 1 and head_info[stack[-2]] == stack[-1] and checkChildren(stack[-2], head_info, relation):
            rel = data[stack[-2]][2] if data[stack[-2]][2] != "_" else "NONE"
            key = (stack[-1], stack[-2])

            relation_str = ["({} {} {})".format(rel, a, b) for rel, a, b in relation[::-1]]
            if len(relation_str) > 0:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("LEFT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                               " ".join([str(x) for x in copy.copy(buffer)]),
                                               " ".join(relation_str)))
            else:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("LEFT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                               " ".join([str(x) for x in copy.copy(buffer)]),
                                               "_"))

            relation.append((rel, key[0], key[1]))
            del stack[-2]

        elif len(stack) > 1 and head_info[stack[-1]] == stack[-2] and checkChildren(stack[-1], head_info, relation):
            rel = data[stack[-1]][2] if data[stack[-1]][2] != "_" else "NONE"
            key = (stack[-2], stack[-1])

            relation_str = ["({} {} {})".format(rel, a, b) for rel, a, b in relation[::-1]]
            if len(relation_str) > 0:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("RIGHT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                                         " ".join([str(x) for x in copy.copy(buffer)]),
                                                         " ".join(relation_str)))
            else:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("RIGHT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                                         " ".join([str(x) for x in copy.copy(buffer)]),
                                                         "_"))
            relation.append((rel, key[0], key[1]))
            del stack[-1]

        else:
            relation_str = ["({} {} {})".format(rel, a, b) for rel, a, b in relation[::-1]]
            if len(relation_str) > 0:
                arc_data.append("{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]),
                                                        " ".join([str(x) for x in copy.copy(buffer)]), " ".join(relation_str)))
            else:
                arc_data.append("{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]),
                                                        " ".join([str(x) for x in copy.copy(buffer)]),
                                                        "_"))
            stack.append(buffer[0])
            del buffer[0]

    return arc_data


def arceager(data):
    head_info = {a: b[1] for a, b in sorted(data.items(), key=lambda x: x[0])}
    size = len(data)
    stack = []
    buffer = [0]+[x for x in range(size-1, 0, -1)]
    relation = []
    arc_data = ["{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]), " ".join([str(x) for x in copy.copy(buffer)]), "_")]

    stack.append(buffer[0])
    del buffer[0]
    #arc_data.append("{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]), " ".join([str(x) for x in copy.copy(buffer)]), "NONE"))

    while len(buffer) > 0:
        if head_info[stack[-1]] == buffer[0]:
            rel = data[stack[-1]][2] if data[stack[-1]][2] != "_" else "NONE"
            key = (buffer[0], stack[-1])

            relation_str = ["({} {} {})".format(rel, a, b) for rel, a, b in relation[::-1]]
            if len(relation_str) > 0:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("LEFT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                                      " ".join([str(x) for x in copy.copy(buffer)]),
                                                      " ".join(relation_str)))
            else:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("LEFT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                               " ".join([str(x) for x in copy.copy(buffer)]),
                                               "_"))

            relation.append((rel, key[0], key[1]))
            del stack[-1]

        elif head_info[buffer[0]] == stack[-1]:
            rel = data[buffer[0]][2] if data[buffer[0]][2] != "_" else "NONE"
            key = (stack[-1], buffer[0])

            relation_str = ["({} {} {})".format(rel, a, b) for rel, a, b in relation[::-1]]
            if len(relation_str) > 0:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("RIGHT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                                      " ".join([str(x) for x in copy.copy(buffer)]),
                                                      " ".join(relation_str)))
            else:
                arc_data.append(
                    "{} {}\t{}\t{}\t{}".format("RIGHT-ARC", rel, " ".join([str(x) for x in copy.copy(stack)]),
                                               " ".join([str(x) for x in copy.copy(buffer)]),
                                               "_"))

            relation.append((rel, key[0], key[1]))
            stack.append(buffer[0])
            del buffer[0]

        elif head_info[stack[-1]] != buffer[0] and checkChildren(stack[-1], head_info, relation):
            relation_str = ["({} {} {})".format(rel, a, b) for rel, a, b in relation[::-1]]
            if len(relation_str) > 0:
                arc_data.append("{}\t{}\t{}\t{}".format("REDUCE", " ".join([str(x) for x in copy.copy(stack)]),
                                                        " ".join([str(x) for x in copy.copy(buffer)]), " ".join(relation_str)))
            else:
                arc_data.append("{}\t{}\t{}\t{}".format("REDUCE", " ".join([str(x) for x in copy.copy(stack)]),
                                                        " ".join([str(x) for x in copy.copy(buffer)]), "_"))
            del stack[-1]

        else:
            relation_str = ["({} {} {})".format(rel, a, b) for rel, a, b in relation[::-1]]
            if len(relation_str) > 0:
                arc_data.append("{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]),
                                                        " ".join([str(x) for x in copy.copy(buffer)]), " ".join(relation_str)))
            else:
                arc_data.append("{}\t{}\t{}\t{}".format("SHIFT", " ".join([str(x) for x in copy.copy(stack)]),
                                                        " ".join([str(x) for x in copy.copy(buffer)]), "_"))
            stack.append(buffer[0])
            del buffer[0]

    return arc_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-root_dir', type=str, required=True)
    parser.add_argument('-file_name', type=str, default="")
    parser.add_argument('-save_file', type=str, default="result")
    parser.add_argument('-arc_standard', action='store_true')

    opt = parser.parse_args()

    arc_standard = opt.arc_standard

    save_path = opt.save_file

    corpus_dir_path = opt.root_dir
    datas = []
    if opt.file_name != "":
        f_text = open(os.path.join(corpus_dir_path, opt.file_name)).read().strip()
        datas.extend(f_text.split("\n\n\n"))

    else:
        for f_path in sorted(os.listdir(corpus_dir_path)):
            if f_path.endswith("~"):
                continue
            f_text = open(os.path.join(corpus_dir_path, opt.file_name)).read().strip()
            datas.extend(f_text.split("\n\n\n"))

    conll_datas = []

    for data in datas:
        data = data.strip()
        info = []
        conll = {}
        for line in data.split("\n"):
            if line.startswith("#"):
                info.append(line)
            else:
                info.append(line)
                idx, _, lemma, _, _, _, head, deprel, _, _ = line.split("\t")
                conll.setdefault(int(idx), (lemma, int(head), deprel))
        conll.setdefault(0, ("ROOT", 0, "_"))
        conll_datas.append((info, conll))
    print(len(conll_datas))

    log = []
    cnt = 1
    size = len(conll_datas)
    start = time.time()
    for info, conll in conll_datas:
        sys.stdout.write("\r{}/{}".format(cnt, size))
        sys.stdout.flush()

        cnt += 1

        if arc_standard:
            arc_data = arcstandard(conll)
        else:

            arc_data = arceager(conll)

        log.extend(info)
        log.extend(arc_data)
        log.append("\n")

    with open(save_path, 'w') as f:
        f.write('\n'.join(log))
    print("\nfinish elapse : {elapse:3.3f} min".format(elapse=(time.time() - start) / 60))

main()
