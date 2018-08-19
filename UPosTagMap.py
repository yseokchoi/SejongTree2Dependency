import re


# 20180809 change
#    VCP --> VERB
#    VCN --> ADJ

class UPosTagMap(object):
    def __init__(self):

        
        self.NPOS = ('NNG', 'NNP', 'NNB', 'NR', 'NP', 'XR')
        self.VPOS = ('VV', 'VA', 'VCP', 'VCN')
        self.AUXPOS = ('VX', 'XSV', 'XSA')  # VCP VCN 제거
        self.MPOS = ('MM', 'MAG', 'MAJ')
        self.ETCPOS = ('IC', 'SW', 'SN')
        self.JPOS = ('JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC')
        self.EPOS = ('EP', 'EF', 'EC', 'ETN', 'ETM')
        self.EPOS_1 = ('EP', 'EF', 'EC', 'ETM')
        self.XPOS = ('XPN', 'XSN')
        self.SPOS = ('SF', 'SP', 'SS', 'SE', 'SO')
        self.XX = ('NF', 'NV', 'NA', 'SL', 'SH')

        self.UposMap = {
            'NNG': ('NOUN', 2),
            'NNP': ('PROPN', 1),
            'NNB': ('NOUN', 7),
            'NR': ('NOUN', 2),
            'NP': ('PRON', 5),
            'VV': ('VERB', 3),
            'VA': ('ADJ', 3),
            'VCP': ('ADJ', 3),   
            'VCN': ('ADJ', 3),              
            'VX': ('AUX', 6),
            'MM': ('DET', 4),
            'MAG': ('ADV', 4),
            'MAJ': ('CCONJ', 4),
            'IC': ('INJT', 7),
            'JKS': ('ADP', 8),
            'JKC': ('ADP', 8),
            'JKG': ('ADP', 8),
            'JKO': ('ADP', 8),
            'JKB': ('ADP', 8),
            'JKV': ('ADP', 8),
            'JKQ': ('ADP', 8),
            'JX': ('ADP', 8),
            'JC': ('CCONJ', 8),
            'EP': ('PART', 9),
            'EF': ('PART', 9),
            'EC': ('PART', 9),
            'ETN': ('PART', 9),
            'ETM': ('PART', 9),
            'XPN': ('PART', 7),
            'XSN': ('PART', 7),
            'XSV': ('VERB', 7),
            'XSA': ('ADJ', 7),
            'XR': ('NOUN', 2),
            'SF': ('PUNCT', 10),
            'SP': ('PUNCT', 10),
            'SS': ('PUNCT', 10),
            'SE': ('PUNCT', 10),
            'SO': ('PUNCT', 10),
            'SW': ('SYM', 10),
            'NF': ('X', 15),
            'NV': ('X', 15),
            'NA': ('X', 15),
            'SL': ('X', 7),
            'SH': ('X', 7),
            'SN': ('NUM', 7)}
        
        self.MM_DET = ('전', '이', '각', '여러', '그런', '그', '이런', '모든', '어느', '어떤', '온', '온갖', '모', '제', '아무', '수', '아무런', '무슨', '저', '뭇', '이런저런', '웬', '저런', '요런', '그깟', '이까짓', '그따위', '요', '뭔', '까짓', '고', '그까짓', '그런저런', '어는')
        self.MM_NUM = ('두', '한', '세', '몇', '서너', '몇몇', '네', ' 한두', '양', '스무', '만', '두세', '두어', '넉', '석', '두서너', '닷', '서')

    def remove_dup(self, wp):

        instring = wp.strip()
        while True:
            x = re.subn(r'(\b\w+)\s+\1', '\g<1>', instring)
            if x[1] == 0: break
            instring = x[0]

        return instring

    def remove_ss(self, wp):

        (z, c) = re.subn('S[FPSEO]', '', wp)
        if c:
            if z.strip():
                wp = self.remove_dup(z)
            else:
                wp = ''

        return wp

    def normalize_wp(self, wp):

        paren_seq = []

        wp = self.remove_dup(wp)
        seq = wp.split()

        if seq.count('SS') > 1:  # parenthesis
            m = re.search(r'SS ((S[A-Z] )+)SS', wp)
            if m:
                paren_wp = self.remove_ss(m.group(1).strip())
                paren_seq = paren_wp.split()
            wp = re.sub(r'SS (S[A-Z] )+SS', '', wp)

        wp = self.remove_ss(wp)
        seq = wp.split()

        while len(seq) > 1 and seq[-1] in self.JPOS + self.EPOS:
            seq.pop()

        while len(seq) > 1 and seq[0] in ('XPN',):
            seq.pop(0)

        return (seq, paren_seq)

    def NOUN_PRON_PROPN(self, wp_input):

        r = []
        
        (org_wp, org_seq, seq, paren_seq, lemma) = wp_input
        wp = self.remove_ss(org_wp)
        if not seq and paren_seq: seq = paren_seq 
        
        #print(org_wp, org_seq, seq, paren_seq, lemma)
        
        COND_1 = bool({'NNG', 'NNB', 'NR', 'XR'} & set(seq))
        COND_2 = bool({'XSA', 'XSV', 'VV', 'VA', 'VCP', 'VCN', 'VX'}.isdisjoint(seq))   
        COND_3 = bool({'NP', 'NNP'}.isdisjoint(seq))
        COND_4 = bool({'MAG'}.isdisjoint(seq))
        COND_8 = bool({'NNP'}.isdisjoint(seq))
        COND_7 = bool({'NNG', 'NNB'}.isdisjoint(seq))
        COND_9 = bool({'NNG', 'NNP'}.isdisjoint(seq))

               
        if 'JC' in org_seq and (org_seq[-1]=='JC' or (org_seq[org_seq.index('JC')+1] in self.SPOS)):
            r.append('CCONJ')
            
        # PROPN
        elif 'NNP' in seq and COND_2 and seq[-1] != 'MAG':
            r.append('PROPN')

        # NOUN
        elif seq and seq[0] == 'NNB' and COND_2 and COND_4 and COND_3:
            r.append('NOUN')

        elif 'NNG' in seq and COND_2 and COND_8 and COND_4:
            r.append('NOUN')

        elif len(seq) > 1 and seq[0] == 'SN' and 'NR' in seq and COND_4 and COND_2 and COND_7:
            r.append('NUM')  # NUM...
            
        elif seq and seq.count('NR') == len(seq): # NR only
            r.append('NUM')
            
        elif org_seq and ('NR' in org_seq) and ('MM' in org_seq) and (org_seq.count('NR') + org_seq.count('MM') == len(org_seq)) and lemma[org_seq.index('MM')] in self.MM_NUM:
            r.append('NUM')

        elif seq and seq[-1] in ('NNG', 'NR', 'XR') in seq and COND_8:
            r.append('NOUN')

        elif COND_1 and COND_2 and COND_4 and COND_3 and seq[0] != 'XSN':
            r.append('NOUN')

        elif wp.find('MM XSN') == 0 and COND_2:  # exception
            r.append('NOUN')
            
        # MAG+NNG            
        elif len(seq) == 2 and seq[0] == 'MAG' and seq[1] == 'NNG':
            r.append('NOUN')
                
        elif org_seq and ((org_seq[0] in ('SL', 'SH', 'SW', 'SO', 'SS', 'SE')) or ('SL' in org_seq) or ('SH' in org_seq)) and (org_seq[-1] in self.JPOS  + ('XSN',)) and COND_2 and COND_4:
            r.append('NOUN')
            
        # 띄어쓰기 오류 지난+해
        elif seq and seq[-1] == 'NNG' and seq[-2] == 'ETM':
            r.append('NOUN')

            # PRON
        elif 'NP' in seq and COND_2 and COND_4 and COND_9:
            r.append('PRON')

        return r

    def VERB_ADJ_AUX(self, wp_input):

        r = []
        (org_wp, org_seq, seq, paren_seq, lemma) = wp_input
        if not seq and paren_seq: seq = paren_seq

        COND_1 = bool(set(self.NPOS).isdisjoint(seq))
        COND_2 = bool({'XSA', 'VA', 'VCN', 'VCP'}.isdisjoint(seq))
        COND_3 = bool({'XSV', 'VV'}.isdisjoint(seq))   
        COND_4 = bool({'MAG'}.isdisjoint(seq))
        COND_5 = bool({'NNG', 'NR', 'XR', 'NP', 'NNP'}.isdisjoint(seq))
        COND_6 = bool({'NNG', 'NNB', 'NR', 'XR', 'NNP', 'MAG', 'NP'} & set(seq))
        COND_7 = bool(not set(paren_seq).difference({'SW', 'SL', 'SH', 'SN'}))
        COND_8 = bool({'NNG', 'NNB', 'NR', 'XR', 'NNP', 'NP', 'MAG', 'XSN', 'SN', 'SF', 'SW', 'SH', 'SL'} & set(seq))

        if seq and seq[0] not in self.AUXPOS:  # AUXPOS = ('VX', 'XSV', 'XSA')

            # VV
            if seq and seq[0] == 'VV' and COND_5 and COND_4:
                r.append('VERB')

            elif 'VV' in seq and COND_1 and COND_2 and COND_4:
                r.append('VERB')
                
            elif seq and seq[-1] == 'VV' and seq[0] != 'VA':
                r.append('VERB')

            elif seq and seq[-1] == 'XSV' and COND_6:
                r.append('VERB')
                
            elif seq and seq[-1] == 'VCP' and COND_8: # 2018-08-09
                r.append('ADJ')            
                
            elif seq and seq[-1] in ('VX', 'XSV') and 'VV' in seq and COND_2:
                r.append('VERB')

            elif seq and seq[-1] in ('VX', 'XSV') and 'XSV' in seq[:-2] and COND_2:
                r.append('VERB')

            elif seq and seq[0] == 'VV' and seq[-1] in ('VX', 'XSV', 'XSA'):
                r.append('VERB')

            elif seq and seq[0] == 'VCP' and COND_3:  # 2018-08-13
                r.append('ADJ')                

            elif len(seq) >= 2 and (seq[0] in self.NPOS + ('MAG',)) and seq[1] == 'XSV' and seq[-1] in ('VX', 'XSV', 'XSA', 'NNB', 'VCP'):
                r.append('VERB')
                
            elif len(seq) >= 2 and (seq[0] in self.NPOS + ('MAG',)) and seq[1] == 'VCP' and seq[-1] in ('VX', 'XSV', 'XSA', 'NNB'):
                r.append('ADJ')
                
            # NNG+VX+ETM
            # NNG+VX+EP+EF+SF
            elif len(seq) >=2 and seq[0] in self.NPOS and seq[1] in ('VX', 'XSV', 'VV'):
                r.append('VERB')
                
            elif len(org_seq) >= 2 and org_seq[-1] in self.EPOS_1 and org_seq[-2] in ('VX', 'XSV', 'VV'):
                r.append('VERB')
            
            # VV+EC+SS+SN+NNG+SS   VV+EC+SS+NNP+NNG+SS  VV+EC+SS+NNG+SS+SF
            # VV+EF+SF+SP+NNP+SP+NNG+SS+SN+NR+SN+NR+NNB+SS
            elif len(org_seq) >= 2 and (org_seq[0] in ('VV', 'VA')) and (org_seq[1] in self.EPOS_1) and (org_seq.count('SS') >= 2) and (org_seq[-1] in self.SPOS):                
                t_seq = org_seq[:org_seq.index('SS')]                
                if 'VV' in t_seq and bool(set(self.NPOS).isdisjoint(t_seq)) and bool({'XSA', 'VA', 'VCN'}.isdisjoint(t_seq)):
                    r.append('VERB') 
                if (('VA' in t_seq) or ('VCN' in t_seq)) and bool(set(self.NPOS).isdisjoint(t_seq)) and bool({'XSV', 'VV'}.isdisjoint(t_seq)):
                    r.append('ADJ')  
                     
                    

                # XR XSA ETN VCP
            # VA
            elif seq and seq[0] in ('VA', 'VCN') and COND_1 and COND_4:
                r.append('ADJ')

            elif 'VA' in seq and COND_1 and COND_3 and COND_4:
                r.append('ADJ')
                
            elif 'VCN' in seq and COND_1 and COND_3 and COND_4:
                r.append('ADJ')   
                
            elif 'VCP' in seq and COND_3 and COND_4:
                r.append('ADJ')                

            elif seq and seq[-1] in ('VA', 'VCN'):
                r.append('ADJ')

            elif seq and 'XSA' in seq and COND_6 and ({'NNG', 'NNB', 'NR', 'XR', 'NNP', 'MAG', 'NP'} & set(seq[:seq.index('XSA')])):
                r.append('ADJ')

            elif seq and seq[-1] in ('VX', 'XSA') and 'VA' in seq and COND_3:
                r.append('ADJ')

            elif seq and seq[-1] in ('VX', 'XSA') and 'XSA' in seq[:-2] and COND_3:
                r.append('ADJ')

            elif len(seq) > 1 and seq[-1] == 'VCN' and seq[-2] in ('NNG', 'MAG'):
                r.append('ADJ')

                # AUX
        if not r:
            if seq and seq[0] == 'VX' and COND_4 and COND_5 and (not paren_seq):
                r.append('AUX')   # modify 2018-08-04
                
            elif seq and seq[0] == 'XSV' and COND_4 and COND_5 and (not paren_seq):
                r.append('VERB')   # modify 2018-08-04                
                
            elif seq and seq[0] == 'XSA' and COND_4 and COND_5 and (not paren_seq):
                r.append('ADJ')   # modify 2018-08-04                                

            elif len(seq) > 1 and seq[0] == 'NNB' and seq[1] == 'VX' and COND_4 and COND_5 and (not paren_seq):
                r.append('AUX')

            elif seq and seq[0] == 'VX' and COND_4 and COND_5 and COND_7:
                r.append('AUX')
                
            elif seq and seq[0] == 'XSV' and COND_4 and COND_5 and COND_7:  # 2018-08-09
                r.append('VERB')
                
            elif seq and seq[0] == 'XSA' and COND_4 and COND_5 and COND_7: # 2018-08-09
                r.append('ADJ')
                
            # VX+EF+SF+SS+SS+NNP+SS+SS                
            elif org_seq and (org_seq[0] == 'VX') and (org_seq.count('SS') >= 2) and (org_seq[-1] in self.SPOS):                
                t_seq = org_seq[:org_seq.index('SS')]                
                if bool(set(self.NPOS).isdisjoint(t_seq)) and bool({'VV', 'XSV', 'XSA', 'VA', 'VCN'}.isdisjoint(t_seq)):
                    r.append('AUX')                    
                
                

        return r

    def ADV_DET_CCONJ(self, wp_input):

        r = []
        (org_wp, org_seq, seq, paren_seq, lemma) = wp_input
        if not seq and paren_seq: seq = paren_seq

        COND_1 = bool(set(self.NPOS).isdisjoint(seq))
        COND_3 = bool({'XSA', 'XSV', 'VV', 'VA', 'VCP', 'VCN'}.isdisjoint(seq))
        COND_4 = bool({'MAG'}.isdisjoint(seq))
        COND_6 = bool({'VCP', 'IC'}.isdisjoint(seq))        

        # 비교 순서 바꾸지 말 것...
        if seq and seq[0] in ('MAJ', 'MAG') and len(lemma)== 1 and lemma[-1] in ('및', '또는'):
            r.append('CCONJ')   # 2018-08-13
            
        elif seq and seq[0] == 'MAJ' and COND_6 and COND_1 and COND_3 and COND_4:
            r.append('SCONJ')  
            
        elif seq and seq[0] == 'MM' and lemma[0] in self.MM_NUM:
            r.append('NUM')
            
        elif seq and seq[0] == 'NR' and seq[-1] == 'MM' and lemma[-1] in self.MM_NUM:
            r.append('NUM')            
            
        elif seq and seq[0] == 'MM' and lemma[0] in self.MM_DET:
            r.append('DET') 
            
        elif seq and seq[0] == 'MM' and seq[-1] == 'MM' and lemma[-1] in self.MM_DET:
            r.append('DET')                    
            
        elif seq and seq[-1] == 'MM':
            r.append('ADJ')
            
                        
        elif seq and seq[0] == 'MAG' and seq[-1] == 'MAG' and COND_1 and COND_3:
            r.append('ADV')

        elif seq and seq[-1] == 'MAG':
            r.append('ADV')

        elif seq and seq[0] == 'MAG' and seq[-1] in ('XSN', 'IC') and COND_1 and COND_3:
            r.append('ADV')


        elif 'IC' in seq and COND_1 and COND_3 and COND_4:
            r.append('INTJ')

        return r

    def ADP_PART(self, wp_input):

        r = []
        (org_wp, org_seq, seq, paren_seq, lemma) = wp_input
        wp = self.remove_ss(org_wp)
        if not seq and paren_seq: seq = paren_seq

        COND_1 = bool(set(self.NPOS).isdisjoint(seq))
        COND_2 = bool({'XSA', 'XSV', 'VV', 'VA', 'VCP', 'VCN'}.isdisjoint(seq))
        COND_3 = bool({'MAG'}.isdisjoint(seq))

        if seq and seq[0] in self.EPOS and COND_1 and COND_3 and COND_2 and (not paren_seq):
            r.append('PART')

        elif wp == 'XPN':
            r.append('PART')

        elif seq and seq[0] == 'XSN' and COND_1 and COND_2 and COND_3:
            r.append('PART')

        elif seq and (not paren_seq) and seq[0] == 'JC' and COND_1 and COND_3 and COND_2:
            r.append('CCONJ')
            
        elif seq and (not paren_seq) and seq[0] in self.JPOS and COND_1 and COND_3 and COND_2:
            r.append('ADP')

        return r

    def SYMBOL(self, wp_input):

        r = []
        (org_wp, org_seq, seq, paren_seq, lemma) = wp_input
        if not seq and paren_seq: seq = paren_seq

        COND_1 = bool(not set(org_seq).difference(self.SPOS))
        COND_2 = bool(set(self.NPOS).isdisjoint(seq))
        COND_3 = bool({'XSA', 'XSV', 'VV', 'VA', 'VCP', 'VCN'}.isdisjoint(seq))
        COND_4 = bool({'MAG'}.isdisjoint(seq))
        COND_5 = bool({'NNG', 'XR', 'NNP', 'NNB'}.isdisjoint(seq))
        COND_6 = bool(set(self.JPOS).isdisjoint(seq))

        if COND_1:
            r.append('PUNCT')            
            
        elif len(org_seq) >= 2 and (bool({'SL', 'SH'} & set(org_seq))) and (org_seq[-1] in self.JPOS or org_seq[-2] in self.JPOS) and COND_3 and COND_4:
            r.append('NOUN')

        elif (seq and seq[0] in ('SL', 'SH')) and COND_2 and COND_3 and COND_4:
            r.append('X')

            # SN | SN + NR && ^NNB
        elif (seq and (seq[0] == 'SN' or 'SN' in seq)) and COND_3 and COND_5:
            r.append('NUM')

        elif COND_2 and COND_3 and COND_4 and paren_seq and paren_seq[0] == 'SN':
            r.append('NUM')

        elif (paren_seq and paren_seq[0] in ('SL', 'SH')) and COND_2 and COND_3 and COND_4 and COND_6:
            r.append('X')
            
        elif (seq and seq[0] in ('SL', 'SH')) and COND_2 and COND_3 and COND_4 and COND_6:
            r.append('X')
            
        elif seq and seq[0] == 'SW' and 'SN' not in seq and COND_2 and COND_3 and COND_4:
            r.append('SYM')


        elif 'Q' in seq and COND_2 and COND_3 and COND_4 and COND_6:
            r.append('X')

        elif seq and seq[0] == 'NA':
            r.append('X')

        return r

    def get_default_POS(self, wp, org_wp):

        r = []
        seq = wp.split()
        while seq and seq[-1] in self.SPOS + self.JPOS + self.EPOS + ('XSN',):  # VCP 제거해야 할 듯
            seq.pop()
        if seq:
            if seq[-1] == 'VV':
                r.append('VERB')
            if seq[-1] == 'VCP':
                r.append('ADJ')                
            elif seq[-1] == 'VA':
                r.append('ADJ')
            elif seq[-1] == 'VCN':
                r.append('ADJ')                
            elif seq[-1] in ('NNG', 'NNB', 'NR', 'XR'):
                r.append('NOUN')
            elif seq[-1] == 'NNP':
                r.append('PROPN')
            elif seq[-1] == 'NP':
                r.append('PRON')
        if not r and seq:
            if seq[0] == 'VV':
                r.append('VERB')
            if seq[0] == 'VCP':
                r.append('ADJ')                
            elif seq[0] == 'VA':
                r.append('ADJ')
            elif seq[0] == 'VCN':
                r.append('ADJ')                
            elif seq[0] in ('NNG', 'NNB', 'NR', 'XR'):
                r.append('NOUN')
            elif seq[0] == 'NNP':
                r.append('PROPN')
            elif seq[0] == 'NP':
                r.append('PRON')
        if not r and seq:
            if seq[-1] == 'XSV':
                r.append('VERB')
            elif seq[-1] == 'XSA':
                r.append('ADJ')
            elif seq[-1] == 'MAG':
                r.append('ADV')
        if not r:
            r_list = []
            for x in org_wp.split():
                if x in self.UposMap:
                    r_list.append([x, self.UposMap[x][0], self.UposMap[x][1]])
            r_list_sorted = sorted(r_list, key=lambda x: x[2])
            if r_list_sorted:
                r.append(r_list_sorted[0][1])
        if not r:
            r.append('X')

        return r

    def GetUPOS(self, wp, lemma):

        org_wp = wp
        (norm_seq, paren_seq) = self.normalize_wp(wp)
        wp = self.remove_ss(org_wp)

        wp_in = (org_wp, org_wp.split(), norm_seq, paren_seq, lemma.split())

        result = []

        if not result: result += self.NOUN_PRON_PROPN(wp_in)
        if not result: result += self.VERB_ADJ_AUX(wp_in)
        if not result: result += self.ADV_DET_CCONJ(wp_in)
        if not result: result += self.ADP_PART(wp_in)
        if not result: result += self.SYMBOL(wp_in)

        
        # default rule
        if not result:
            result = self.get_default_POS(wp, org_wp)            

        return result