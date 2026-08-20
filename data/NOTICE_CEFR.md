# CEFR data notice

`studyforge/data/cefr_levels.json` is a compact derivative generated from:

1. **The CEFR-J Wordlist Version 1.5**, compiled by Yukio Tono,
   Tokyo University of Foreign Studies (Tono Laboratory).
2. **Octanove Vocabulary Profile C1/C2 Version 1.0**, created by Octanove Labs.

Source mirror:
<https://github.com/openlanguageprofiles/olp-en-cefrj>

The CEFR-J vocabulary profile may be used for research and commercial purposes
at no charge with proper citation. Copyright remains with Tono Laboratory at
Tokyo University of Foreign Studies.

The Octanove C1/C2 profile is licensed under the Creative Commons
Attribution-ShareAlike 4.0 International license:
<https://creativecommons.org/licenses/by-sa/4.0/>

## StudyForge processing policy

StudyForge expands slash-separated spelling variants and keeps a word-level
CEFR label only when every source entry for that normalized headword agrees on
the same A1-C2 level. Headwords with conflicting part-of-speech or sense levels
are omitted and reported as `unknown` at runtime. StudyForge does not infer CEFR
from word frequency.
