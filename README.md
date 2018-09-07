
# S2D : SejongTree To Dependency
세종 구문 분석 말뭉치의 의존 구문 구조로의 변환 도구(ver. 0.9)
- **Universal Dependency Relation이 매번 업데이트 될 예정입니다.(180820)**
- 2018.09.08 기준으로 아래의 사이트에서 업데이트할 예정입니다.
  - https://github.com/cnunlplab/SejongTree2Dependency

# Update
- 180820 ver. 0.9 업로드

# Document : SejongTree2Dep.pdf

# Requirement
- python 3.6

# Execution
> (rigid head): python SejongToDependency.py -root_dir corpus_folder_path -save_file result  -head_initial ./Rules/linear_rules.txt -head_final 1
> (non-rigid head): python SejongToDependency.py -root_dir corpus_folder_path -save_file result  -head_initial_file ./Rules/linear_rules.txt -head_final 0


    Paramters
    -root_dir: 세종 코퍼스 폴더 위치
    -file_name(optional): 세종 코퍼스 파일 이름(하나의 세종 코퍼스 파일만 읽고자 할 때)
    -save_file: 의존 구문 구조 저장할 파일 이름
    -head_initial_file: head-initial 예외 규칙(구분자 : \t)
    -head_final: 1 if head-final  0 else (default: 0)



# Format : CONLL-U
*예제:* 
엠마누엘 웅가로는 "실내 장식품을 디자인할 때 옷을 만들 때와는 다른 해방감을 느낀다"고 말한다.

**Rigid Head-final Version**

|  ID  |   FORM   |    LEMMA     | UPOSTAG |    XPOSTAG    | FEATS | HEAD | DEPREL | DEPS |     MISC      |
| :--: | :------: | :----------: | :-----: | :-----------: | :---: | :--: | :----: | :--: | :-----------: |
|  1   | 엠마누엘 |   엠마누엘   |  PROPN  |      NNP      |   _   |  2   |  nmod  |  _   |       _       |
|  2   | 웅가로는 |  웅가로 는   |  PROPN  |    NNP+JX     |   _   |  16  | nsubj  |  _   |       _       |
|  3   |    "     |      "       |  PUNCT  |      SS       |   _   |  14  | punct  |  _   | SpaceAfter=No |
|  4   |   실내   |     실내     |  NOUN   |      NNG      |   _   |  5   |  nmod  |  _   |       _       |
|  5   | 장식품을 |  장식품 을   |  NOUN   |    NNG+JKO    |   _   |  6   |  obj   |  _   |       _       |
|  6   | 디자인할 | 디자인 하 ㄹ |  VERB   |    VV+ETM     |   _   |  7   |  acl   |  _   |       _       |
|  7   |    때    |      때      |  NOUN   |      NNG      |   _   |  13  |  obl   |  _   |       _       |
|  8   |   옷을   |    옷 을     |  NOUN   |    NNG+JKO    |   _   |  9   |  obj   |  _   |       _       |
|  9   |   만들   |   만들 ㄹ    |  VERB   |    VV+ETM     |   _   |  10  |  acl   |  _   |       _       |
|  10  |  때와는  |   때 와 는   |  NOUN   |  NNG+JKB+JX   |   _   |  11  | nsubj  |  _   |       _       |
|  11  |   다른   |   다르 ㄴ    |   ADJ   |    VA+ETM     |   _   |  12  |  acl   |  _   |       _       |
|  12  | 해방감을 |  해방감 을   |  NOUN   |    NNG+JKO    |   _   |  13  |  obj   |  _   |       _       |
|  13  |  느낀다  |  느낀 ㄴ다   |  VERB   |     VV+EC     |   _   |  14  | advcl  |  _   | SpaceAfter=No |
|  14  |    "     |      "       |  PUNCT  |      SS       |   _   |  15  | punct  |  _   | SpaceAfter=No |
|  15  |    고    |      고      |   ADP   |      JKQ      |   _   |  16  | ccomp  |  _   |       _       |
|  16  | 말한다.  | 말 하 ㄴ다 . |  VERB   | NNG+XSV+EF+SF |   _   |  0   |  root  |  _   |       _       |

**Non-rigid Head final Version**

|  ID  |   FORM   |    LEMMA     | UPOSTAG |    XPOSTAG    | FEATS | HEAD | DEPREL | DEPS |     MISC      |
| :--: | :------: | :----------: | :-----: | :-----------: | :---: | :--: | :----: | :--: | :-----------: |
|  1   | 엠마누엘 |   엠마누엘   |  PROPN  |      NNP      |   _   |  2   |  nmod  |  _   |       _       |
|  2   | 웅가로는 |  웅가로 는   |  PROPN  |    NNP+JX     |   _   |  16  | nsubj  |  _   |       _       |
|  3   |    "     |      "       |  PUNCT  |      SS       |   _   |  13  | punct  |  _   | SpaceAfter=No |
|  4   |   실내   |     실내     |  NOUN   |      NNG      |   _   |  5   |  nmod  |  _   |       _       |
|  5   | 장식품을 |  장식품 을   |  NOUN   |    NNG+JKO    |   _   |  6   |  obj   |  _   |       _       |
|  6   | 디자인할 | 디자인 하 ㄹ |  VERB   |    VV+ETM     |   _   |  7   |  acl   |  _   |       _       |
|  7   |    때    |      때      |  NOUN   |      NNG      |   _   |  13  |  obl   |  _   |       _       |
|  8   |   옷을   |    옷 을     |  NOUN   |    NNG+JKO    |   _   |  9   |  obj   |  _   |       _       |
|  9   |   만들   |   만들 ㄹ    |  VERB   |    VV+ETM     |   _   |  10  |  acl   |  _   |       _       |
|  10  |  때와는  |   때 와 는   |  NOUN   |  NNG+JKB+JX   |   _   |  11  | nsubj  |  _   |       _       |
|  11  |   다른   |   다르 ㄴ    |   ADJ   |    VA+ETM     |   _   |  12  |  acl   |  _   |       _       |
|  12  | 해방감을 |  해방감 을   |  NOUN   |    NNG+JKO    |   _   |  13  |  obj   |  _   |       _       |
|  13  |  느낀다  |  느낀 ㄴ다   |  VERB   |     VV+EC     |   _   |  16  | ccomp  |  _   | SpaceAfter=No |
|  14  |    "     |      "       |  PUNCT  |      SS       |   _   |  13  | punct  |  _   | SpaceAfter=No |
|  15  |    고    |      고      |   ADP   |      JKQ      |   _   |  13  |  case  |  _   |       _       |
|  16  | 말한다.  | 말 하 ㄴ다 . |  VERB   | NNG+XSV+EF+SF |   _   |  0   |  root  |  _   |       _       |



# CoNLL2Transition : CONLL To Transition

Transition-based 의존 구문 파서를 위한 데이터 변환



# Requirement

- python 3.6


# Execution

> (ARC Standard + forward): python MakeTransitionCorpus.py -root_dir ./ -file_name *sejong.conll* -save_file *sejong_ARC_STANDARD.txt* -arc_standard  
> (ARC Eager + backward): python MakeTransitionCorpus.py -root_dir ./ -file_name *sejong.conll* -save_file *sejong_ARC_EAGER.txt*

```
Paramters
root_dir: 세종 코퍼스 폴더 위치
file_name(optional): 세종 코퍼스 파일 이름(하나의 세종 코퍼스 파일만 읽고자 할때)
save_file: 변환한 구문 구조를 저장할 파일 이름
arc_standard: ARC-Standard를 이용한 데이터 변환
```
