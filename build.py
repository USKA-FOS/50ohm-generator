import src.build as build
import src.config as config

conf = config.Config()

# Build Everything:
bd = build.Build(conf)
bd.build_website()
bd.build_unified_edition("HB.json", "A", "Upgrade-Kurs auf HB9", "HB3")
bd.build_unified_edition("HB.json", "NE", "Einsteigerkurs HB3", "HB9")
bd.build_unified_edition("HB.json", "NEA", "Gesamtkurs HB3 und HB9", "")
bd.build_assets()
bd.build_solutions()
#bd.build_zip()
