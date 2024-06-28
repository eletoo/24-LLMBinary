import os.path
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import argparse

parser = argparse.ArgumentParser(prog='SicInf-Elab')
parser.add_argument('infile')
parser.add_argument('outdir')

df = pd.DataFrame({
    "function": [],
    "strip_meteor": [],
    "strip_bleu": [],
    "strip_rouge": [],
    "non_strip_meteor": [],
    "non_strip_bleu": [],
    "non_strip_rouge": [],
    "name_meteor": [],
    "name_bleu": [],
    "name_rouge": [],
})


def load_dataset(infile):
    data = json.load(open(infile))
    for k, v in data.items():
        df.loc[len(df.index)] = [
            k,
            v["summary_strip"]["meteor"], v["summary_strip"]["bleu"], v["summary_strip"]["rouge-l"],
            v["summary_non_strip"]["meteor"], v["summary_non_strip"]["bleu"], v["summary_non_strip"]["rouge-l"],
            v["summary_fun_name"]["meteor"], v["summary_fun_name"]["bleu"], v["summary_fun_name"]["rouge-l"]
        ]


def comparison_plot(out_dir, sort, metric, metric_title):
    global df
    df = df.sort_values(by=[sort], ascending=False)
    _, ax = plt.subplots(2, 1, sharex=True, sharey=True)
    ax[0].plot(list(range(len(df))), df[f"name_{metric}"], 'xb', label="fun-name")
    ax[0].plot(list(range(len(df))), df[f"non_strip_{metric}"], 'r', label="non-stripped")
    ax[1].plot(list(range(len(df))), df[f"strip_{metric}"], 'xb', label="stripped")
    ax[1].plot(list(range(len(df))), df[f"non_strip_{metric}"], 'r', label="non-stripped")
    plt.suptitle(f"Confronto Metrica {metric_title}")
    plt.xlabel("Commento")
    ax[0].set_ylabel("Valore Metrica")
    ax[1].set_ylabel("Valore Metrica")
    ax[0].legend()
    ax[1].legend()
    ax[0].grid()
    ax[1].grid()
    plt.savefig(f"{out_dir}/{metric}-plot.pdf")
    plt.close()


def violin_plot(out_dir):
    global df
    vdf = df.filter(items=[
        "diff_meteor_non_strip_strip",
        "diff_meteor_name_strip",
        "diff_bleu_non_strip_strip",
        "diff_bleu_name_strip",
        "diff_rouge_non_strip_strip",
        "diff_rouge_name_strip"
    ])
    vdf = vdf.melt()
    vdf['label'] = ""
    vdf['label'][vdf['variable'] == 'diff_meteor_non_strip_strip'] = 'METEOR'
    vdf['label'][vdf['variable'] == 'diff_meteor_name_strip'] = 'METEOR'
    vdf['label'][vdf['variable'] == 'diff_bleu_non_strip_strip'] = 'BLEU'
    vdf['label'][vdf['variable'] == 'diff_bleu_name_strip'] = 'BLEU'
    vdf['label'][vdf['variable'] == 'diff_rouge_non_strip_strip'] = 'ROUGE-L'
    vdf['label'][vdf['variable'] == 'diff_rouge_name_strip'] = 'ROUGE-L'

    vdf['variable'][vdf['variable'] == 'diff_meteor_non_strip_strip'] = "NonStrip-Strip"
    vdf['variable'][vdf['variable'] == 'diff_meteor_name_strip'] = "FunName-Strip"
    vdf['variable'][vdf['variable'] == 'diff_bleu_non_strip_strip'] = "NonStrip-Strip"
    vdf['variable'][vdf['variable'] == 'diff_bleu_name_strip'] = "FunName-Strip"
    vdf['variable'][vdf['variable'] == 'diff_rouge_non_strip_strip'] = "NonStrip-Strip"
    vdf['variable'][vdf['variable'] == 'diff_rouge_name_strip'] = "FunName-Strip"

    print(vdf.head())
    sns.violinplot(
        data=vdf,
        split=True,
        hue='variable',
        y='value',
        x='label',
        inner=None,
        density_norm='count'
    )
    plt.title("Distribuzioni delle Differenze tra Coppie di Metriche")
    plt.grid()
    plt.savefig(f"{out_dir}/violin_distr.pdf")
    plt.close()


if __name__ == '__main__':
    args = parser.parse_args()
    load_dataset(args.infile)

    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    print(df[df.columns.difference(["function"])].mean(axis=0))
    df["diff_rouge_non_strip_strip"] = -(df["strip_rouge"] - df["non_strip_rouge"])
    df["diff_rouge_name_strip"] = -(df["strip_rouge"] - df["name_rouge"])
    df["diff_bleu_non_strip_strip"] = -(df["strip_bleu"] - df["non_strip_bleu"])
    df["diff_bleu_name_strip"] = -(df["strip_bleu"] - df["name_bleu"])
    df["diff_meteor_non_strip_strip"] = -(df["strip_meteor"] - df["non_strip_meteor"])
    df["diff_meteor_name_strip"] = -(df["strip_meteor"] - df["name_meteor"])

    comparison_plot(args.outdir, "non_strip_rouge", "rouge", "ROUGE-L")
    comparison_plot(args.outdir, "name_bleu", "bleu", "BLEU")
    comparison_plot(args.outdir, "non_strip_meteor", "meteor", "METEOR")
    violin_plot(args.outdir)


