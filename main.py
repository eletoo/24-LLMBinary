import sys
import warnings
import argparse
from tqdm import tqdm
import nltk
from transformers import RobertaTokenizer, T5ForConditionalGeneration
import json
from rouge import Rouge
import os


def gen_summary(function, tokenizer, model):
    tokens = tokenizer(function, return_tensors="pt")
    input_ids = tokens.input_ids
    if len(input_ids[0]) <= 512:
        generated_ids = model.generate(input_ids, max_length=512)
        comment = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        return comment.strip()
    return None


def eval_single(expected, value):
    with warnings.catch_warnings():
        return (
            nltk.translate.meteor_score.meteor_score([expected.split(" ")], value.split(" ")),
            nltk.translate.bleu_score.sentence_bleu(references=[expected.split(" ")], hypothesis=value.split(" "),
                                                    weights=[1. / 2., 1. / 2.]),
            Rouge().get_scores(value, expected)[0]['rouge-l']['f']
        )


def evaluate(name, expected, summary, non_strip_summary, fun_name_summary):
    strip = eval_single(expected, summary)
    non_strip = eval_single(expected, non_strip_summary)
    fun_name = eval_single(expected, fun_name_summary)
    tqdm.write(
        "{} \n    STRIP:      meteor={:.4f}, bleu={:.4f}, rouge-l={:.4f}".format(name, *strip))
    tqdm.write(
        "    NON_STRIP:  meteor={:.4f}, bleu={:.4f}, rouge-l={:.4f}".format(*non_strip))
    tqdm.write(
        "    FUN_NAME:   meteor={:.4f}, bleu={:.4f}, rouge-l={:.4f}".format(*fun_name))
    sys.stdout.flush()
    return (strip, non_strip, fun_name)


parser = argparse.ArgumentParser(prog='SicInf')
parser.add_argument('modelname')
parser.add_argument('-d', '--dataset', type=str)
parser.add_argument('-o', '--output', type=str)
parser.add_argument('-r', '--results', type=str)

if __name__ == '__main__':
    args = parser.parse_args()

    if os.path.exists("codet5-base/pytorch_model.bin"):
        os.remove("codet5-base/pytorch_model.bin")

    model_path = os.path.abspath(f"BinT5/{args.modelname}/pytorch_model.bin")
    if os.path.exists(model_path):
        os.symlink(model_path, os.path.abspath("codet5-base/pytorch_model.bin"))
    else:
        print("Model does not exist")
        exit(1)

    tokenizer = RobertaTokenizer.from_pretrained('codet5-base')
    model = T5ForConditionalGeneration.from_pretrained('codet5-base')

    data = json.load(open(args.dataset))
    results = open(args.results, "w")
    out = open(args.output, "w")
    outdata = {}
    outvalues = {}
    for i in tqdm(data):

        function_name = i["function_name"]
        function_name_in_strip = i["function_name_in_strip"]

        comment = i["comment"]
        pseudo_code = i["pseudo_code"]
        pseudo_code_non_strip = i["pseudo_code_non_strip"]

        summary = gen_summary(pseudo_code, tokenizer, model)
        non_strip_summary = gen_summary(pseudo_code_non_strip, tokenizer, model)
        fun_name_summary = gen_summary(pseudo_code.replace(function_name_in_strip, function_name), tokenizer, model)

        if summary is not None and non_strip_summary is not None and fun_name_summary is not None:
            ret = evaluate(function_name, comment, summary, non_strip_summary, fun_name_summary)

            outdata.update({
                function_name: {
                    "comment": comment,
                    "summary_strip": summary,
                    "summary_non_strip": non_strip_summary,
                    "summary_fun_name": fun_name_summary
                }
            })

            outvalues.update({
                function_name: {
                    "summary_strip": {
                        "meteor": ret[0][0],
                        "bleu": ret[0][1],
                        "rouge-l": ret[0][2],
                    },
                    "summary_non_strip": {
                        "meteor": ret[1][0],
                        "bleu": ret[1][1],
                        "rouge-l": ret[1][2],
                    },
                    "summary_fun_name": {
                        "meteor": ret[2][0],
                        "bleu": ret[2][1],
                        "rouge-l": ret[2][2],
                    }
                }
            })
    json.dump(outdata, results)
    json.dump(outvalues, out)
