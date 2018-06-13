from UPosTagMap import *
from six import string_types
from hgtk.text import decompose, compose
import re, math

class Node(object):
    def __init__(self, label, index=-1, token=None):
        self.index = index
        self.label = label
        self.token = token
        self.head_index = -1
        self.head_label = None
        self.head_final_index = -1
        self.linear_check = False
        self.left_child = self.right_child = None

class ConstitiuentStructureTree(object):
    def __init__(self, rules):
        self.root = None
        self.length = 0
        self.rules = rules
        self.upostag_map = UPosTagMap()
        self.keymap = {
            "ᆫ":"ㄴ",
            "ᆯ":"ㄹ",
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
            "_":"_",
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
            "/*":6,
            ",*":6,
            "/SS,":3,
            "고EC,":1,
            "·*":2
        }

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


    def insert(self, stt):
        self.root = self._insert_value(self.root, stt)
        return self.root is not None

    def _insert_value(self, node, stt):
        if node is None:
            if isinstance(stt[0], string_types) and isinstance(stt[1][0], string_types):
                token = ''.join(stt[1])
                if token[0] == '+':
                    token = token[1:]
                node = Node(stt[0], index=self.length, token=token)
                self.length += 1
                return node
            else:
                node = Node(stt[0])

        try:
            node.left_child = self._insert_value(node.left_child, stt[1][0])
        except IndexError:
            return node

        try:
            node.right_child = self._insert_value(node.right_child, stt[1][1])
        except IndexError:
            return node

        return node

    def find(self, node, method):
        if method == 'rmn':
            if node.right_child is None:
                return node
            else:
                return self.find(node.right_child, method=method)
        elif method == 'lmn':
            if node.left_child is None:
                return node
            else:
                return self.find(node.left_child, method=method)

    def find_node_index(self, index):
        return self._find_node_index(self.root, index)

    def _find_node_index(self, node, index):
        if node is None:
            return -1

        if node.index == index:
            return node

        left_result = -1
        right_result = -1
        if node.left_child is not None:
            left_result = self._find_node_index(node.left_child, index)
        if node.right_child is not None:
            right_result = self._find_node_index(node.right_child, index)

        if left_result != -1:
            return left_result
        if right_result != -1:
            return right_result

        return -1

    def find_head(self, head_free=True):
        def _find_head(node):
            if node is None:
                pass
            else:
                _find_head(node.left_child)
                _find_head(node.right_child)
                if node.index == -1:
                    right_most_node = self.find(node.left_child, method='rmn')
                    left_most_node = self.find(node.right_child, method='lmn')

                    for parent_label_rule, left_label_rule, left_eojul_rule, right_label_rule, right_eojul_rule, left_context_rule, right_context_rule, linear_rule in self.rules:
                        left_context_node = None
                        right_context_node = None
                        if left_context_rule is not None and right_most_node.index - 1 >= 0:
                            left_context_node = self.find_node_index(right_most_node.index-1)
                        if right_context_rule is not None and left_most_node.index + 1 < self.length:
                            right_context_node = self.find_node_index(left_most_node.index+1)

                        if self.checkPattern(parent_label_rule, node.label) and \
                            self.checkPattern(left_label_rule, right_most_node.label) and \
                            self.checkPattern(left_eojul_rule, right_most_node, True) and \
                            self.checkPattern(right_label_rule, left_most_node.label) and \
                            self.checkPattern(right_eojul_rule, left_most_node, False) and \
                            self.checkPattern(left_context_rule, left_context_node, True) and \
                            self.checkPattern(right_context_rule, right_context_node, False):
                            if node.left_child.index == -1:
                                node.head_index = node.left_child.head_index
                            else:
                                node.head_index = node.left_child.index

                            if node.right_child.index == -1:
                                target_node = self.find_node_index(node.right_child.head_index)
                                target_node.head_index = node.head_index
                                target_node.head_label = node.right_child.label
                                if linear_rule:
                                    target_node.linear_check = True
                            else:
                                node.right_child.head_index = node.head_index
                                node.right_child.head_label = node.right_child.label
                                if linear_rule:
                                    node.right_child.linear_check = True
                            break

                    if node.head_index == -1:
                        if node.right_child.index == -1:
                            node.head_index = node.right_child.head_index
                        else:
                            node.head_index = node.right_child.index

                        if node.left_child.index == -1:
                            target_node = self.find_node_index(node.left_child.head_index)
                            target_node.head_index = node.head_index
                            target_node.head_label = node.left_child.label
                        else:
                            node.left_child.head_index = node.head_index
                            node.left_child.head_label = node.left_child.label

        def _find_head_final(node):
            if node is None:
                pass
            else:
                _find_head_final(node.left_child)
                _find_head_final(node.right_child)
                if node.index == -1:
                    right_most_node = self.find(node.left_child, method='rmn')
                    left_most_node = self.find(node.right_child, method='lmn')
                    cnt_linear_rule = False

                    for parent_label_rule, left_label_rule, left_eojul_rule, right_label_rule, right_eojul_rule, left_context_rule, right_context_rule, linear_rule in self.rules:
                        left_context_node = None
                        right_context_node = None
                        if left_context_rule is not None and right_most_node.index - 1 >= 0:
                            left_context_node = self.find_node_index(right_most_node.index - 1)
                        if right_context_rule is not None and left_most_node.index + 1 < self.length:
                            right_context_node = self.find_node_index(left_most_node.index + 1)

                        if self.checkPattern(parent_label_rule, node.label) and \
                                self.checkPattern(left_label_rule, right_most_node.label) and \
                                self.checkPattern(left_eojul_rule, right_most_node, True,) and \
                                self.checkPattern(right_label_rule, left_most_node.label) and \
                                self.checkPattern(right_eojul_rule, left_most_node, False) and \
                                self.checkPattern(left_context_rule, left_context_node, True) and \
                                self.checkPattern(right_context_rule, right_context_node, False) and \
                                linear_rule:

                            if left_most_node.head_final_index != -1:
                                if left_most_node.head_final_index < right_most_node.index:
                                    continue
                            left_most_node.head_final_index = right_most_node.index
                            cnt_linear_rule = True
                            break

                    if node.head_index == -1:
                        if node.right_child.index == -1:
                            node.head_index = node.right_child.head_index
                        else:
                            node.head_index = node.right_child.index

                        cnt_head_index = node.head_index
                        linear_head = self.find_node_index(cnt_head_index)
                        if not cnt_linear_rule and linear_head.head_final_index != -1:
                            while linear_head.head_final_index != -1:
                                linear_head = self.find_node_index(linear_head.head_final_index)

                            cnt_head_index = linear_head.index

                        if node.left_child.index == -1:
                            target_node = self.find_node_index(node.left_child.head_index)
                            target_node.head_index = cnt_head_index
                            target_node.head_label = node.left_child.label
                            if left_most_node.head_final_index != -1 and math.fabs(target_node.head_index - target_node.index) > 1:
                                target_node.head_index = target_node.index + 1
                        else:
                            node.left_child.head_index = cnt_head_index
                            node.left_child.head_label = node.left_child.label
                            if left_most_node.head_final_index != -1 and math.fabs(node.left_child.head_index - node.left_child.index) > 1:
                                node.left_child.head_index = node.left_child.index + 1
        if head_free:
            _find_head(self.root)
        else:
            _find_head_final(self.root)

    def get_lemma_and_xpostag(self, token):
        lemma_pos_check = re.compile("(.+?)/([A-Z]+)")

        result = lemma_pos_check.findall(token)
        lemmas = []
        for x in result:
            lemma = x[0] if len(x[0]) == 1 else x[0].replace('+', '')
            lemmas.append(lemma)
        poses = [x[1] for x in result]

        return ' '.join(lemmas), ' '.join(poses)

    def get_header(self):
        result = dict()

        def _post_order_traversal(node, headers):
            if node is None:
                pass
            else:
                _post_order_traversal(node.left_child, headers)
                _post_order_traversal(node.right_child, headers)
                if node.index != -1:
                    lemma, xpostag = self.get_lemma_and_xpostag(node.token)
                    if node.linear_check:
                        headers.setdefault(node.index, [node.token, lemma, " ".join(self.upostag_map.GetUPOS(xpostag)), xpostag, "-", node.index, "-", "-", "-"])
                    else:
                        if node.head_index == -1:
                            headers.setdefault(node.index, [node.token, lemma, " ".join(self.upostag_map.GetUPOS(xpostag)), xpostag, "-", 0, "ROOT", "-", "-"])
                        elif node.head_label is None:
                            headers.setdefault(node.index, [node.token, lemma, " ".join(self.upostag_map.GetUPOS(xpostag)), xpostag, "-", node.head_index+1, "-", "-", "-"])
                        else:
                            headers.setdefault(node.index, [node.token, lemma," ".join(self.upostag_map.GetUPOS(xpostag)), xpostag, "-", node.head_index+1, node.head_label, "-", "-"])
        _post_order_traversal(self.root, result)

        return result

    def fromstring(self, sent, brackets='()', node_pattern=None, leaf_pattern=None):
        if not isinstance(brackets, string_types) or len(brackets) != 2:
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
                # Beginning of a tree/subtree
                if token[0] == open_b:
                    label = token[1:].lstrip()
                    stack.append((label, []))
                # End of a tree/subtree
                elif token == close_b:
                    label, children = stack.pop()
                    stack[-1][1].append((label, children))
                # Leaf node
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
        cross_head_check = len(id_header_pairs)
        for idx, head_number in id_header_pairs:
            if cross_head_check > idx and cross_head_check < head_number:
                result = False
                break

            cross_head_check = head_number
        return result

    def check_cycle(self, headers):
        result = True
        id_header_pairs = [(idx+1, head[5], headers[head[5]-1][5]) for idx, head in sorted(headers.items(), key=lambda x:x[0]) if head[5] != 0]
        for idx, _, head_idx in id_header_pairs:
            if idx == head_idx:
                result = False
                break
        return result

    def edit_distance(self, first, second):
        first_len, second_len = len(first), len(second)

        if first_len > second_len:
            first, second = second, first
            first_len, second_len = second_len, first_len

        current = range(first_len + 1)

        for i in range(1, second_len + 1):
            previous, current = current, [i] + [0] * second_len

            for j in range(1, first_len + 1):
                add, delete = previous[j] + 1, current[j - 1] + 1
                change = previous[j - 1]
                if first[j - 1] != second[i - 1]:
                    change = change + 1

                current[j] = min(add, delete, change)

        return current[first_len]

    def reform_ori_sent(self, sent, headers):
        hanja_regex = "([\u2e80-\u2eff\u31c0-\u31ef\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fbf\uf900-\ufaff]+)"
        eojul_breplace_lists = [decompose(x) for x  in sent.strip().split(" ")]
        eojul_lists = [decompose(x).replace("ᴥ", "") for x  in sent.strip().split(" ")]
        sent_lists = sent.strip().split(" ")
        result_reform = True
        results = {}
        temporary_duplicate_word = dict()
        start_eojul_idx = 0
        hanja_lists = dict()
        for idx, eojul in enumerate(sent_lists):
            temp_regex = re.search(hanja_regex, eojul)
            if temp_regex:
                hanja_lists.setdefault(idx, temp_regex.group())

        for node_idx in sorted(headers.keys()):
            cnt_node = headers[node_idx]
            cnt_lemma_dec = decompose("".join(cnt_node[1].split(" "))).replace("ᴥ", "")
            results.setdefault(node_idx, cnt_node)

            for eojul_idx in range(start_eojul_idx, len(eojul_lists)):
                if cnt_lemma_dec == eojul_lists[eojul_idx]:
                    temporary_duplicate_word.setdefault(node_idx, eojul_idx)
                    start_eojul_idx = eojul_idx
                    break
                elif eojul_idx in hanja_lists and hanja_lists[eojul_idx] in cnt_node[1]:
                    temporary_duplicate_word.setdefault(node_idx, eojul_idx)
                    start_eojul_idx = eojul_idx
                    break

        for node_idx in range(len(results.keys())):

            if node_idx in temporary_duplicate_word:
                cnt_node = results[node_idx]
                cnt_node[0] = temporary_duplicate_word[node_idx]

        cnt_eojul_idx = 0

        temp = eojul_lists[cnt_eojul_idx]
        for node_idx in sorted(results.keys()):
            next_eojul_idx = cnt_eojul_idx + 1

            cnt_node = results[node_idx]
            cnt_lemma_dec = decompose("".join(cnt_node[1].split(" "))).replace("ᴥ", "")

            if isinstance(cnt_node[0], int):
                cnt_eojul_idx += 1
                continue

            if node_idx >= len(headers.keys()) - 1 or cnt_eojul_idx >= len(eojul_lists):
                cnt_node[0] = len(eojul_lists)-1
                continue

            if cnt_lemma_dec in eojul_lists[cnt_eojul_idx]:
                cnt_node[0] = cnt_eojul_idx
                temp = temp.replace(cnt_lemma_dec, "")

            elif re.match(re.escape(eojul_lists[cnt_eojul_idx]), cnt_lemma_dec):
                cnt_node[0] = cnt_eojul_idx
                temp = temp[1:]

            elif next_eojul_idx < len(eojul_lists) and cnt_lemma_dec in eojul_lists[next_eojul_idx]:
                cnt_node[0] = next_eojul_idx
                temp = eojul_lists[next_eojul_idx]
                temp = temp.replace(cnt_lemma_dec, "")
                cnt_eojul_idx += 1

            elif next_eojul_idx < len(eojul_lists) and re.match(re.escape(eojul_lists[next_eojul_idx]), cnt_lemma_dec):
                cnt_node[0] = next_eojul_idx
                cnt_eojul_idx += 1

            elif next_eojul_idx < len(eojul_lists) and len(eojul_lists[next_eojul_idx]) == 1:
                if len(cnt_lemma_dec) > len(eojul_lists[next_eojul_idx]):
                    cnt_node[0] = cnt_eojul_idx
                else:
                    cnt_node[0] = next_eojul_idx
                    cnt_eojul_idx += 1

            elif next_eojul_idx < len(eojul_lists) and self.edit_distance(cnt_lemma_dec, eojul_lists[cnt_eojul_idx]) < \
                    self.edit_distance(cnt_lemma_dec, eojul_lists[next_eojul_idx]):
                cnt_node[0] = cnt_eojul_idx

            elif next_eojul_idx < len(eojul_lists) and self.edit_distance(cnt_lemma_dec, temp) < \
                    self.edit_distance(cnt_lemma_dec, eojul_lists[next_eojul_idx]):
                cnt_node[0] = cnt_eojul_idx

            else:
                cnt_node[0] = next_eojul_idx
                cnt_eojul_idx += 1

        for node_idx in range(1, len(results) - 1):
            pre_node = results[node_idx-1]
            node = results[node_idx]
            next_node = results[node_idx+1]

            if next_node[0]-pre_node[0] == 1 and (math.fabs(pre_node[0]-node[0]) > 1 or math.fabs(next_node[0]-node[0]) > 1):
                cnt_lemma_dec = decompose("".join(node[1].split(" "))).replace("ᴥ", "")
                if self.edit_distance(cnt_lemma_dec, eojul_lists[pre_node[0]]) <= \
                    self.edit_distance(cnt_lemma_dec, eojul_lists[next_node[0]]):
                    node[0] = pre_node[0]
                else:
                    node[0] = next_node[0]

        for node_idx in range(len(results) - 1):
            node = results[node_idx]
            next_node = results[node_idx+1]

            if next_node[0] - node[0] > 1:
                result_reform = False

        temporary_eojul = dict()
        for node_idx in sorted(results.keys()):
            cnt_node = results[node_idx]
            temporary_eojul.setdefault(cnt_node[0], [])
            temporary_eojul[cnt_node[0]].append(node_idx)

        for eojul_idx in range(len(eojul_lists)):
            eojul = eojul_breplace_lists[eojul_idx].split("ᴥ")

            if eojul_idx not in temporary_eojul:
                result_reform = False
                break

            for cnt_idx, node_idx in enumerate(temporary_eojul[eojul_idx]):
                cnt_node = results[node_idx]
                cnt_lemma = "".join(cnt_node[1].split())
                compare_lemma = decompose(cnt_lemma).split("ᴥ")
                if cnt_idx == len(temporary_eojul[eojul_idx])-1:
                    idx = cnt_node[0]
                    cnt_node[0] = self.restoreSymbol(compose("ᴥ".join(eojul)))
                    cnt_node[1] = self.restoreSymbol(cnt_node[1])
                    if cnt_node[0] == "" and eojul_idx+1 in temporary_eojul and node_idx-1 > 0:
                        results[node_idx-1][-1] = "-"
                        temporary_eojul[eojul_idx+1].insert(0, temporary_eojul[eojul_idx][-1])
                    if idx in hanja_lists:
                        if hanja_lists[idx] in cnt_node[1].replace(" ", ""):
                            hanja_insert_index = cnt_node[1].replace(" ", "").find(hanja_lists[idx])
                            cnt_node[0] = cnt_node[0][:hanja_insert_index] + hanja_lists[idx] + cnt_node[0][hanja_insert_index:]
                    break

                temp = []
                for lemma in compare_lemma:
                    for i in range(len(eojul)):
                        if lemma == eojul[i]:
                            temp.extend(eojul[:i+1])
                            for j in range(i+1):
                                del eojul[0]
                            break
                        elif lemma in eojul[i]:
                            temp.append(lemma)
                            eojul[i] = eojul[i].replace(lemma, "")
                            break
                del_items = []
                for i in range(len(temp)):
                    if temp[i] != '' and len(temp[i]) == 1 and i > 0:
                        temp[i-1] += temp[i]
                        del_items.append(temp[i])
                for deli in del_items:
                    if deli in temp:
                        temp.remove(deli)
                idx = cnt_node[0]
                cnt_node[0] = self.restoreSymbol(compose("ᴥ".join(temp)))
                cnt_node[1] = self.restoreSymbol(cnt_node[1])
                cnt_node[-1] = "SpaceAfter=No"
                if idx in hanja_lists:
                    if hanja_lists[idx] in cnt_node[1].replace(" ", ""):
                        hanja_insert_index = cnt_node[1].replace(" ", "").find(hanja_lists[idx])
                        cnt_node[0] = cnt_node[0][:hanja_insert_index] + hanja_lists[idx] + cnt_node[0][hanja_insert_index:]

        ori_sent = self.restoreSymbol(sent)
        for node_idx in sorted(results.keys()):
            node = results[node_idx]
            if node[0] == "":
                result_reform = False
        return ori_sent, results, result_reform