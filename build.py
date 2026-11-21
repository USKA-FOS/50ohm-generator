import argparse

import src.build as build
import src.config as config

parser = argparse.ArgumentParser()
parser.add_argument(
    "--seed",
    type=int,
    default=None,
    help="Deterministic seed for question-answer shuffling. Omit for non-deterministic builds.",
)
args = parser.parse_args()

conf = config.Config(random_seed=args.seed)
lang = conf.language

course_titles = {
    "de": {
        "A": "Upgrade-Kurs auf HB9",
        "NE": "Einsteigerkurs HB3",
        "NEA": "Gesamtkurs HB3 und HB9",
    },
    "fr": {
        "A": "Cours de mise à niveau vers HB9",
        "NE": "Cours débutant HB3",
        "NEA": "Cours complet HB3 et HB9",
    },
    "it": {
        "A": "Corso di aggiornamento a HB9",
        "NE": "Corso principianti HB3",
        "NEA": "Corso completo HB3 e HB9",
    },
}

class_map = {'N': 'HB3', 'E': 'HB3', 'A': 'HB9' }

# Build Everything:
bd = build.Build(conf)
bd.build_website()
bd.build_unified_edition("HB.json", "A", course_titles[lang]["A"], class_map)
bd.build_unified_edition("HB.json", "NE", course_titles[lang]["NE"], class_map)
bd.build_unified_edition("HB.json", "NEA", course_titles[lang]["NEA"], class_map)
bd.build_assets()
bd.build_solutions()
bd.build_question_index()
bd.build_index()
#bd.build_zip()
