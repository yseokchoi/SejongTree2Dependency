# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 21:28:25 2018

@author: kong_
"""

class UDepRelMap(object):
    
    def __init__(self, OPTION):
        
        self.LEMMA = 2
        self.UPOS  = 3
        self.XPOS  = 4
        self.HEAD  = 6
        self.KREL  = 7
                
        self.NP_UPOS = ('NOUN', 'PRON', 'PROPN', 'NUM', 'X') #, 'SYM')
        self.VP_UPOS = ('VERB', 'ADJ', 'AUX')        
        
        self.NPOS = ('NNG', 'NNP', 'NNB', 'NR', 'NP', 'XR')
        self.JPOS = ('JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC')

        
        self.HEAD_FINAL = OPTION
        
        self.SEP = '+'
        self.DEFAULT_DEPREL = 'dep'


    def HAS_JOSA(self, pos_string):
        
        pos_list = pos_string.split(self.SEP)
        
        return bool(set(self.JPOS) & set(pos_list))
        
    def GuessDepRel(self, head_dep_info):
        
        (cd, hd, cd_lemma, hd_lemma, cd_upos, hd_upos, cd_xpos, hd_xpos, krel, hd_krel) = head_dep_info
    
        
        if cd + 1 == hd and cd_upos == hd_upos == 'NOUN':
            return 'nmod'
        
            
        # EXCEPTION...        
        if self.HEAD_FINAL:
            if cd_upos == 'PART' and hd_upos == 'ADP': return 'advcl' # ~며 ~이라고                
            
      
        # 생략된 병렬 구문....
        if krel in ('S', 'VP', 'S_OBJ', 'S_AJT', 'S_CMP', 'VP_AJT') or krel.endswith('_CNJ'):  
            
            cd_xpos_list = cd_xpos.split(self.SEP)
            hd_xpos_list = hd_xpos.split(self.SEP)
            cd_xpos_first = cd_xpos_list[0]
            hd_xpos_first = hd_xpos_list[0]
        
            while len(cd_xpos_list) > 1 and cd_xpos_list[-1] in ('SP', 'SF'):
                cd_xpos_list.pop()
            while len(hd_xpos_list) > 1 and hd_xpos_list[-1] in ('SP', 'SF'):
                hd_xpos_list.pop()
                
            if cd_upos == hd_upos and cd_xpos_first == hd_xpos_first and cd_xpos.endswith('SP'):
                return 'conj'
            if cd_upos == hd_upos and cd_xpos == hd_xpos:
                return 'conj'        
            if cd_upos == hd_upos and cd_xpos_first == hd_xpos_first and cd_xpos_list == hd_xpos_list:
                return 'conj'
            if cd_upos == hd_upos and cd_xpos_list[-1] == hd_xpos_list[-1] and cd_xpos.endswith('SP'):
                return 'conj'            
            if cd_upos in ('NOUN', 'PROPN', 'NUM') and hd_upos in ('NOUN', 'PROPN', 'NUM') and cd_xpos.endswith('SP'):
                return 'conj'
            
            cd_lemma_list = cd_lemma.split()
            hd_lemma_list = hd_lemma.split()
            
            if cd_lemma_list[-1] == hd_lemma_list[-1] and cd_lemma_list[-1] != ',':
                return 'conj'
            if len(cd_lemma_list) > 1 and cd_lemma_list[-1] == ',' and cd_lemma_list[-2] == hd_lemma_list[-1]:
                return 'conj'
            
            
        if krel == 'S':  # S를 SYMBOL로 생각한 태깅 오류...                                                           
            if cd_upos == 'DET' and hd_upos == 'NOUN' and cd + 3 > hd:
                return 'amod'
            if hd_upos == 'NOUN' and hd_xpos.endswith('SP'):
                return 'advcl'
            
        ######  Ignore KREL
        cd_xpos_list = cd_xpos.split(self.SEP)
        hd_xpos_list = hd_xpos.split(self.SEP)
            
        if cd_upos in ('NUM') and hd_upos in ('NOUN', 'PROPN', 'NUM'): return 'nummod' 
        if cd_upos in ('NOUN', 'PROPN') and hd_upos in ('NOUN', 'PROPN', 'NUM') and cd_xpos_list[-1] in self.NPOS + ('XSN',): return 'nmod' 
        if cd_upos in self.NP_UPOS +('ADP',) and cd_xpos.endswith('JKG'): return 'nmod'        
        
        if cd_upos in self.NP_UPOS+('ADP',) and cd_xpos.endswith('JKB') and (hd_upos in self.VP_UPOS): return 'obl'
        if cd_upos in self.NP_UPOS and cd_xpos.endswith('JKB') and hd_upos in self.NP_UPOS : return 'obl'
        if cd_upos in ('ADP', 'PART') and  'JKB' in cd_xpos_list and hd_upos =='ADV' : return 'obl'        
        if cd_upos in ('NOUN', 'ADJ') and hd_upos == 'ADV': return 'obl'     
        if cd_upos in ('NOUN', 'PROPN') and cd_xpos_list[-1] in self.NPOS + ('XSN',) and hd_upos in ('VERB', 'ADJ'): return 'obl'
        if cd_upos in ('NOUN', 'PROPN', 'ADP') and cd_xpos_list[-1] == 'JX' and hd_upos in self.VP_UPOS: return 'obl'
        if cd_upos == 'ADJ' and cd_xpos_list[0] == 'VCP' and cd_xpos_list[-1] == 'EC' and hd_xpos_list[0] == 'NNB': return 'obl'
        if cd_upos == 'INTJ' and hd_upos in self.VP_UPOS: return 'obl'
        
        
        if (cd_xpos.endswith('JKO') or cd_xpos.endswith('JKO+SP')) and hd_upos in self.VP_UPOS: return 'obj'        
        
        if cd_upos in ('DET', 'ADJ') and (cd_xpos_list[-1] == 'MM' or cd_xpos.endswith('MM+SP')): return 'amod'
        if cd_upos in ('VERB', 'PART', 'AUX', 'ADJ') and cd_xpos.endswith('ETM') : return 'acl'

        
        if hd_upos == 'ADJ' and hd_xpos.startswith('VCP'): return 'xcomp'
        if cd_upos == 'ADV' and hd_upos in ('NOUN', 'PROPN'): return 'advmod'
        
        if cd_upos == 'PART' and cd_xpos.endswith('EC') : return 'advcl' 
        if cd_upos in self.VP_UPOS and cd_xpos.endswith('EC') and hd_upos in self.VP_UPOS: return 'advcl' 
        

        if cd_xpos_list[-1] not in self.JPOS and (hd_upos == 'ADP' or hd_xpos_list[-1] == 'JC'): return 'dep'
        
        if cd_upos == 'NOUN' and hd_upos == 'SCONJ': return 'conj'
        
        

        
        return self.DEFAULT_DEPREL
    
        
    def assign_urel(self, head_dep_info):
        
        cd, hd, cd_lemma, hd_lemma, cd_upos, hd_upos, cd_xpos, hd_xpos, krel, hd_krel = head_dep_info
        
        COND_1 = bool({'NNG', 'NNB', 'NNP', 'NR', 'XR', 'ETN', 'SN', 'NP'} & set(cd_xpos.split(self.SEP)))
        COND_2 = bool({'NNG', 'NNB', 'NNP', 'NR', 'XR', 'ETN', 'SN', 'NP'} & set(hd_xpos.split(self.SEP)))

        COND_3 = bool({'VV', 'VA', 'VX', 'XSV', 'XSA', 'VCP', 'VCN'} & set(cd_xpos.split(self.SEP)))
        COND_4 = bool({'VV', 'VA', 'VX', 'XSV', 'XSA', 'VCP', 'VCN'} & set(hd_xpos.split(self.SEP)))

        COND_vh = bool((hd_upos in self.VP_UPOS) or COND_4)
        COND_vc = bool((cd_upos in self.VP_UPOS) or COND_3)
        
        COND_vh_strict = bool((hd_upos in self.VP_UPOS) and COND_2==False)
        COND_vc_strict = bool((cd_upos in self.VP_UPOS) and COND_1==False)

        COND_nh = bool((hd_upos in self.NP_UPOS) or COND_2)
        COND_nc = bool((cd_upos in self.NP_UPOS) or COND_1)
        
        COND_nh_strict = bool((hd_upos in self.NP_UPOS) and COND_4==False)
        COND_nc_strict = bool((cd_upos in self.NP_UPOS) and COND_3==False)

        new_rel = None
               
        if krel == 'ROOT':
            return 'root'
        
        if self.HEAD_FINAL == 0 and krel == '_':
            if hd + 1 == cd: return 'aux'


        if cd_upos == 'CCONJ':
            if cd_xpos.startswith('JC'): return 'cc'
            elif bool(set(cd_xpos.split(self.SEP)) & {'MAJ', 'MAG'}) and cd_xpos.find('JC') == -1: return 'cc'
            else: return 'conj'
        if cd_upos == 'SCONJ' and krel.find('_CNJ') == -1: return 'mark'
        if self.HEAD_FINAL == 0 and cd_upos == 'ADP' and hd < cd: return 'case'
        if self.HEAD_FINAL == 0 and cd_upos == 'PUNCT': return 'punct'
        if cd_upos == hd_upos == 'PUNCT': return 'punct'
        
            
        ### NP  ; 거의 모든 경우가 다 발생
        if krel == 'NP':   # 비교순서 중요

            if cd_upos == 'NUM': new_rel = 'nummod' 
            elif COND_nc and COND_nh: new_rel = 'nmod'                
            elif COND_nc and hd_xpos.startswith('VCP'):  new_rel = 'xcomp'  # '이다'의 보어
            elif COND_nc and hd_xpos.startswith('XSN+VCP'):  new_rel = 'xcomp'  # '이다'의 보어
            elif cd_xpos == 'XPN' and COND_nh: new_rel = 'amod'                
            elif cd_upos == 'PART' and cd_xpos.startswith('XSN') and hd_xpos.startswith('VCP'): new_rel = 'xcomp'
            elif cd_upos == 'PART' and cd_xpos.endswith('XSN') and COND_nh: new_rel = 'nmod'                
            elif cd_upos == 'PART' and cd_xpos.startswith('E') and COND_vh: new_rel = 'advcl'
            elif COND_nc and hd_xpos.startswith('XSN') and hd_xpos.find('VCP') == -1: new_rel = 'dep'
            elif cd_upos == 'ADV' and COND_nh: new_rel = 'advmod'
            elif cd_upos == 'ADV' and hd_upos in self.VP_UPOS: new_rel = 'advmod'
            elif COND_nc and COND_vh_strict: new_rel = 'obl'                
            elif COND_nc_strict and hd_upos in ('ADV', 'DET', 'INTJ'): new_rel = 'obl'
            elif COND_nc_strict and cd_xpos.endswith('SP') == False and COND_vh_strict: new_rel = 'obl'
            elif cd_xpos == 'NR' and hd_xpos == 'MM': new_rel = 'nummod'
            elif cd_upos == 'NOUN' and hd_upos == 'NOUN': new_rel = 'nmod'
            elif cd_upos == 'DET' and COND_nh: new_rel = 'det'
            elif COND_nc and hd_upos == 'CCONJ': new_rel = 'conj'   # TaggingError
            elif COND_nc and hd_upos == 'SCONJ': new_rel = 'conj'   # TaggingError
                                                


        ### VP  S  VNP
        if krel in ('S', 'VP', 'VNP', 'S_PRN', 'VP_PRN'):  # 비교순서 중요
            if COND_vc and hd_upos == 'PART': new_rel = 'dep'  # must be 'AND'             
            elif cd_upos == 'SCONJ': new_rel = 'mark'
                
            elif COND_vc and COND_vh:  new_rel = 'advcl'
            elif COND_vc and COND_nh and hd_xpos.endswith('SP'): new_rel = 'advcl'  # ~하다 생략된 형태
            elif COND_nc and cd_xpos.endswith('SP') and COND_vh: new_rel = 'advcl'            
            elif cd_upos == 'PART' and cd_xpos.startswith('E') and COND_vh: new_rel = 'advcl'
            
            elif COND_vc and COND_nh_strict and cd_xpos.endswith('+ETN'): new_rel ='acl' # 먹기 때문에
            elif COND_vc and COND_nh_strict and cd_xpos.endswith('+ETM'): new_rel ='acl' # 탈 수  (tagging error)
            
            elif COND_vc: new_rel = 'advcl'
            elif cd_upos == 'ADV' and COND_vh: new_rel = 'advmod'
            
            elif COND_nc_strict and (hd_upos == 'ADJ' and hd_xpos.startswith('VCP')): new_rel = 'xcomp'
            elif COND_nc_strict and (COND_vh_strict or hd_upos == 'ADJ'): new_rel = 'obl'
            elif cd_upos == 'ADP' and cd_xpos.endswith('JX') and COND_vh: new_rel = 'obl'
            
           
                
        ## _SBJ
        if krel.find('_SBJ') > 0:
            if krel == 'NP_SBJ' or krel == 'LP_SBJ':
                if COND_nc or COND_vh: new_rel = 'nsubj'
                elif cd_upos == 'ADP' :  new_rel = 'nsubj'  # head-final quotation  
                    
            if krel in ('VP_SBJ', 'S_SBJ', 'VNP_SBJ'):
                if COND_vc or COND_vh: new_rel = 'csubj'
                elif cd_upos == 'ADP': new_rel = 'csubj'
                elif krel == 'S_SBJ' and cd_upos == 'NOUN' and cd_xpos.endswith('JKS'): new_rel = 'nsubj'
                    
            if krel == 'AP_SBJ':
                if cd_upos == 'ADV' and COND_vh: new_rel = 'advmod'
            if krel == 'DP_SBJ':
                if cd_upos == 'NOUN'  or cd_xpos.endswith('JKS'): new_rel = 'nsubj'
            
        
        ## _OBJ
        if krel.find('_OBJ') > 0:
            if krel == 'NP_OBJ':
                if COND_nc or COND_vh: new_rel = 'obj'
                elif cd_upos == 'ADP': new_rel = 'obj'
                    
            if krel == 'DP_OBJ':
                if cd_upos == 'NOUN': new_rel = 'obj'
            if krel == 'AP_OBJ':
                if cd_upos == 'ADV':new_rel = 'obj'
            if krel in ('VP_OBJ', 'S_OBJ', 'VNP_OBJ'):
                if COND_vc or COND_vh: new_rel = 'ccomp'
                if cd_upos == 'ADP': new_rel = 'obj'
                    
            if krel == 'IP_OBJ':
                if cd_xpos.endswith('JKO'): new_rel = 'obj'

        ## _CMP
        if krel.find('_CMP') > 0:
            if krel == 'NP_CMP':
                if COND_nc or COND_vh: new_rel = 'xcomp' #####&&&&&&&&&& TO_DO                      
                elif cd_upos == 'ADP': new_rel = 'xcomp'
                    
            elif krel == 'AP_CMP':
                if cd_upos == 'ADV': new_rel = 'advmod'
                elif cd_upos == 'ADP': new_rel = 'ccomp'  # "하나만 더 줘"하고 안달을 했다
                    
            elif krel in ('S_CMP', 'VP_CMP', 'VNP_CMP', 'IP_CMP'):
                if hd_upos == 'PART': new_rel = 'dep'
                elif cd_upos == 'ADP': new_rel = 'ccomp'
                elif COND_vc or COND_vh:  new_rel = 'ccomp' ###&&&&&&&&&&&& TO_DO                    
                elif hd_krel == 'ROOT': new_rel = 'ccomp'
            else:
                if cd_upos == 'ADP' and COND_vh: new_rel = 'ccomp'                
                


        ## _MOD
        if krel.find('_MOD') > 0:
            
            if krel == 'NP_MOD':
                if cd_upos == 'NUM': new_rel = 'nummod'            
                elif COND_nc and COND_nh: new_rel = 'nmod'                
                elif COND_nc and (cd_xpos.endswith('+ETN') or cd_xpos.endswith('+ETM')) and COND_nh_strict: new_rel = 'acl'
                elif COND_nc_strict and hd_upos == 'ADV': new_rel = 'nmod'
                elif cd_upos == 'ADP' and COND_nh: new_rel = 'nmod'
                elif cd_xpos.startswith('VCP') and COND_nh_strict: new_rel = 'acl'
                elif cd_upos == 'NOUN' and hd_upos == 'ADP': new_rel = 'nmod'
                elif COND_nh and cd_xpos.endswith('JKG') and COND_3 == False: new_rel = 'nmod'
                elif COND_nh and cd_xpos.endswith('JKG') and COND_3: new_rel = 'acl'
                elif COND_nc_strict: new_rel = 'nmod'
                elif COND_vc_strict and COND_nh_strict: new_rel = 'acl'                
                elif cd_upos == 'ADP' and hd_upos == 'ADP':  new_rel = 'nmod'  # ~의 ~()는 
                
            elif krel in ('S_MOD', 'VP_MOD', 'VNP_MOD'):
                if COND_vc or COND_nh: new_rel = 'acl'

            elif krel == 'DP_MOD':
                if cd_upos == 'DET' and COND_nh: new_rel = 'amod'
                elif cd_upos == 'NOUN' and COND_nh: new_rel = 'nmod'   
                
            elif krel == 'AP_MOD':
                if cd_upos == 'ADV' or COND_nh: new_rel = 'advmod'
                
                    
            
        if krel.find('_AJT') > 0:        
            if krel == 'NP_AJT':
                #if COND_nc_strict and COND_nh_strict and self.HAS_JOSA(cd_xpos) == False: new_rel = 'nmod'
                if COND_nc or COND_vh: new_rel = 'obl'  #####&&&&&&&& TO_DO                    
                elif cd_upos == 'ADP': new_rel = 'obl'
                    
            elif krel == 'DP_AJT':
                if COND_nc and COND_vh:  new_rel = 'obl' # must be AND                    
                elif cd_upos == 'DET' and (COND_nh or hd_upos == 'ADV'): new_rel = 'amod'
                
            elif krel == 'AP_AJT':
                if cd_upos == 'ADV' or COND_vh: new_rel = 'advmod'  ## TO_DO
                                        
            elif krel in ('S_AJT', 'VP_AJT', 'VNP_AJT'):
                if COND_vc or COND_vh:  new_rel = 'advcl' ## TO_DO
                                       
            elif krel == 'IP_AJT':
                if cd_xpos.find('JKB') > 0 and COND_vh: new_rel = 'obl'                    
            else:
                if COND_vh: new_rel = 'obl'

            
        if krel.find('_CNJ') > 0:        
            if krel == 'NP_CNJ':
                if cd_upos == 'SCONJ' and COND_nh: new_rel = 'cc' 
                elif cd_upos == 'CCONJ': new_rel = 'conj'
                elif COND_nc or COND_nh: new_rel = 'conj'
                elif cd_upos == hd_upos: new_rel = 'conj'
                elif cd_upos in ('PUNCT', 'ADP'): new_rel = 'conj'
                    
            if krel in ('VP_CNJ', 'S_CNJ', 'VNP_CNJ'): new_rel = 'conj'  # 품사 조건을 보지 않았음
                                
            if cd_xpos.endswith('JC'): new_rel = 'conj'
                
        ## DP  
        if krel == 'DP':
            if cd_upos == 'DET': new_rel = 'det'
            elif cd_upos == 'ADJ': new_rel = 'amod'
            elif cd_upos == 'NUM': new_rel = 'nummod'
            elif cd_upos in self.NP_UPOS and hd_upos in self.NP_UPOS : new_rel = 'nmod'                                    
                    
        ## AP
        if krel == 'AP':
            if cd_upos == 'CCONJ': new_rel = 'cc'
            elif cd_upos == 'SCONJ': new_rel = 'mark'                    
            elif cd_upos in ('ADV', 'INTJ'): new_rel = 'advmod'   ## TO_DO
            elif cd_upos in self.VP_UPOS and hd_upos in self.VP_UPOS: new_rel = 'advcl'                    

                    
        if krel.startswith('IP') or krel.find('_INT') > 0:
            
            if krel in ('IP', 'IP_INT', 'NP_INT', 'S_INT'):
                if cd_upos in ('INTJ', 'NOUN', 'PRON', 'PROPN', 'X'): new_rel = 'vocative'
                elif cd_xpos.find('JKV') > 0: new_rel = 'vocative'
                
            if krel in ('VP_INT', 'VNP_INT'):
                if cd_upos == hd_upos == 'VERB': new_rel = 'advcl'            
                
        ## NP_PRN
        if krel == 'NP_PRN':
            if hd < cd: new_rel = 'appos'
            elif COND_nc and COND_nh and hd > cd: new_rel = 'nmod'
            elif hd > cd and COND_vh: new_rel = 'obl'   ## 이거 맞을까요?

        
        ## rigid head-final vs. nonrigid head-final
        if self.HEAD_FINAL == 0 and krel.startswith('X'):
            if cd_upos in ('PUNCT', 'SYM'): new_rel = 'punct'
            elif cd_upos == 'CCONJ' : new_rel = 'cc'
            elif cd_upos == 'ADP' and hd < cd: new_rel = 'case'
            elif cd_upos == 'PART' and cd_xpos.startswith('E'): new_rel = 'mark'
            elif cd_upos == 'PART' and cd_xpos.startswith('XSN') and hd < cd: new_rel = 'dep'
            
            elif krel == 'X_SBJ' and hd > cd and cd_upos != 'ADP': new_rel = 'nsubj' # tagging error.... 
            elif krel == 'X_SBJ' and hd < cd and cd_upos != 'ADP' and COND_nh:  new_rel = 'appos' # tagging error...                        
            elif krel == 'X_AJT' and hd > cd : new_rel = 'obl'

            elif krel == 'X_CMP':
                if hd > cd and COND_vc and COND_vh:  new_rel = 'advcl'
                elif hd > cd and COND_nc and COND_vh: new_rel = 'xcomp'   ########

        if self.HEAD_FINAL == 1 and krel.startswith('X'):
            if cd_upos in ('PUNCT', 'SYM'): new_rel = 'punct'
            elif krel == 'X_SBJ' and cd_upos == 'ADP': new_rel = 'nsubj'
            elif krel == 'X_CNJ' and cd_upos == 'CCONJ': new_rel = 'conj'
            elif krel == 'X_AJT' and cd_upos == 'ADP': new_rel = 'obl'
            elif krel == 'X_CMP':
                if cd_upos == 'ADP' and hd_upos == 'ADJ' and hd_xpos.startswith('VCN'): new_rel = 'xcomp'
                elif cd_upos in ('VERB', 'ADJ') and COND_vh: new_rel = 'advcl'
            elif krel == 'X_MOD' and cd_upos == 'PART' and COND_nh: new_rel = 'acl'
                

        if krel.startswith('Q'): new_rel = 'parataxis'
            
        # 마지막에 안되어 있으면 할당하자...
        if new_rel == None and cd_upos == 'SYM': new_rel = 'punct'            
        if new_rel == None and hd_upos in ('PUNCT', 'SYM'): new_rel = 'dep'
        if new_rel == None and cd_upos == 'PUNCT': return 'punct'
        
            
        ### ERROR HANDLING                
        if new_rel == None:
            new_rel = self.GuessDepRel(head_dep_info)
                               
        return new_rel
    
    def assign_sent_urel(self, SENT):
        
        SENT.insert(0, ['_' for _ in range(10)])        
        
        for idx in range(1, len(SENT)):
            
            cd = idx
            hd = int(SENT[idx][self.HEAD])
            cd_lemma = SENT[cd][self.LEMMA]
            hd_lemma = SENT[hd][self.LEMMA]
            cd_upos = SENT[cd][self.UPOS]
            hd_upos = SENT[hd][self.UPOS]
            cd_xpos = SENT[cd][self.XPOS]
            hd_xpos = SENT[hd][self.XPOS]
            krel = SENT[cd][self.KREL]  
            hd_krel = SENT[hd][self.KREL]
            
            head_dep_info = (cd, hd, cd_lemma, hd_lemma, cd_upos, hd_upos, cd_xpos, hd_xpos, krel, hd_krel)
             
            new_rel = self.assign_urel(head_dep_info)
            if new_rel == None:
                SENT[cd][self.KREL] = krel + '**'   # 모르는 거 "DEP"
            else:
                SENT[cd][self.KREL] = new_rel
         
        return SENT[1:]          
    
    