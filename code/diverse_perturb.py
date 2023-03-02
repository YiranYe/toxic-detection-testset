import random
from collections import defaultdict
import json
import demoji
from nltk.corpus import words
import warnings
import copy


class PerturbationCluster:
    
    def __init__(self, pert_dict, discard_func = None, **kwargs):
        self.place_holder_list = ['_','-','*','~','/']
        self.pert_dict = pert_dict
        self.word_set = set(words.words())
        self.func_dict = {
            'lowercase_uppercase': self.lowercase_uppercase,
            'interesting_lowercase_uppercase': self.interesting_lowercase_uppercase,
            'emoticons': self.emoticons,
            'repeat_char': self.repeat_char,
            'abbr': self.abbr,
            'placeholder': self.placeholder,
            'special_character': self.special_character
        }

        if discard_func:
            for func_name in discard_func:
                del self.func_dict[func_name]

        for k,v in kwargs:
            assert v.__code__.co_varnames == ('clean_word','pert_word')
            if k in self.func_dict:
                warnings.warn(f'default function {k} has been overwritten')
            self.func_dict[k] = v


    def get_attribute_list(self):
        return list(self.func_dict.keys())


    def classify(self, include_other=False):
        res = defaultdict(lambda: defaultdict(list))
        for clean, pert_list in self.pert_dict.items():
            for pert in pert_list:
                is_other = include_other
                for func_name, func in self.func_dict.items():
                    if func(clean, pert):
                        res[clean][func_name].append(pert)
                        is_other = False

                if is_other:
                    res[clean]['other'].append(pert)
        return res


    def simplify_word(self, word):
        pw = list(word.lower())
        i = 1
        while i < len(pw):
            if pw[i] == pw[i-1]:
                pw.pop(i)
            else:
                i += 1
        return ''.join(pw)


    def lowercase_uppercase(self, clean_word, pert_word):
        return pert_word[1:].lower() != pert_word[1:] and pert_word.upper() != pert_word


    def interesting_lowercase_uppercase(self, clean_word, pert_word):
        collect = ''
        for c in pert_word:
            if c.lower() != c:
                collect += c
        return pert_word.lower() != pert_word and collect.lower() in self.word_set and len(collect) != len(pert_word) and len(collect) > 1


    def emoticons(self, clean_word, pert_word):
        return len(demoji.findall(pert_word)) >= 1


    def repeat_char(self, clean_word, pert_word):
        c,p = clean_word.lower(),pert_word.lower()
        simp_c, simp_p = self.simplify_word(c), self.simplify_word(p)
        return len(p) > len(c) and simp_c == simp_p and simp_p != p


    def abbr(self, clean_word, pert_word):
        c,p = clean_word.lower(),pert_word.lower()
        i = 0
        for character in c:
            if character == p[i]:
                i += 1
                if i == len(p):
                    return len(p) < len(c)
        return False


    def placeholder(self, clean_word, pert_word):
        if len(pert_word) < 4:
            return False
        for c in list(pert_word):
            if c in self.place_holder_list:
                return True
        return False


    def special_character(self, clean_word, pert_word):
        for c in list(pert_word.lower()):
            if (c < 'a' or c > 'z') and c not in self.place_holder_list:
                return True
        return False


class PerturbationGenerator:
    
    def __init__(self, candidate_dict, attributes, initial_cnt=None):
        self.MAX_NUM_OF_ATTEMPTS = 100
        self.MAX_NUM_OF_REPEATED_PERT = 3
        self.initial_cnt = initial_cnt if initial_cnt else [1 for _ in range(len(attributes))]
        self.attribute_cnt = {attr:cnt for attr,cnt in zip(attributes,self.initial_cnt)}
        self.candidate_dict = copy.deepcopy(candidate_dict)
        self.pert_cnt = defaultdict(int)

    def get_cnt(self):
        return '\n'.join([f"{item[0]}: {item[1]-init_cnt}" for init_cnt,item in zip(self.initial_cnt, self.attribute_cnt.items())])


    def find_attribute(self, candidate_attribute):
        weight = [(attr,1/self.attribute_cnt[attr]) for attr in candidate_attribute]
        return random.choices(list([attr for attr,_cnt in weight]), weights=tuple([cnt for _attr,cnt in weight]), k=1)[0]


    def pert_one(self,word):
        candidate_attributes = list(self.attribute_cnt.keys())
        while len(candidate_attributes) > 0:
            attribute = self.find_attribute(candidate_attributes)
            perturb_list = self.candidate_dict.get(word, {}).get(attribute, None)
            while perturb_list:
                perturb = perturb_list[0]
                if perturb and isinstance(perturb, str) and self.pert_cnt[perturb] < self.MAX_NUM_OF_REPEATED_PERT:
                    self.pert_cnt[perturb] += 1
                    self.attribute_cnt[attribute] += 1
                    perturb_list = perturb_list[1:] + [perturb]
                    return perturb
                else:
                    perturb_list = perturb_list[1:]

            candidate_attributes.remove(attribute)
        return None


    def shuffle(self,seed=1):
        for k,v in self.candidate_dict.items():
            for pert_list in v.values():
                random.Random(seed).shuffle(pert_list)





        
# with open('/Users/yeyiran/PycharmProjects/Norm_Pert/hard_pert_test.json') as hard_pert_f:
#     old_hard_pert = json.load(hard_pert_f)

# with open('/Users/yeyiran/PycharmProjects/Norm_Pert/easy_pert_test.json') as hard_pert_f:
#     easy_pert = json.load(hard_pert_f)


# hard_pert = defaultdict(list)
# for k,v in old_hard_pert.items():
#     for value in v:
#         if value.lower() != k:
#             hard_pert[k].append(value)


# pert_total = defaultdict(list)
# for k,v in old_hard_pert.items():
#     for val in v:
#         pert_total[k].append(val)
# for k,v in easy_pert.items():
#     for val in v:
#         pert_total[k].append(val)


        
# cluster = PerturbationCluster(pert_dict=pert_total)
# res = cluster.classify()