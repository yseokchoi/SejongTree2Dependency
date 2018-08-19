from UPosTagMap import *
from AssignUDepRel import *
from itertools import product
from collections import OrderedDict
import re, math

class Node(object):
    def __init__(self, label, index=-1, token=None, t_index=-1, parent_id=-1):
        self.t_index = t_index
        self.index = index
        self.label = label
        self.token = token
        self.parent_id = parent_id
        self.head_index = -1
        self.head_label = None
        self.head_index_linear = -1
        self.head_final_index = -1
        self.linear_check = False
        self.left_child = self.right_child = None

class ConstitiuentStructureTree(object):
    def __init__(self, linear_rules_file, symbol_rules=True, head_final=True):
        self.pos_list = [
            "NNG",
            "NNP",
            "NNB",
            "NP",
            "NR",
            "VV",
            "VA",
            "VX",
            "VCP",
            "VCN",
            "MM",
            "MAG",
            "MAJ",
            "IC",
            "JKS",
            "JKC",
            "JKG",
            "JKO",
            "JKB",
            "JKV",
            "JKQ",
            "JX",
            "JC",
            "EP",
            "EF",
            "EC",
            "ETN",
            "ETM",
            "XPN",
            "XSN",
            "XSV",
            "XSA",
            "XR",
            "SF",
            "SP",
            "SS",
            "SE",
            "SO",
            "SL",
            "SH"
        ]
        self.rules = self.readHeadRules(linear_rules_file, self.pos_list, linear_rule=True)
        print("FIND HEAD INITAL RULES : {}".format(len(self.rules)))
        if symbol_rules:
            self.rules += self.getSymbolRules(self.pos_list, linear_rule=False)

        self.root = None
        self.length = 0
        self.total_node = 0
        self.upostag_map = UPosTagMap()
        self.keymap = {
            "ᄀ":"ㄱ",
            "ᆫ":"ㄴ",
            "ᄃ":"ㄷ",
            "ᆯ":"ㄹ",
            "ᄆ":"ㅁ",
            "ᄇ":"ㅂ",
            "ᆼ":"ㅇ",
            "ᄎ":"ㅊ",
            "ᄒ":"ㅎ",
            "，":",",
            "`":"\'",
            "\'":"\'",
            "\"":"\"",
            "-":"-",
            "‘":"\'",
            "“":"\"",
            "­":"-",
            "”":"\"",
            "─":"-",
            "―":"-",
            "－":"-",
            "_":"_",
            "’":"\'",
            "…":"...",
            "...":"...",
            "…………":"...",
            "∼":"~",
            "～":"~",
            "~":"~",
            "○":"O",
            "O":"O",
            "X":"X",
            "×":"x",
            "+":"+",
            ".":".",
            "?":"?",
            "!":"!",
            "/":"/",
            ",":",",
            "·":"·",
            ";":";",
            "(":"(",
            ")":")",
            "[":"[",
            "]":"]",
            "{":"{",
            "}":"}",
            "/*":"/",
            ",*":",",
            "·*":"·",
            "【":"@@SYMBOL_0@@",
            "『":"@@SYMBOL_1@@",
            "』":"@@SYMBOL_2@@",
            "「":"@@SYMBOL_3@@",
            "」":"@@SYMBOL_4@@",
            "〔":"@@SYMBOL_5@@",
            "〕":"@@SYMBOL_6@@",
            "《":"@@SYMBOL_7@@",
            "》":"@@SYMBOL_8@@",
            "㎏":"@@SYMBOL_9@@",
            "%":"%",
            "㎞":"@@SYMBOL_10@@",
            "㎝":"@@SYMBOL_11@@",
            "▴":"@@SYMBOL_12@@",
            "㎜":"@@SYMBOL_13@@",
            "㈜":"@@SYMBOL_14@@",
            "=":"@@SYMBOL_15@@",
            "◇":"@@SYMBOL_16@@",
            "Ⅰ":"@@SYMBOL_17@@",
            "Ⅱ":"@@SYMBOL_18@@",
            "㎖":"@@SYMBOL_19@@",
            "ℓ":"@@SYMBOL_20@@",
            "²":"@@SYMBOL_21@@",
            "㎡":"@@SYMBOL_22@@",
            "→":"@@SYMBOL_23@@",
            "&":"&",
            "○":"@@SYMBOL_24@@",
            "△":"@@SYMBOL_25@@",
            "@":"@",
            "#":"#",
            "*":"*",
            "◎":"@@SYMBOL_26@@",
            "▹":"@@SYMBOL_27@@",
            "□":"@@SYMBOL_28@@",
            "◁":"@@SYMBOL_29@@",
            "℃":"@@SYMBOL_30@@",
            "➀":"@@SYMBOL_31@@",
            "❷":"@@SYMBOL_32@@",
            "➌":"@@SYMBOL_33@@",
            "^":"^",
            "∠":"@@SYMBOL_34@@",
            "α":"@@SYMBOL_35@@",
            "〓":"=",
            "±":"@@SYMBOL_36@@",
            "<":"<",
            ">":">"
        }

        self.keymap_exception = {
            "/SS.":1,
            "/SS,":3,
            "고EC,":1,
        }

        self.JONGSUNG = {u'':0, u'ㄱ':1, u'ㄲ':2, u'ㄳ':3, u'ㄴ':4, u'ㄵ':5, u'ㄶ':6, u'ㄷ':7, u'ㄹ':8, u'ㄺ':9, u'ㄻ':10, u'ㄼ':11,
            u'ㄽ':12, u'ㄾ':13, u'ㄿ':14, u'ㅀ':15, u'ㅁ':16, u'ㅂ':17, u'ㅄ':18, u'ㅅ':19, u'ㅆ':20, u'ㅇ':21, u'ㅈ':22,
            u'ㅊ':23, u'ㅋ':24, u'ㅌ':25, u'ㅍ':26, u'ㅎ':27}

        self.NUMJONG = len(self.JONGSUNG)
        self.string_types = (type(""),)
        self.head_final = head_final
        self.depRel_map = UDepRelMap(int(self.head_final))

    def reset(self):
        if self.length > 0:
            self.root = None
            self.length = 0
            self.total_node = 0


    def get_all_pos_list(self, key, all_pos_key, pos_list):
        allsymbol = '@@ALL@@'
        key_pattern = key.replace('*', '').strip()

        all_pos_key.setdefault(key, [])
        for pos in pos_list:
            if re.match(key_pattern, pos) is not None:
                all_pos_key[key].append('{}/{}'.format(allsymbol, pos))

        return all_pos_key[key]

    def strToPattern(self, patternstr, pos_list=None, label=True):
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
                            temporary_morpheme_rules.append(self.get_all_pos_list(morpheme_rule, all_pos_key, pos_list))
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

    def getSymbolRules(self, pos_list, linear_rule=False):
        rules = [("-", "-", "-", "X*", "SS  SP", "-", "-"),
                 ("-", "-", "-", "R*", "SS  SP", "-", "-"),
                 ("-", "-", "-", "X*", "J*  E*  XP*  XS*  SS  SP", "-", "-"),
                 ("NP", "NP  R(NP)", "-", "NP_PRN  L(NP_PRN)", "SS", "-", "-")]

        result = []

        for line in rules:
            parent_label, left_label, left_eojul, right_label, right_eojul, left_context, right_context = line
            result.append(
                (
                    self.strToPattern(parent_label.strip(), pos_list, label=True),
                    self.strToPattern(left_label.strip(), pos_list, label=True),
                    self.strToPattern(left_eojul.strip(), pos_list, label=False),
                    self.strToPattern(right_label.strip(), pos_list, label=True),
                    self.strToPattern(right_eojul.strip(), pos_list, label=False),
                    self.strToPattern(left_context.strip(), pos_list, label=False),
                    self.strToPattern(right_context.strip(), pos_list, label=False),
                    linear_rule
                )
                )
        return tuple(result)

    def readHeadRules(self, filename, pos_list, linear_rule=True):
        head_rules = []

        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                parent_label, left_label, left_eojul, right_label, right_eojul, left_context, right_context = line.split('\t')
                head_rules.append(
                    (
                        self.strToPattern(parent_label.strip(), pos_list, label=True),
                        self.strToPattern(left_label.strip(), pos_list, label=True),
                        self.strToPattern(left_eojul.strip(), pos_list, label=False),
                        self.strToPattern(right_label.strip(), pos_list, label=True),
                        self.strToPattern(right_eojul.strip(), pos_list, label=False),
                        self.strToPattern(left_context.strip(), pos_list, label=False),
                        self.strToPattern(right_context.strip(), pos_list, label=False),
                        linear_rule
                    )
                )
        return tuple(head_rules)

    def replaceSymbol(self, sentence):
        result = sentence
        except_result = False
        for key in self.keymap_exception:
            if key in sentence:
                except_result = True
                return result, except_result


        for key1, key2 in self.keymap.items():
            key1_, key2_ = re.escape(key1), re.escape(key2)
            if re.search(key1_, result):
                result = re.sub(key1_, key2, result)
        return result, except_result

    def restoreSymbol(self, sentence):
        result = sentence
        for key1, key2 in self.keymap.items():
            if re.search("@@SYMBOL_[0-9]+@@", key2):
                result = result.replace(key2, key1)
        return result

    def threeLinearCheck(self, head_list, linear_rules):
        result_head = []
        for a, b, rule, s_rule, label, except_PRN in head_list:
            if (a-1, a, b) in linear_rules:
                if linear_rules[(a-1, a, b)][0] and linear_rules[(a-1, a, b)][1]:
                    result_head.append((a, b, rule, s_rule, label[0], except_PRN))
                else:
                    result_head.append((a, b, False, False, label[1], False))
            else:
                result_head.append((a, b, rule, s_rule, label[0], except_PRN))
        return result_head

    def rearrangeLinear(self, head_list):
        result_head = []
        for a, b, rule, s_rule, label, except_PRN in head_list:
            if rule and not except_PRN and math.fabs(a - b) > 1:
                result_head.append((a, a+1, rule, s_rule, label, except_PRN))
            else:
                result_head.append((a, b, rule, s_rule, label, except_PRN))
        return result_head

    def PRN_rules(self, head_list):
        linear_rules = {b:a for a, b, rule, _, _, _ in head_list if rule}
        result_head = []

        for a, b, rule, s_rule, label, except_PRN in head_list:
            if except_PRN:
                target_a = a
                target_b = b
                while target_a in linear_rules:
                    target_a = linear_rules[target_a]

                while target_b in linear_rules:
                    target_b = linear_rules[target_b]

                result_head.append((target_a, target_b, rule, s_rule, label, except_PRN))
            else:
                result_head.append((a, b, rule, s_rule, label, except_PRN))
        return result_head

    def moveSymbolHead(self, head_list):
        linear_and_symbol_rules = {b:a for a, b, rule, _, _, _ in head_list if rule}
        result_head = []
        for a, b, rule, s_rule, label, except_PRN in head_list:
            if s_rule:
                target_a = a
                while target_a in linear_and_symbol_rules:
                    target_a = linear_and_symbol_rules[target_a]
                result_head.append((target_a, b, rule, s_rule, label, except_PRN))
            else:
                result_head.append((a, b, rule, s_rule, label, except_PRN))
        return result_head

    def moveHead(self, head_list):
        linear_rules = {b:a for a, b, rule, _, _, _ in head_list if rule}
        loc_PRN = {loc:(b, a) for loc, (a, b, _, _, _, except_PRN) in enumerate(head_list) if except_PRN}
        result_head = []

        for loc, (a, b, rule, s_rule, label, except_PRN) in enumerate(head_list):
            if loc-1 in loc_PRN:
                head, child = loc_PRN[loc-1]
                if head in linear_rules:
                    linear_rules[head] = child
                else:
                    linear_rules.setdefault(head, child)

            if not rule:
                target_b = b
                while target_b in linear_rules:
                    target_b = linear_rules[target_b]
                result_head.append((a, target_b, rule, s_rule, label, except_PRN))

            else:
                if not s_rule and not self.head_final:
                    result_head.append((a, b, rule, s_rule, "_", except_PRN))
                elif not self.head_final:
                    target_a = a
                    while target_a in linear_rules and rule:
                        target_a = linear_rules[target_a]
                    result_head.append((target_a, b, rule, s_rule, label, except_PRN))
                else:
                    result_head.append((a, b, rule, s_rule, label, except_PRN))
        return result_head

    def doubleHead(self, head_list):
        head_list_dict = {b:a for a, b, rule, _, _, except_PRN in head_list if rule or except_PRN}
        result_head = []
        for a, b, rule, s_rule, label, except_PRN in head_list:
            if not rule and a in head_list_dict:
                key = head_list_dict[a]
                while key in head_list_dict:
                    key = head_list_dict[key]
                result_head.append((key, b, rule, s_rule, label, except_PRN))
                continue

            else:
                result_head.append((a, b, rule, s_rule, label, except_PRN))
        return result_head

    def getHead(self, head_list):
        result_head = {}
        result_label = {}
        for a, b, rule, _, label, except_PRN in head_list:
            if rule or except_PRN:
                result_head.setdefault(b, a)
                result_label.setdefault(b, label)
            else:
                result_head.setdefault(a, b)
                result_label.setdefault(a, label)

        return result_head, result_label

    def insert(self, stt):
        self.root = self._insert_value(self.root, stt, total_index=self.total_node)
        return self.root is not None

    def _insert_value(self, node, stt, total_index=-1, parent_id=-1):
        if node is None:
            if isinstance(stt[0], self.string_types) and isinstance(stt[1][0], self.string_types):
                token = ''.join(stt[1])
                if '+/SW' in token:
                    token = token
                elif token[0] == '+':
                    token = token[1:]

                node = Node(stt[0], index=self.length, token=token, t_index=total_index, parent_id=parent_id)
                self.length += 1
                self.total_node += 1
                return node
            else:
                node = Node(stt[0], t_index=total_index, parent_id=parent_id)
                self.total_node += 1
        try:
            node.left_child = self._insert_value(node.left_child, stt[1][0], total_index=self.total_node, parent_id=node.t_index)
        except IndexError:
            return node

        try:
            node.right_child = self._insert_value(node.right_child, stt[1][1], total_index=self.total_node, parent_id=node.t_index)
        except IndexError:
            return node

        return node

    def find(self, node, method, depth=0):
        if method == 'rmn':
            if node.right_child is None:
                return node, depth
            else:
                depth += 1
                return self.find(node.right_child, method=method, depth=depth)
        elif method == 'lmn':
            if node.left_child is None:
                return node, depth
            else:
                depth += 1
                return self.find(node.left_child, method=method, depth=depth)
        else:
            print("ERROR")
            exit()

    def find_node_index(self, index, total_index=False):
        return self._find_node_index(self.root, index, total_index=total_index)

    def _find_node_index(self, node, index, total_index=False):
        if node is None:
            return -1
        if not total_index and node.index == index:
            return node
        elif total_index and node.t_index == index:
            return node

        left_result = -1
        right_result = -1
        if node.left_child is not None:
            left_result = self._find_node_index(node.left_child, index, total_index=total_index)
        if node.right_child is not None:
            right_result = self._find_node_index(node.right_child, index, total_index=total_index)

        if left_result != -1:
            return left_result
        if right_result != -1:
            return right_result

        return -1

    def find_head(self):
        result_head = []
        three_linear_rules = {}

        def _find_head(node, head_list, linear_rules):
            if node is None:
                pass
            else:
                _find_head(node.left_child, head_list, linear_rules)
                _find_head(node.right_child, head_list, linear_rules)
                if node.index == -1:
                    right_most_node, _ = self.find(node.left_child, method='rmn')
                    left_most_node, ldepth = self.find(node.right_child, method='lmn')
                    right_node, _ = self.find(node.right_child, method='rmn')

                    linear_rule_check = False

                    for parent_label_rule, left_label_rule, left_eojul_rule, right_label_rule, right_eojul_rule, left_context_rule, right_context_rule, linear_rule in self.rules:
                        except_PRN = False
                        left_context_node = None
                        right_context_node = None
                        if left_context_rule is not None and right_most_node.index - 1 >= 0:
                            left_context_node = self.find_node_index(right_most_node.index - 1)
                        elif left_context_rule is not None and right_most_node.index - 1 == -1:
                            left_context_node = ""
                        if right_context_rule is not None and left_most_node.index + 1 < self.length:
                            right_context_node = self.find_node_index(left_most_node.index + 1)
                        elif right_context_rule is not None and left_most_node.index + 1 == self.length:
                            right_context_node = ""

                        t_left_most_node_label = left_most_node.label
                        t_right_most_node_label = right_most_node.label
                        if self.checkPattern(self.strToPattern("L", self.pos_list, label=True), left_most_node.label):
                            left_most_node_parent = self.find_node_index(left_most_node.parent_id, total_index=True)
                            t_left_most_node_label = "{}({})".format(t_left_most_node_label, left_most_node_parent.label)
                            except_PRN = True
                        if self.checkPattern(self.strToPattern("R", self.pos_list, label=True), right_most_node.label):
                            right_most_node_parent = self.find_node_index(right_most_node.parent_id, total_index=True)
                            t_right_most_node_label = "{}({})".format(t_right_most_node_label, right_most_node_parent.label)
                            except_PRN = True

                        if self.checkPattern(parent_label_rule, node.label) and \
                            self.checkPattern(left_label_rule, t_right_most_node_label) and \
                            self.checkPattern(left_eojul_rule, right_most_node, True) and \
                            self.checkPattern(right_label_rule, t_left_most_node_label) and \
                            self.checkPattern(right_eojul_rule, left_most_node, False) and \
                            self.checkPattern(left_context_rule, left_context_node, True) and \
                            self.checkPattern(right_context_rule, right_context_node, False):

                            if left_context_rule is not None and isinstance(left_context_node, Node) and self.checkPattern(left_context_rule, left_context_node, True):
                                linear_rules.setdefault((left_context_node.index, right_most_node.index, left_most_node.index), [False, False])
                                linear_rules[(left_context_node.index, right_most_node.index, left_most_node.index)][0] = True
                                if left_most_node.index + 1 == self.length: #180814 마지막 노드가 문장 끝일 경우
                                    linear_rules[(left_context_node.index, right_most_node.index, left_most_node.index)][1] = True
                            elif right_context_rule is not None and isinstance(right_context_node, Node) and self.checkPattern(right_context_rule, right_context_node, False):
                                linear_rules.setdefault((right_most_node.index, left_most_node.index, right_context_node.index), [False, False])
                                linear_rules[(right_most_node.index, left_most_node.index, right_context_node.index)][1] = True

                            if linear_rule:
                                head_list.append((right_most_node.index, right_node.index, True, False, (node.right_child.label, node.left_child.label), except_PRN))
                                linear_rule_check = True
                                break
                            elif except_PRN:
                                head_list.append((right_most_node.index, right_node.index, False, False,
                                                  (node.right_child.label, node.left_child.label), except_PRN))
                                linear_rule_check = True
                                break
                            elif ldepth == 0:
                                head_list.append((right_most_node.index, right_node.index, True, True, (node.right_child.label, node.left_child.label), except_PRN))
                                linear_rule_check = True
                                break
                    except_PRN = False

                    if not linear_rule_check:
                        head_list.append((right_most_node.index, right_node.index, False, False, (node.left_child.label, node.right_child.label), except_PRN))

        def _find_head_final(node, head_list, linear_rules):
            if node is None:
                pass
            else:
                _find_head_final(node.left_child, head_list, linear_rules)
                _find_head_final(node.right_child, head_list, linear_rules)
                if node.index == -1:
                    right_most_node, _ = self.find(node.left_child, method='rmn')
                    left_most_node, _ = self.find(node.right_child, method='lmn')
                    right_node, _ = self.find(node.right_child, method='rmn')

                    linear_rule_check = False
                    for parent_label_rule, left_label_rule, left_eojul_rule, right_label_rule, right_eojul_rule, left_context_rule, right_context_rule, linear_rule in self.rules:
                        left_context_node = None
                        right_context_node = None
                        if left_context_rule is not None and right_most_node.index - 1 >= 0:
                            left_context_node = self.find_node_index(right_most_node.index - 1)
                        elif left_context_rule is not None and right_most_node.index - 1 == -1:
                            left_context_node = ""
                        if right_context_rule is not None and left_most_node.index + 1 < self.length:
                            right_context_node = self.find_node_index(left_most_node.index + 1)
                        elif right_context_rule is not None and left_most_node.index + 1 == self.length:
                            right_context_node = ""

                        if self.checkPattern(parent_label_rule, node.label) and \
                                self.checkPattern(left_label_rule, right_most_node.label) and \
                                self.checkPattern(left_eojul_rule, right_most_node, True) and \
                                self.checkPattern(right_label_rule, left_most_node.label) and \
                                self.checkPattern(right_eojul_rule, left_most_node, False) and \
                                self.checkPattern(left_context_rule, left_context_node, True) and \
                                self.checkPattern(right_context_rule, right_context_node, False) and \
                                linear_rule:

                            if left_context_rule is not None and isinstance(left_context_node, Node) and self.checkPattern(left_context_rule, left_context_node, True):
                                linear_rules.setdefault((left_context_node.index, right_most_node.index, left_most_node.index), [False, False])
                                linear_rules[(left_context_node.index, right_most_node.index, left_most_node.index)][0] = True
                                if left_most_node.index + 1 == self.length: #180814 마지막 노드가 문장 끝일 경우
                                    linear_rules[(left_context_node.index, right_most_node.index, left_most_node.index)][1] = True
                            elif right_context_rule is not None and isinstance(right_context_node, Node) and self.checkPattern(right_context_rule, right_context_node, False):
                                linear_rules.setdefault((right_most_node.index, left_most_node.index, right_context_node.index), [False, False])
                                linear_rules[(right_most_node.index, left_most_node.index, right_context_node.index)][1] = True

                            head_list.append((right_most_node.index, right_node.index, True, False, (node.left_child.label, node.left_child.label), False))
                            linear_rule_check = True
                            break

                    if not linear_rule_check:
                        head_list.append((right_most_node.index, right_node.index, False, False, (node.left_child.label, node.left_child.label), False))

        if not self.head_final:
            _find_head(self.root, result_head, three_linear_rules)
            result_head = self.threeLinearCheck(result_head, three_linear_rules)
            result_head = self.rearrangeLinear(result_head)
            result_head = self.PRN_rules(result_head)
            result_head = self.moveSymbolHead(result_head)
            result_head = self.moveHead(result_head)
            result_head = self.doubleHead(result_head)
            result_head, result_label = self.getHead(result_head)
            if len(result_head) != self.length-1:
                return None, None
        else:
            _find_head_final(self.root, result_head, three_linear_rules)
            result_head = self.threeLinearCheck(result_head, three_linear_rules)
            result_head = self.rearrangeLinear(result_head)
            result_head = self.moveHead(result_head)
            result_label = {a: label for a, _, _, _, label, _ in result_head}
            result_head = {a:b for a, b, _, _, _, _ in result_head}

        return result_head, result_label

    def get_lemma_and_xpostag(self, token):
        lemma_pos_check = re.compile("(.+?)/([A-Z]+)")

        result = lemma_pos_check.findall(token)
        lemmas = []
        for x in result:
            lemma = x[0] if len(x[0]) == 1 else x[0].replace('+', '')
            if len(lemma) > 1 and lemma[-1] == "*":
                lemma = lemma[:-1]
            lemmas.append(lemma)
        poses = [x[1] for x in result]

        return ' '.join(lemmas), '+'.join(poses)

    def get_header(self, headers_info=None, labels_info=None):
        result = dict()

        def _post_order_traversal(node, result_, headers_info, labels_info):
            if node is None:
                pass
            else:
                _post_order_traversal(node.left_child, result_, headers_info, labels_info)
                _post_order_traversal(node.right_child, result_, headers_info, labels_info)
                if node.index != -1:
                    lemma, xpostag = self.get_lemma_and_xpostag(node.token)
                    input_xpostag = " ".join(xpostag.split("+"))
                    if node.index not in headers_info:
                        result_.setdefault(node.index, [node.token, lemma, "+".join(self.upostag_map.GetUPOS(input_xpostag, lemma)), xpostag, "_", 0, "ROOT", "_", "_"])
                    else:
                        result_.setdefault(node.index, [node.token, lemma,"+".join(self.upostag_map.GetUPOS(input_xpostag, lemma)), xpostag, "_", headers_info[node.index]+1, labels_info[node.index], "_", "_"])
        _post_order_traversal(self.root, result, headers_info, labels_info)
        return result

    def fromstring(self, sent, brackets='()', node_pattern=None, leaf_pattern=None):
        if not isinstance(brackets, self.string_types) or len(brackets) != 2:
            raise TypeError('brackets must be a length 2 string')
        if re.search('\s', brackets):
            raise TypeError('whitespace brackets not allowed')

        sent_open_bracket = ('(/SS', '%OPEN%/SS')
        sent_close_bracket = (')/SS', '%CLOSE%/SS')

        sent = sent.replace(sent_open_bracket[0], sent_open_bracket[1])
        sent = sent.replace(sent_close_bracket[0], sent_close_bracket[1])

        open_b, close_b = brackets
        open_pattern, close_pattern = (re.escape(open_b), re.escape(close_b))

        if node_pattern is None:
            node_pattern = '[^\s%s%s]+' % (open_pattern, close_pattern)
        if leaf_pattern is None:
            leaf_pattern = '[^\s%s%s]+' % (open_pattern, close_pattern)
        token_re = re.compile('%s\s*(%s)?|%s|(%s)' % (
            open_pattern, node_pattern, close_pattern, leaf_pattern))

        try:
            stack = [(None, [])]
            for match in token_re.finditer(sent):
                token = match.group()
                if token[0] == open_b:
                    label = token[1:].lstrip()
                    stack.append((label, []))
                elif token == close_b:
                    label, children = stack.pop()
                    stack[-1][1].append((label, children))
                else:
                    if token == sent_open_bracket[1]:
                        token = token.replace(sent_open_bracket[1], sent_open_bracket[0])
                    elif token == sent_close_bracket[1]:
                        token = token.replace(sent_close_bracket[1], sent_close_bracket[0])
                    stack[-1][1].append(token)

            tree = stack[0][1][0]
            return tree, True
        except:
            return None, False

    def checkPattern(self, patterns, target, left=True):
        if patterns is None or target is None:
            return True

        for str_pattern in patterns:
            pattern = re.compile(str_pattern)
            if isinstance(target, Node):
                pattern_length = len(str_pattern.split('\+'))
                if left:
                    token = '+'.join(target.token.split('+')[-pattern_length:])
                else:
                    token = '+'.join(target.token.split('+')[:pattern_length])

                if pattern_length == 1 and left and 'JX' in target.token.split('+')[-1] and len(target.token.split('+')) > 1:
                    token = target.token.split('+')[-2]

                if pattern.match(token):
                    return True
            else:
                if pattern.match(target):
                    return True
        return False

    def check_crossing(self, headers):
        result = True
        id_header_pairs = [(idx+1, head[5]) for idx, head in sorted(headers.items(), key=lambda x:x[0])]
        for i, (idx, head_number) in enumerate(id_header_pairs):
            for idx_, head_number_ in id_header_pairs[i+1:]:
                gap = math.fabs(idx - head_number)
                if gap == 1:
                    break

                if idx < idx_ and idx_ < head_number:
                    gap2 = math.fabs(idx_ - head_number_)
                    if gap < gap2 and head_number_ != 0:
                        result = False
                        break

            if not result:
                break

        return result

    def check_cycle(self, headers):
        result = True
        for idx in sorted(headers.keys()):
            visit_idx = OrderedDict()
            while headers[idx][5] != 0:
                if headers[idx][5] - 1 in visit_idx:
                    result = False
                    break
                idx = headers[idx][5] - 1
                visit_idx.setdefault(idx)

        return result

    def decomposeJongCheck(self, letter):
        jong = int((ord(letter)-0xAC00) % self.NUMJONG)
        return jong == 0, jong

    def composeHangul(self, morphemes):
        key_morphemes = {}
        results = []
        for idx, morpheme in enumerate(morphemes):
            key_morphemes.setdefault(morpheme, 0)
            ja_syllable = re.search("[ㄱ-ㅎ]", morpheme)
            if len(results) > 0 and ja_syllable and re.search("[가-힣]", results[-1]):
                del results[-1]
                post_morpheme = morpheme[1:]
                post_ja_syllable_index = self.JONGSUNG[ja_syllable.group()]
                pre_syllable_check, jong_number = self.decomposeJongCheck(morphemes[idx-1][-1])
                if pre_syllable_check:
                    pre_syllable = ord(morphemes[idx-1][-1])
                else:
                    pre_syllable = ord(morphemes[idx-1][-1]) - jong_number
                compose_syllable = pre_syllable + post_ja_syllable_index
                compose_syllable = chr(compose_syllable)
                results.append(compose_syllable)
                results.extend([x for x in post_morpheme])
            elif len(results) > 0 and "으" not in key_morphemes and results[-1] == "으" and morpheme == "아":  # 으 + 아  = 아(except "아" + "")
                del results[-1]
                results.append("아")
            elif len(results) > 0 and results[-1] == "하" and morpheme == "았":  # 하 + 았 = 했
                del results[-1]
                results.append("했")
            elif len(results) > 0 and results[-1] == "오" and morpheme == "았":  # 오 + 았 = 왔
                del results[-1]
                results.append("왔")
            elif len(results) > 0 and results[-1] == "가" and morpheme == "았":  # 가 + 았 = 갔
                del results[-1]
                results.append("갔")
            elif len(results) > 0 and results[-1] == "하" and morpheme == "아야":  # 하 + 아야 = 해야
                del results[-1]
                results.extend(["해", "야"])
            elif len(results) > 0 and results[-1] == "하" and morpheme == "아요":  # 하 + 아요 = 해요
                del results[-1]
                results.extend(["해", ""])
            elif len(results) > 0 and results[-1] == "시" and morpheme == "어요":  # 시 + 어요 = 세요
                del results[-1]
                results.extend(["세", "요"])
            elif len(results) > 0 and results[-1] == "되" and morpheme == "어도":  # 되 + 어도 = 돼도
                del results[-1]
                results.extend(["돼", "도"])
            elif len(results) > 0 and "".join(results[-2:]) == "그러" and morpheme == "어도":  # 그러 + 어도 = 그래도
                del results[-1]
                del results[-1]
                results.extend(["그", "래", "도"])
            elif len(results) > 0 and results[-1] == "서" and morpheme == "어서":  # 서 + 어서 = 서서
                del results[-1]
                results.extend(["서", "서"])
            elif len(results) > 0 and results[-1] == "말" and morpheme == "아":  # 말 + 아 = 마
                del results[-1]
                results.append("마")
            else:
                results.extend([x for x in morpheme])

        return "".join(results)

    def reform_ori_sent(self, sent, headers):
        eojul_lists = sent.strip().split(" ")

        results = {}
        temporary_duplicate_word = dict()
        ori_sent = self.restoreSymbol(" ".join(eojul_lists))
        check_lists = {i:-1 for i in range(len(headers))}

        start_eojul_idx = 0
        for node_idx in sorted(headers.keys()):
            cnt_node = headers[node_idx]
            results.setdefault(node_idx, cnt_node)
            compose_eojul = self.composeHangul(cnt_node[1].split(" "))

            for eojul_idx in range(start_eojul_idx, len(eojul_lists)):
                if compose_eojul == eojul_lists[eojul_idx]:
                    temporary_duplicate_word.setdefault(node_idx, eojul_idx)
                    start_eojul_idx = eojul_idx + 1
                    break
                elif compose_eojul in eojul_lists[eojul_idx]:
                    temporary_duplicate_word.setdefault(node_idx, eojul_idx)
                    if eojul_lists[eojul_idx][-1] == compose_eojul[-1]:
                        start_eojul_idx = eojul_idx + 1
                    else:
                        start_eojul_idx = eojul_idx
                    break

        for node_idx in range(len(results.keys())):
            if node_idx+1 == len(results.keys()):
                cnt_node = results[node_idx]
                cnt_node[0] = len(eojul_lists)-1
                check_lists[node_idx] = len(eojul_lists)-1
            elif node_idx in temporary_duplicate_word:
                cnt_node = results[node_idx]
                cnt_node[0] = temporary_duplicate_word[node_idx]
                check_lists[node_idx] = temporary_duplicate_word[node_idx]

        # check_lists (node_idx, eojul_idx)
        for key in sorted(check_lists):
            if check_lists[key] == -1:
                pre_key = key-1
                post_key = key+1

                if pre_key == -1:
                    results[key][0] = 0
                    check_lists[key] = 0

                elif post_key == len(headers):
                    results[key][0] = len(eojul_lists)-1
                    check_lists[key] = len(eojul_lists)-1

                elif check_lists[post_key] - check_lists[pre_key] == 2:
                    results[key][0] = check_lists[pre_key] + 1
                    check_lists[key] = check_lists[pre_key] + 1


        # reversed_check_lists (eojul_idx, [node_idx])
        reversed_check_lists = {}
        for i, j in check_lists.items():
            reversed_check_lists.setdefault(j, [])
            reversed_check_lists[j].append(i)

        if -1 in reversed_check_lists:
            no_match_lists = reversed_check_lists[-1]
            no_match_lists_pairs = []
            j = no_match_lists[0]
            temp = [j]
            for i in no_match_lists[1:]:
                if i - j == 1 and check_lists[j] == -1:
                    temp.append(i)
                elif i - j != 1:
                    no_match_lists_pairs.append(temp)
                    temp = [i]
                j = i
            if len(temp) > 0:
                no_match_lists_pairs.append(temp)

            for items in no_match_lists_pairs:
                pre_idx = check_lists[items[0] - 1]
                post_idx = check_lists[items[-1] + 1]
                if (len(items) + 1) == (post_idx-pre_idx):
                    cnt_idx = pre_idx + 1
                    for i in items:
                        results[i][0] = cnt_idx
                        check_lists[i] = cnt_idx
                        cnt_idx += 1

            reversed_check_lists = {}
            for i, j in check_lists.items():
                reversed_check_lists.setdefault(j, [])
                reversed_check_lists[j].append(i)

        for node_idx in sorted(results.keys()):
            node = results[node_idx]
            eojul_idx = node[0]
            compose_eojul = self.composeHangul(node[1].split(" "))
            if eojul_idx in reversed_check_lists and len(reversed_check_lists[eojul_idx]) == 1:
                if node_idx + 1 < len(results) and check_lists[node_idx+1] == -1:
                    node[0] = self.restoreSymbol(compose_eojul)
                    node[1] = self.restoreSymbol(node[1])
                else:
                    node[0] = self.restoreSymbol(eojul_lists[eojul_idx])
                    node[1] = self.restoreSymbol(node[1])

            elif eojul_idx in reversed_check_lists and len(reversed_check_lists[eojul_idx]) > 1:
                eojul_info = eojul_lists[eojul_idx]
                if compose_eojul in eojul_info:
                    node[0] = self.restoreSymbol(compose_eojul)
                    node[1] = self.restoreSymbol(node[1])
                    node[-1] = "SpaceAfter=No"
                else:
                    start = reversed_check_lists[eojul_idx][0]
                    for i in range(start, node_idx):
                        eojul_info = eojul_info.replace(self.composeHangul(results[i][1].split(" ")), "")
                    node[0] = self.restoreSymbol(eojul_info)
                    node[1] = self.restoreSymbol(node[1])
                    node[-1] = "SpaceAfter=No"

            elif check_lists[node_idx] == -1:
                pre_node_idx = node_idx - 1
                post_node_idx = node_idx + 1
                while check_lists[pre_node_idx] == -1:
                    pre_node_idx -= 1
                while check_lists[post_node_idx] == -1:
                    post_node_idx += 1

                pre_eojul_idx = check_lists[pre_node_idx]
                post_eojul_idx = check_lists[post_node_idx]

                set_eojul_idx = -1
                if len(reversed_check_lists[pre_eojul_idx]) > 1:
                    set_eojul_idx = pre_eojul_idx
                    check_lists[node_idx] = pre_eojul_idx

                    eojul_info = eojul_lists[set_eojul_idx]
                    for i in sorted(reversed_check_lists[set_eojul_idx]):
                        results[i][-1] = "SpaceAfter=No"
                        eojul_info = eojul_info.replace(self.composeHangul(results[i][1].split(" ")), "")

                    if eojul_info != "":
                        reversed_check_lists[set_eojul_idx].append(node_idx)
                        node[0] = self.restoreSymbol(eojul_info)
                        node[1] = self.restoreSymbol(node[1])
                        node[-1] = "SpaceAfter=No"
                    else:
                        set_eojul_idx = post_eojul_idx
                        check_lists[node_idx] = post_eojul_idx

                        eojul_info = eojul_lists[set_eojul_idx]
                        for i in sorted(reversed_check_lists[set_eojul_idx]):
                            results[i][-1] = "SpaceAfter=No"
                            eojul_info = eojul_info.replace(self.composeHangul(results[i][1].split(" ")), "")
                        reversed_check_lists[set_eojul_idx].append(node_idx)
                        node[0] = self.restoreSymbol(eojul_info)
                        node[1] = self.restoreSymbol(node[1])
                        node[-1] = "SpaceAfter=No"


                elif len(reversed_check_lists[post_eojul_idx]) > 1:
                    set_eojul_idx = post_eojul_idx
                    check_lists[node_idx] = post_eojul_idx

                    eojul_info = eojul_lists[set_eojul_idx]
                    for i in sorted(reversed_check_lists[set_eojul_idx]):
                        results[i][-1] = "SpaceAfter=No"
                        eojul_info = eojul_info.replace(self.composeHangul(results[i][1].split(" ")), "")

                    if eojul_info != "":
                        reversed_check_lists[set_eojul_idx].append(node_idx)
                        node[0] = self.restoreSymbol(eojul_info)
                        node[1] = self.restoreSymbol(node[1])
                        node[-1] = "SpaceAfter=No"
                    else:
                        set_eojul_idx = pre_eojul_idx
                        check_lists[node_idx] = pre_eojul_idx

                        eojul_info = eojul_lists[set_eojul_idx]
                        for i in sorted(reversed_check_lists[set_eojul_idx]):
                            results[i][-1] = "SpaceAfter=No"
                            eojul_info = eojul_info.replace(self.composeHangul(results[i][1].split(" ")), "")
                        reversed_check_lists[set_eojul_idx].append(node_idx)
                        node[0] = self.restoreSymbol(eojul_info)
                        node[1] = self.restoreSymbol(node[1])
                        node[-1] = "SpaceAfter=No"

                elif len(reversed_check_lists[pre_eojul_idx]) == 1 and len(reversed_check_lists[post_eojul_idx]) == 1 \
                        and check_lists[reversed_check_lists[post_eojul_idx][0]] - check_lists[reversed_check_lists[pre_eojul_idx][0]] == 1:
                    pre_node = results[reversed_check_lists[pre_eojul_idx][0]]
                    pre_eojul = eojul_lists[check_lists[reversed_check_lists[pre_eojul_idx][0]]]
                    if pre_eojul == self.composeHangul(pre_node[1].split(" ")):
                        set_eojul_idx = post_eojul_idx
                        check_lists[node_idx] = set_eojul_idx
                        reversed_check_lists[set_eojul_idx].append(node_idx)
                    else:
                        set_eojul_idx = pre_eojul_idx
                        check_lists[node_idx] = set_eojul_idx
                        reversed_check_lists[set_eojul_idx].append(node_idx)

                    if self.composeHangul(results[node_idx][1].split(" ")) in eojul_lists[set_eojul_idx]:
                        node[0] = self.restoreSymbol(self.composeHangul(results[node_idx][1].split(" ")))
                        node[1] = self.restoreSymbol(node[1])
                        node[-1] = "SpaceAfter=No"
                    else:
                        eojul_info = eojul_lists[set_eojul_idx]
                        for i in reversed_check_lists[set_eojul_idx]:
                            results[i][-1] = "SpaceAfter=No"
                            eojul_info = eojul_info.replace(self.composeHangul(results[i][1].split(" ")), "")
                        node[0] = self.restoreSymbol(eojul_info)
                        node[1] = self.restoreSymbol(node[1])
                        node[-1] = "SpaceAfter=No"

        reversed_check_lists = {}
        for i, j in check_lists.items():
            reversed_check_lists.setdefault(j, [])
            reversed_check_lists[j].append(i)

        for node_lists in reversed_check_lists.values():
            if len(node_lists) > 1:
                node_idx = sorted(node_lists)[-1]
                results[node_idx][-1] = "_"
            elif len(node_lists) == 1:
                node_idx = node_lists[0]
                results[node_idx][-1] = "_"

        result_reform = True
        if len(eojul_lists) > len(results):
            result_reform = False

        if len(reversed_check_lists) != len(eojul_lists):
            result_reform = False

        if result_reform:
            for j in check_lists.values():
                if j == -1:
                    result_reform = False
                    break

        if result_reform:
            for node_idx in sorted(results.keys()):
                node = results[node_idx]
                if node[0] == "":
                    result_reform = False
                    break

        return ori_sent, results, result_reform

    def assignDepRelation(self, headers):
        headinfo_lists = []
        for node_idx in sorted(headers.keys()):
            headinfo_lists.append([node_idx+1] + headers[node_idx])
        results = self.depRel_map.assign_sent_urel(headinfo_lists)
        results_dict = {}
        for item in results:
            results_dict.setdefault(item[0], item[1:])
        return results_dict