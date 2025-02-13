import re
import json
import random
import os
from transformers import AutoTokenizer
from tea import TEA


def load_article(cs):
    #Load and normalise article texts
    with open(f"TEA_curated_data/source_articles/{cs}/{cs}.txt") as fp:
        data = fp.read()

    data = re.sub(r'\$/i\$', '', data)
    data = re.sub(r'\$i\$', '', data)
    data = re.sub(r'\s+', ' ', data)
    return data.split()


if __name__ == '__main__':
    '''
    Example script for generating training and test datasets for 'strategy' experiment by using TEA for curated data and source articles.
    Assumes that the TEA_curated_data is found from the same directory.
    Clone TEA_curated_data from here: https://github.com/tznurmin/TEA_curated_data
    '''

    
    # Suppress tokenizer warnings by using model_max_length that is longer than the target length
    tokenizer = AutoTokenizer.from_pretrained('dmis-lab/biobert-base-cased-v1.2', do_lower_case=False, model_max_length=100000)

    # Define test set sizes here
    test_set_size = {
        'pathogens': 120,
        'strains': 85
    }

    # Define pooled labels
    # Important to note: labels that are not found from here are defaulted to 'O'
    pooled_labels = {
        'pathogens': {'PATH': 'PATH', 'OPPO': 'PATH', 'STRA': 'PATH'},
        'strains': {'STRA': 'STRA', 'SPEC': 'SPEC'}
    }

    curation_data = {}
    for t in ['pathogens', 'strains']:
        for s in ['training', 'test']:
            os.makedirs(os.path.dirname(f"results/{t}/{s}/"), exist_ok=True)

        tea = TEA(tokenizer)
        tag_types = set()
        curation_data[t] = {
            'checksums': [],
            'data': {}
        }
        with open(f"TEA_curated_data/curation_data/{t}/{t}.json") as fp:
            temp = json.load(fp)
            for c,d in temp.items():
                curation_data[t]['checksums'].append(c)
                curation_data[t]['data'][c] = d
                for k,v in d.items():
                    tag_types.add(k.split('/')[0])

        curation_data[t]['tags'] = tag_types
        
        csums = curation_data[t]['checksums']
        random.shuffle(csums)
        test_csums = []

        while len(test_csums) < test_set_size[t]:
            test_csums.append(csums.pop())    

        training_set = {
            'original': [],
            'switched': [],
            'scrambled': [],
            'all': []
        }
        test_set = {
            'original': [],
            'all': []
        }

        for csum in csums:
            print(f"Processing {csum}")
            text = load_article(csum)
            results = tea.augment(text, curation_data[t]['data'][csum], scramble=['strains'], l2l=pooled_labels[t])
            labels = results.pop('labels')

            for aug_t, texts in results.items():
                for pos, txt in texts.items():
                    temp = txt.split()
                    s,e = int(pos.split(',')[0]), int(pos.split(',')[1])
                    example = []
                    for w,l in zip(temp,labels[s:e+1]):
                        example.append(f"{w} {l}")
                    training_set[aug_t].append("\n".join(example) + "\n")

        for aug_t, examples in training_set.items():
            # convert to match the naming scheme of 'strategy' experiment
            jt = {
                'original': 'none',
                'switched': 'species',
                'scrambled': 'strains'
            }
            temp = jt.get(aug_t, aug_t)
            with open(f"results/{t}/training/{temp}_{t}_training_1.set", 'w') as fp:
                    fp.write("\n".join(examples))
        
        for csum in test_csums:
            text = load_article(csum)
            results = tea.augment(text, curation_data[t]['data'][csum], scramble=['strains'], l2l=pooled_labels[t])
            labels = results.pop('labels')

            for aug_t, texts in results.items():
                for pos, txt in texts.items():
                    temp = txt.split()
                    s,e = int(pos.split(',')[0]), int(pos.split(',')[1])
                    example = []
                    for w,l in zip(temp,labels[s:e+1]):
                        example.append(f"{w} {l}")
                    if aug_t in test_set:
                        test_set[aug_t].append("\n".join(example) + "\n")


        for aug_t, examples in test_set.items():
            temp = aug_t
            if aug_t == 'original':
                temp = 'unaugmented'
            
            with open(f"results/{t}/test/{temp}_1v_test_1.set", 'w') as fp:
                fp.write("\n".join(examples))

        print(f"{t} done")
