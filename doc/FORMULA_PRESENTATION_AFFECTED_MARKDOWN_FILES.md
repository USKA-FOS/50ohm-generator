# Fichiers Markdown concernés par les corrections de présentation des formules

Document établi le 20 novembre 2026 à partir de l’inventaire du site allemand du **30 octobre 2026**. Il ne constitue pas un nouvel audit du contenu actuel.

## Périmètre et interprétation

La branche `fix/formula-presentation` du générateur regroupe les corrections de présentation : distinction entre expressions intégrées au texte et équations isolées, polices adaptées au contexte, tailles relatives, alignement et gestion de la largeur disponible.

- **34 fichiers** contiennent des paragraphes dont les formules doivent être reconnues comme des blocs isolés par le générateur.
- **254 fichiers** contiennent des formules dans le contenu pédagogique et constituent le périmètre plus large auquel s’applique la politique de rendu. Les 34 premiers sont inclus dans ces 254 fichiers.
- La présence dans la liste générale ne signifie pas que chaque formule du fichier était incorrecte.
- Il s’agit de corrections du générateur et de ses styles ; cette liste ne prescrit pas de réécriture des sources Markdown.
- Les pages répétées dans plusieurs éditions ont été regroupées par fichier source. Les questions intégrées aux pages sont exclues de cet inventaire des fichiers pédagogiques ; les diapositives conservent leur traitement distinct.

Les chemins ci-dessous sont relatifs à la racine du dépôt de contenus `50ohm-contents-ch`. Les noms allemands des fichiers sont conservés.

## 1. Reconnaissance des formules isolées — 34 fichiers

Ces fichiers présentent au moins un paragraphe identifié par le détecteur comme pouvant passer du traitement inline à un bloc de formule. Les cas comprennent notamment une formule suivie de ponctuation ou plusieurs formules reliées par un connecteur autorisé. La formule elle-même est conservée.

```text
contents/sections/aequivalente_isotrope_strahlungsleistung_eirp_2.md
contents/sections/amateurfunkbaender.md
contents/sections/baken.md
contents/sections/bandbreite.md
contents/sections/binaer.md
contents/sections/datenuebertragungsrate.md
contents/sections/dezibel_1.md
contents/sections/dezibel_2.md
contents/sections/emitterschaltung.md
contents/sections/frequenz.md
contents/sections/frequenzspektrum.md
contents/sections/kabeldaempfung_1.md
contents/sections/kondensator_1.md
contents/sections/leiterwiderstand.md
contents/sections/leitung_phasenverschiebung.md
contents/sections/mischer_2.md
contents/sections/nicht_sinus_signale.md
contents/sections/oszilloskop_1.md
contents/sections/photovoltaik.md
contents/sections/qam.md
contents/sections/reihe_parallel_widerstand.md
contents/sections/relaisfunkstellen.md
contents/sections/sender_messungen.md
contents/sections/spannung.md
contents/sections/spitze_effektiv_wert.md
contents/sections/strom.md
contents/sections/strom_spannung_messung_3.md
contents/sections/swr_2.md
contents/sections/transverter_2.md
contents/sections/unerwuenschte_aussendungen_3.md
contents/sections/verstaerker_klasse.md
contents/sections/wellenwiderstand.md
contents/sections/widerstandsfarbcode.md
contents/sections/zehnerpotenzen.md
```

## 2. Périmètre général de présentation des formules — 254 fichiers

Cette liste complète inclut la précédente. Elle identifie les fichiers dont les pages allemandes contiennent des formules dans le contenu pédagogique, qu’elles soient intégrées au texte ou isolées.

```text
contents/sections/9600_port.md
contents/sections/abtasttheorem.md
contents/sections/aequivalente_isotrope_strahlungsleistung_eirp_1.md
contents/sections/aequivalente_isotrope_strahlungsleistung_eirp_2.md
contents/sections/afsk.md
contents/sections/akku.md
contents/sections/am.md
contents/sections/am_2.md
contents/sections/amateurfunkbaender.md
contents/sections/amplitude_periode.md
contents/sections/analog_vs_digital.md
contents/sections/antenne_laenge_resonanz.md
contents/sections/antennen_beruehrung_2.md
contents/sections/antennenformen_2.md
contents/sections/antennenformen_3.md
contents/sections/antennengewinn.md
contents/sections/anti_alias_rekonstruktionsfilter.md
contents/sections/anzeige_ortsfester_amateurfunkanlagen.md
contents/sections/ask_fsk_afsk.md
contents/sections/aufbau_empfaenger.md
contents/sections/aufbau_sender.md
contents/sections/aurora_1.md
contents/sections/aurora_2.md
contents/sections/automatische_empfangsberichte.md
contents/sections/baken.md
contents/sections/bandbreite.md
contents/sections/bandbreite_2.md
contents/sections/bandreite_3.md
contents/sections/batterien_und_akkus.md
contents/sections/bfo_2.md
contents/sections/binaer.md
contents/sections/bodenwelle.md
contents/sections/brueckengleichrichter.md
contents/sections/brueckenschaltung.md
contents/sections/computersteuerung.md
contents/sections/dac_adc.md
contents/sections/daempfungsglieder.md
contents/sections/datenuebertragungsrate.md
contents/sections/demodulator.md
contents/sections/dezibel_1.md
contents/sections/dezibel_2.md
contents/sections/digimode_ssb.md
contents/sections/digital_iq.md
contents/sections/digitale_filter.md
contents/sections/digitale_signalverarbeitung_einleitung.md
contents/sections/diode_1.md
contents/sections/diode_2.md
contents/sections/dipol.md
contents/sections/dummy_load_2.md
contents/sections/e_feld.md
contents/sections/effektive_strahlungsleistung_erp_1.md
contents/sections/effektive_strahlungsleistung_erp_2.md
contents/sections/einbau_kfz.md
contents/sections/elektrische_geaete_oeffnen_1.md
contents/sections/elektrische_verlaengerung_verkuerzung.md
contents/sections/em_feld.md
contents/sections/emitterschaltung.md
contents/sections/endgespeiste_antennen.md
contents/sections/fading.md
contents/sections/fehlererkennung.md
contents/sections/fehlerkorrektur.md
contents/sections/fernspeiseweiche.md
contents/sections/fm.md
contents/sections/fm_2.md
contents/sections/fm_3.md
contents/sections/formeln_umstellen.md
contents/sections/fourier_transformation.md
contents/sections/frequenz.md
contents/sections/frequenzgenauigkeit.md
contents/sections/frequenzmessung_1.md
contents/sections/frequenzmessung_2.md
contents/sections/frequenzspektrum.md
contents/sections/frequenzvervielfacher_1.md
contents/sections/funken_im_ausland.md
contents/sections/funkhorizont.md
contents/sections/funkwellen.md
contents/sections/fusspunktimpedanz_1.md
contents/sections/fusspunktimpedanz_2.md
contents/sections/gefahren.md
contents/sections/gleich_und_wechselspannung.md
contents/sections/gleichrichter_2.md
contents/sections/greyline.md
contents/sections/h_feld.md
contents/sections/halbwertsbreite.md
contents/sections/iaru_bandplan.md
contents/sections/iaru_bandplan_2m.md
contents/sections/impedanztransformation.md
contents/sections/innenwiderstand.md
contents/sections/integrierte_schaltkreise.md
contents/sections/intermodulation_kreuzmodulation.md
contents/sections/ionosphaere_2.md
contents/sections/ionosphaere_3.md
contents/sections/iq_verfahren.md
contents/sections/kabeldaempfung_1.md
contents/sections/kollektorschaltung.md
contents/sections/kondensator_1.md
contents/sections/kondensator_2.md
contents/sections/ladung_energie.md
contents/sections/langer_kurzer_weg_2.md
contents/sections/lecherleitung.md
contents/sections/leistung.md
contents/sections/leistung_2.md
contents/sections/leistungsvertaerker.md
contents/sections/leiterwiderstand.md
contents/sections/leitung_phasenverschiebung.md
contents/sections/linkstrecken.md
contents/sections/low_noise_block.md
contents/sections/mantelwellen_1.md
contents/sections/mantelwellen_2.md
contents/sections/mapping.md
contents/sections/mischer.md
contents/sections/mischer_2.md
contents/sections/modulatoren.md
contents/sections/moegel_dellinger_effekt.md
contents/sections/morsetelegrafie.md
contents/sections/muf_luf_1.md
contents/sections/muf_luf_2.md
contents/sections/naeherungsformel_1.md
contents/sections/naeherungsformel_2.md
contents/sections/nahfeld.md
contents/sections/netzgeraet_1.md
contents/sections/nicht_sinus_signale.md
contents/sections/notfunk.md
contents/sections/ohmsches_gesetz.md
contents/sections/oszillator_dds.md
contents/sections/oszillator_gpsdo.md
contents/sections/oszillator_pll.md
contents/sections/oszillator_tcxo_ocxo.md
contents/sections/oszillator_vco.md
contents/sections/oszillatoren.md
contents/sections/oszilloskop_1.md
contents/sections/oszilloskop_2.md
contents/sections/parabolspiegel_1.md
contents/sections/parbolspiegel_2.md
contents/sections/personenschutzabstand_2.md
contents/sections/personenschutzabstand_3.md
contents/sections/personenschutzabstand_grenzwerte.md
contents/sections/personenschutzabstand_richtantennen.md
contents/sections/phase.md
contents/sections/photovoltaik.md
contents/sections/physikalische_stromrichtung.md
contents/sections/pm.md
contents/sections/polarmodulation.md
contents/sections/primaerer_sekundaerer_funkdienst.md
contents/sections/psk.md
contents/sections/q_schluessel.md
contents/sections/qam.md
contents/sections/rauch_und_morsezeichen.md
contents/sections/rauschen.md
contents/sections/reihe_parallel_gemischt.md
contents/sections/reihe_parallel_kondensator.md
contents/sections/reihe_parallel_widerstand.md
contents/sections/reihe_parallel_widerstandsnetz_1.md
contents/sections/reihe_parallel_widerstandsnetz_2.md
contents/sections/reihenschaltung_spule.md
contents/sections/relaisfunkstellen.md
contents/sections/restwelligkeit.md
contents/sections/rundstrahler.md
contents/sections/s_meter.md
contents/sections/sampling_quantisierung.md
contents/sections/satelliten.md
contents/sections/satelliten_2.md
contents/sections/scatter.md
contents/sections/schaltnetzteil_1.md
contents/sections/schaltnetzteil_2.md
contents/sections/schwingkreis_1.md
contents/sections/schwingkreis_2.md
contents/sections/sendeleistung_klasse_n.md
contents/sections/sender_messungen.md
contents/sections/shannon_hartley_gesetzt.md
contents/sections/sinusschwingung.md
contents/sections/snr_rauschzahl.md
contents/sections/spannung.md
contents/sections/spannungsmessung.md
contents/sections/spannungsquelle.md
contents/sections/spannungsstabilisierung.md
contents/sections/spannungsteiler_1.md
contents/sections/spannungsteiler_2.md
contents/sections/spannungswandler.md
contents/sections/spiegelfrequenzen.md
contents/sections/spitze_effektiv_wert.md
contents/sections/split_betrieb.md
contents/sections/sporadic_e_1.md
contents/sections/sporadic_e_2.md
contents/sections/sporadic_e_3.md
contents/sections/sprachsignale.md
contents/sections/sprungdistanz_1.md
contents/sections/sprungdistanz_2.md
contents/sections/spule_1.md
contents/sections/spule_2.md
contents/sections/ssb.md
contents/sections/ssb_2.md
contents/sections/ssb_3.md
contents/sections/standortbescheinigung.md
contents/sections/statische_aufladung.md
contents/sections/steckverbinder_bnc.md
contents/sections/steckverbinder_pl.md
contents/sections/stoerungen_elektronischer_geraete_1.md
contents/sections/stoerungen_elektronischer_geraete_2.md
contents/sections/strahlengang_aufenthalt.md
contents/sections/strom.md
contents/sections/strom_spannung_messung_2.md
contents/sections/strom_spannung_messung_3.md
contents/sections/strom_spannung_speisung_1.md
contents/sections/strom_spannung_speisung_2.md
contents/sections/stromkreis.md
contents/sections/strommessung.md
contents/sections/swr.md
contents/sections/swr_2.md
contents/sections/swr_3.md
contents/sections/swr_meter_2.md
contents/sections/symbole_symbolrate.md
contents/sections/tote_zone_2.md
contents/sections/transistor_1.md
contents/sections/transistor_2.md
contents/sections/transverter_1.md
contents/sections/transverter_2.md
contents/sections/traps.md
contents/sections/trennschaerfe_2.md
contents/sections/troposphaere.md
contents/sections/troposphaere_2.md
contents/sections/troposphaere_3.md
contents/sections/trxmodulation.md
contents/sections/ueberlagerungsempfaenger_einfachsuper_1.md
contents/sections/uebertrager_1.md
contents/sections/uebertrager_2.md
contents/sections/uebertragungsleitungen.md
contents/sections/uebertragungsleitungen_3.md
contents/sections/umwegleitung.md
contents/sections/unerwuenschte_aussendungen_2.md
contents/sections/unerwuenschte_aussendungen_3.md
contents/sections/verkuerzungsfaktor_1.md
contents/sections/verkuerzungsfaktor_2.md
contents/sections/verstaerker.md
contents/sections/verstaerker_klasse.md
contents/sections/verstaerker_wirkungsgrad.md
contents/sections/vna_1.md
contents/sections/vna_2.md
contents/sections/vollweggleichrichter.md
contents/sections/vor_rueck_verhaeltnis.md
contents/sections/vorverstaerker_daempfungsglied.md
contents/sections/wasserfall.md
contents/sections/wechselstrom_leistung.md
contents/sections/wellenlaenge.md
contents/sections/wellenlaenge_2.md
contents/sections/wellenwiderstand.md
contents/sections/widerstand_materialien.md
contents/sections/widerstand_ntc_ptc.md
contents/sections/widerstand_smd.md
contents/sections/widerstand_toleranz.md
contents/sections/widerstandsfarbcode.md
contents/sections/yagi_uda_3.md
contents/sections/zehnerpotenzen.md
contents/sections/zeigerinstrumente_ablesen.md
```

## 3. Traçabilité et limites

- Branche du générateur : `fix/formula-presentation`.
- Commit de la branche examiné : `fa6ca9fe105a0159b3f3c1137051722197f01f2a`.
- Commits de référence : `9301006` (documentation), `3618738` (rendu contextuel), `fa6ca9f` (mise en page près des illustrations flottantes).
- Analyse et stratégie détaillées : `doc/FORMULA_PRESENTATION.md` dans le dépôt du générateur.
- Rapport de détection historique : `tmp/formula-presentation-20261030/report-v3.json` dans l’espace d’orchestration local.
- SHA-256 du rapport : `e5512a79d21b96b21f6a0754f9f4b748c8bf0eec9335ba05b6663e0a48446f58`.

L’inventaire est fondé sur les pages HTML historiques, puis relié aux noms des sources Markdown. Il ne conclut pas à des erreurs de contenu mathématique, ne vérifie pas la signification des indices et ne couvre pas les PDF. Les corrections de police peuvent également concerner des réponses aux questions ; celles-ci ne sont pas des fichiers Markdown pédagogiques et ne figurent donc pas dans ces listes.

Les chemins canoniques actuels ont été résolus séparément à partir des métadonnées des objets, à la révision `495ce8dcb75383176370fd3537e2881f02bd4ffd` du dépôt de contenus. Aucun contenu, code du générateur ou site publié n’a été modifié pour produire cet inventaire.
