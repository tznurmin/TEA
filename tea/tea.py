import random
import re
import importlib.resources

class TEA:

    def __init__(self, tokenizer, rseed=None, non_stops=None, max_len=480, max_final_len=505):
        if rseed:
            self.r_seed = rseed
            random.seed(self.r_seed)

        self.tokenizer = tokenizer

        self.maxlen = max_len
        self.max_final_len = max_final_len

        self.non_stops = non_stops or ['fig.', 'al.', 'sp.', 'spp.', 'e.g.', 'pv.', 'eg.']

        self.all_species = set()
        self.species_list = []
        self.spec_re = re.compile(r"[A-Z](?:[a-z]+|\.)\s[a-z]+")

        try:
            species = importlib.resources.read_text("tea.data", "species.txt")
            for spec in species.split("\n"):
                temp = spec.strip()
                self.all_species.add(temp)
                self.all_species.add(f"{temp[0]}. {temp.split(' ')[1]}")
        except FileNotFoundError as e:
            raise FileNotFoundError("species.txt not found") from e
        
        self._regenerate_list()

    def extract_sentence(self, sp, text):
        s = sp
        e = sp

        while e < len(text) - 1 and not self.is_stop(text[e]):
            e += 1

        while s > 0 and not self.is_stop(text[s - 1]):
            s -= 1

        return (s,e)

    def num_tokens(self, text, tokenizer):
        return len(tokenizer.tokenize(text))

    def maximise(self, loc, text):

        r_count = 0
        f_count = 0
        l_count = 0

        s, e = self.extract_sentence(loc, text)

        s_done = s == 0
        e_done = e == len(text) - 1

        while not (s_done and e_done):
            l_count += 1
            if not s_done and (r_count < 2 or random.randint(0,1) == 0):
                new_s, _ = self.extract_sentence(s-1, text)
                if self.num_tokens(' '.join(text[new_s:e+1]), self.tokenizer) < self.maxlen:
                    r_count += 1
                    s = new_s
                    if s == 0:
                        s_done = True
                else:
                    s_done = True
            else:
                if e >= len(text) - 1:
                    e_done = True
                    continue
                _, new_e = self.extract_sentence(e+1, text)
                if self.num_tokens(' '.join(text[s:new_e+1]), self.tokenizer) < self.maxlen:
                    f_count += 1
                    e = new_e
                    if e == len(text) - 1:
                        e_done = True
                else:
                    e_done = True
        return s, e

    def is_stop(self, word: str):

        if not word[-1] == '.':
            return False

        if word != '].' and (len(word) < 3 or word.lower() in self.non_stops):
            return False

        return True


    def _regenerate_list(self):
        self.species_list = sorted([spec for spec in self.all_species if spec[1] != '.'])
        random.shuffle(self.species_list)

    def switch(self, text:str):
        verified = {}
        temp = self.spec_re.findall(text)
        for candidate in temp:
            if candidate in self.all_species:
                if candidate[1] == '.':
                    if not candidate in verified:
                        verified[candidate] = True
                else:
                    verified[candidate] = True
                    verified[f"{candidate[0]}. {candidate.split(' ')[1]}"] = candidate

        for s in list(verified.keys()):
            if s[1] == '.':
                continue
            new_species = self.sample()
            verified[s] = new_species
            verified[f"{s[0]}. {s.split(' ')[1]}"] = f"{new_species[0]}. {new_species.split(' ')[1]}"

        for s in list(verified.keys()):
            if s[1] != '.':
                continue
            if verified[s] != True:
                continue
            new_species = self.sample()
            verified[f"{s[0]}. {s.split(' ')[1]}"] = f"{new_species[0]}. {new_species.split(' ')[1]}"

        for k,v in verified.items():
            text = text.replace(k, v)
        return text

    def scramble(self, text, wordlist, force_diff=False, skipped_chars=None, conserved=None):

        skipped_chars = skipped_chars or set(['δ', 'Δ'])
        conserved = conserved or ['strain', 'subsp', 'subspecies', 'isolate', 'pathovar', 'serovar', 'serotype', 'genotype', 'ecotype', 'sequence', 'mutant', 'wild-type', 'complementation', 'complemented', 'pv', 'wt', 'type', 'sp']

        jt = {}

        numbers = sorted(list(set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) - skipped_chars))
        downcase_v = set(['a', 'e', 'i', 'o', 'u', 'y'])
        downcase_c = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']) - downcase_v

        upcase_v = sorted(list(set([c.upper() for c in downcase_v]) - skipped_chars))
        upcase_c = sorted(list(set([c.upper() for c in downcase_c]) - skipped_chars))

        downcase_v = sorted(list(downcase_v - skipped_chars))
        downcase_c = sorted(list(downcase_c - skipped_chars))

        g_downcase = sorted(list(set(['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω',]) - skipped_chars))
        g_upcase = sorted(list(set(['Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω']) - skipped_chars))

        for arr in [numbers, downcase_v, downcase_c, upcase_v, upcase_c, g_downcase, g_upcase]:
            arr2 = sorted(list(arr))
            random.shuffle(arr2)
            temp = arr
            if force_diff:
                temp = sorted(list(arr2))
                t = temp.pop(0)
                temp.append(t)

            for idx, c in enumerate(temp):
                jt[c] = arr2[idx]

        new_words = {}
        for words in wordlist:
            temp = ''
            for word in words.split(' '):
                if re.sub(r'[^a-z0-9]', '', word.lower()) in conserved:
                    temp += word
                else:
                    for c in word:
                        if c in jt:
                            temp += jt[c]
                        else:
                            temp += c
                temp += ' '
            temp = temp.strip()
            new_words[words] = temp

        for k,v in new_words.items():
            text = text.replace(k,v)

        return text

    def sample(self):
        if len(self.species_list) == 0:
            self._regenerate_list()
        return self.species_list.pop()

    def _extract_words(self, text, curation_data):
        word_list = set()
        for l, v in curation_data.items():
            for loc in v:
                s,e = loc.split('+')
                s = int(s)
                e = int(e)
                word_list.add(' '.join(text[s:s+e]))
        return word_list

    def augment(self, text: str, curation_data: dict, scramble=None, l2l=None) -> str:
        '''
        You can pool labels by using l2l. By default l2l preserves all labels.
        Please note that if l2l exists, everything is 'O' by default unless found from l2l.
        '''

        scramble = scramble or []
        words = set()
        
        results = {
            'original': {},
            'scrambled': {},
            'switched': {},
            'all': {}
        }

        labels = ['O'] * len(text)

        for t, locations in curation_data.items():
            t = t.split('/')[0]
            label:str = t[0:4].upper()
            if not l2l is None:
                # Conditionally pool labels
                # Please note: changes everything to 'O' unless otherwise specified if l2l exists
                label = l2l.get(label, 'O')

            if t in scramble:
                words.update(self._extract_words(text, {t: locations}))

            for loc in locations:
                t_sta,t_len = loc.split('+')
                t_sta = int(t_sta)
                t_len = int(t_len)

                if label != 'O':
                    for idx in range(t_sta, t_sta+t_len):
                        if idx == t_sta:
                            labels[idx] = f"B-{label}"
                        else:
                            labels[idx] = f"I-{label}"
                s, e = self.maximise(int(loc.split('+')[0]), text)
                results['original'][f"{s},{e}"] = ' '.join(text[s:e+1])


        results['labels'] = labels

        for pos,text in results['original'].items():
            
            transformations = {'switched': [self.switch], 'scrambled': [self.scramble], 'all': [self.switch, self.scramble]}
            extra_params = {self.scramble: [words]}

            for t, tfs in transformations.items():
                temp = text
                for idx, tf in enumerate(tfs):
                    tries = 5
                    while tries > 0:
                        params = extra_params.get(tf, [])
                        temp = tf(temp, *params)
                        if self.num_tokens(temp, self.tokenizer) <= self.max_final_len:
                            break
                        tries -= 1
                    if tries == 0:
                        break
                    if idx == len(tfs) - 1:
                        results[t][pos] = temp
        return results
