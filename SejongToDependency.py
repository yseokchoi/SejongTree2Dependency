from Tree import *
from itertools import product
from tqdm import tqdm
import re, os, sys, copy, argparse, time

def get_all_pos_list(key, all_pos_key, pos_list):
    allsymbol = '@@ALL@@'
    key_pattern = key.replace('*', '').strip()

    all_pos_key.setdefault(key, [])
    for pos in pos_list:
        if re.match(key_pattern, pos) is not None:
            all_pos_key[key].append('{}/{}'.format(allsymbol, pos))

    return all_pos_key[key]

def strToPattern(patternstr, pos_list=None, label=True):
    if len(pos_list) == 0 or pos_list is None:
        print("POS List is empty. please read the pos file")
        exit()

    all_pos_key = dict()

    allsymbol = '@@ALL@@'
    allsymbol_escape = re.escape(allsymbol)
    if label:
        allsymbol_compile = '.*?'
    else:
        allsymbol_compile = '.+?'

    if patternstr == '-':
        return None

    if label:
        pattern_str_list = [re.sub('\*', allsymbol, x) for x in patternstr.split(' ') if x != '']
        pattern_compile = [re.escape(x).replace(allsymbol_escape, allsymbol_compile) for x in pattern_str_list]

    else:
        pattern_str_list = [x.strip() for x in patternstr.split(' ') if x != '']
        pattern_str_list_2 = []
        for item in pattern_str_list:
            morphemes_rule = item.split('+')
            temporary_morpheme_rules = []
            for morpheme_rule in morphemes_rule:
                if len(morpheme_rule.split('/')) == 1:
                    if morpheme_rule in all_pos_key:
                        temporary_morpheme_rules.append(all_pos_key[morpheme_rule])
                    elif '*' in morpheme_rule:
                        temporary_morpheme_rules.append(get_all_pos_list(morpheme_rule, all_pos_key, pos_list))
                    elif morpheme_rule in pos_list:
                        temporary_morpheme_rules.append(['{}/{}'.format(allsymbol, morpheme_rule)])
                    else:
                        temporary_morpheme_rules.append(['{}/{}'.format(morpheme_rule, allsymbol)])
                else:
                    temporary_morpheme_rules.append([morpheme_rule])
            temporary_morpheme_rules_combination = ['+'.join(x) for x in list(product(*temporary_morpheme_rules))]
            pattern_str_list_2.extend(temporary_morpheme_rules_combination)

        pattern_compile = [re.escape(x).replace(allsymbol_escape, allsymbol_compile) for x in pattern_str_list_2]


    return pattern_compile

def read_pos_list(filename):
    pos_lists = [line.strip() for line in open(filename, 'r', encoding='utf-8')]

    return pos_lists

def readHeadRules(filename, pos_list, linear_rule=True):
    head_rules = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            parent_label, left_label, left_eojul, right_label, right_eojul, left_context, right_context = line.split('\t')
            head_rules.append(
                (
                strToPattern(parent_label.strip(), pos_list, label=True),
                strToPattern(left_label.strip(), pos_list, label=True),
                strToPattern(left_eojul.strip(), pos_list, label=False),
                strToPattern(right_label.strip(), pos_list, label=True),
                strToPattern(right_eojul.strip(), pos_list, label=False),
                strToPattern(left_context.strip(), pos_list, label=False),
                strToPattern(right_context.strip(), pos_list, label=False),
                linear_rule
                )
            )
    #print(head_rules)
    return tuple(head_rules)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-root_dir', type=str, required=True)
    parser.add_argument('-file_name', type=str, default="")
    parser.add_argument('-save_file', type=str, default="result")
    parser.add_argument('-non_rigid_head', action='store_true')

    parser.add_argument('-pos_list', type=str, default="./Rules/pos_list.txt")
    parser.add_argument('-head_initial', type=str, default="./Rules/linear_rules.txt")
    parser.add_argument('-head_initial_symbol', type=str, default="./Rules/symbol_rules.txt")

    opt = parser.parse_args()
    rigid_head = not opt.non_rigid_head
    if rigid_head:
        save_path = "{}-{}.txt".format(opt.save_file, "rigid_head")
    else:
        save_path = "{}-{}.txt".format(opt.save_file, "non_rigid_head")

    error_count = 0
    pos_list = read_pos_list(opt.pos_list)
    print("Loading POS LIST : {}".format(len(pos_list)))
    head_rules = readHeadRules(opt.head_initial, pos_list, linear_rule=True) + readHeadRules(opt.head_initial_symbol, pos_list, linear_rule=False)
    print("FIND HEAD RULES : {}".format(len(head_rules)))

    corpus_dir_path = opt.root_dir
    sent_tree_list = []
    if opt.file_name != "":
        f_text = "".join([line for line in open(os.path.join(corpus_dir_path, opt.file_name))])
        text = f_text.split("<body>")[1].split("</body>")[0].strip()

        sent_tree_s = text.split("\n\n")

        for sent_tree in sent_tree_s:
            sent = sent_tree.split("\n")[0].replace("; ", "")
            tree = "\n".join(sent_tree.split("\n")[1:])

            sent_tree_list.append((sent, tree, opt.file_name))
    else:
        for f_path in sorted(os.listdir(corpus_dir_path)):
            if f_path.endswith("~"):
                continue

            f_text = "".join([line for line in open(os.path.join(corpus_dir_path, f_path))])
            text = f_text.split("<body>")[1].split("</body>")[0].strip()

            sent_tree_s = text.split("\n\n")

            for sent_tree in sent_tree_s:
                sent = sent_tree.split("\n")[0].replace("; ", "")
                tree = "\n".join(sent_tree.split("\n")[1:])

                sent_tree_list.append((sent, tree, f_path))

    print(len(sent_tree_list))

    log = []

    start = time.time()
    cnt = 0
    for ori_sent, struct, ref in tqdm(sent_tree_list, desc=" - (Converting)  "):
        cnt += 1
        sent_id = cnt
        cst = ConstitiuentStructureTree(head_rules)
        ori_sent, _ = cst.replaceSymbol(ori_sent)

        quotation_check = re.match("(Q[0-9]+)", ori_sent)
        if quotation_check:
            quotation = quotation_check.group()
            sent_id = "{}-{}".format(sent_id, quotation)
            ori_sent = ori_sent.replace(quotation, "").strip()

        struct, except_result = cst.replaceSymbol(struct)
        if except_result:
            error_count += 1
            continue

        strToTree, tree_result = cst.fromstring(struct)
        if not tree_result:
            error_count += 1
            continue

        cst.insert(strToTree)
        cst.find_head(head_free=rigid_head)

        headers = cst.get_header()

        check_crossing = cst.check_crossing(headers)
        if not check_crossing:
            error_count += 1
            continue

        ori_sent, headers, reform_result = cst.reform_ori_sent(ori_sent, headers)
        if not reform_result:
            error_count += 1
            continue

        log.append("#SENTID:{}".format(sent_id))
        log.append("#FILE:{}".format(ref))
        log.append("#ORISENT:{}".format(ori_sent))
        for node_idx in sorted(headers.keys()):
            node = headers[node_idx]
            log.append('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(node_idx+1, node[0], node[1], node[2], node[3], node[4], node[5], node[6], node[7], node[8]))
        log.append("\n")

    with open(save_path, 'w') as f:
         f.write('\n'.join(log))
    print("\nfinish")
    print("error_count : {error_count} elapse : {elapse:3.3f} min".format(error_count=error_count, elapse=(time.time()-start)/60))

main()

