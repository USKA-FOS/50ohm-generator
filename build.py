import src.build as build
import src.config as config

conf = config.Config()

class_map = {'N': 'HB3', 'E': 'HB3', 'A': 'HB9' }

# Build Everything:
bd = build.Build(conf)
bd.build_website()
bd.build_unified_edition("HB.json", "A", "Upgrade-Kurs auf HB9", class_map)
bd.build_unified_edition("HB.json", "NE", "Einsteigerkurs HB3", class_map)
bd.build_unified_edition("HB.json", "NEA", "Gesamtkurs HB3 und HB9", class_map)
bd.build_assets()
bd.build_solutions()
bd.build_question_index()
bd.build_index()
#bd.build_zip()
