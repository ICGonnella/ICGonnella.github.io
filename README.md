# Sito personale di Isabella Carla Gonnella

Sito statico in inglese, compatibile con GitHub Pages. La home comprende solo About & Research e una selezione di pubblicazioni e preprint. L’email è nella barra laterale, insieme ai profili accademici. `cv.html`, raggiungibile dal menu CV & Info, contiene il PDF scaricabile e gli annunci dei prossimi eventi organizzati. `publications.html`, raggiungibile dal menu Publications & Preprints, contiene l'elenco completo in ordine cronologico dal più recente, senza raggruppamenti per tipo. Non richiede Node, librerie esterne o un database; i contenuti restano accessibili senza JavaScript.

## Anteprima

Apri `index.html` direttamente nel browser, oppure avvia dalla repo:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Visita `http://localhost:8000`. Con il server locale è disponibile anche la copia automatica del BibTeX; se il browser non consente l'accesso agli appunti, il testo viene selezionato per la copia manuale. Il download `.bib` funziona anche senza JavaScript.

## Aggiornare i contenuti

- `data/profile.json`: biografia, supervisori, contatti, percorso del CV PDF e prossimi eventi (`upcoming_events`).
- `data/publications.json`: pubblicazioni, autori, date, DOI, identificativi arXiv e stato.
- `templates/index.html`: struttura condivisa, profilo e navigazione.
- `templates/home.html`, `templates/publications.html` e `templates/cv.html`: contenuto delle tre pagine.
- `assets/styles.css`: aspetto grafico e layout responsive.
- `assets/site.js`: navigazione attiva e copia delle citazioni.

Dopo una modifica ai dati o al template:

```sh
python3 scripts/build.py
python3 scripts/check.py
```

Il generatore utilizza solo la libreria standard di Python 3. Rigenera `index.html`, `publications.html`, `cv.html`, le citazioni in `files/`, `robots.txt`, `sitemap.xml` e `.nojekyll`. Non modificare manualmente questi file generati. Conserva gli ID delle pubblicazioni esistenti: sono usati per i riferimenti alle citazioni.

Per aggiungere un articolo, copia una voce in `data/publications.json`, assegna un `id` univoco e aggiorna i campi. I tipi supportati sono `preprint`, `article` e `incollection`. Tutte le voci sono ordinate per `date`, dalla più recente, indipendentemente dal tipo. Imposta `selected` a `true` sui lavori da mostrare anche nella home; impostalo a `false` o omettilo per mostrarli soltanto nell'elenco completo. La selezione comprende il lavoro sui Wasserstein gradient flows, quello sulle perturbazioni stocastiche e il lavoro con Giacomo Venier sul polynomial chaos. Quando un preprint viene pubblicato, aggiorna la stessa voce con tipo, anno, data, DOI e rivista, conservando l'identificativo arXiv.

La barra laterale contiene l’email cliccabile, Google Scholar e LinkedIn. La pagina CV & Info offre il download di `Gonnella_CV_05032026.pdf`, configurato tramite `cv_file` in `data/profile.json`. Dopo modifiche al CV LaTeX, ricompila e aggiorna questo PDF nella repo: il sito scarica direttamente quel file e l’esportazione `_site/` lo include automaticamente. La pagina mostra il pulsante di download e, sotto un separatore, la sezione Upcoming events con il ruolo di co-organizzatrice. Gli annunci si aggiornano tramite `upcoming_events`; SISSA Women in Mathematics 2027 riporta per ora solo l’anno, con data e programma da annunciare. Il sito ha anche uno stile di stampa.

## GitHub Pages

La cartella principale contiene già i file statici pronti per GitHub Pages. Dopo aver salvato e pubblicato le modifiche su GitHub, configura Pages per utilizzare il branch desiderato e la cartella principale della repo. L'implementazione locale non effettua commit, push o modifiche alle impostazioni di hosting.

Per creare una cartella contenente soltanto i file del sito, senza sorgenti e proposte di design:

```sh
python3 scripts/build.py --output _site
python3 scripts/check.py _site
```

La cartella `_site/` è ignorata da Git e può essere usata come artefatto di distribuzione. Per cambiare dominio, modifica `url` in `data/profile.json` e rigenera il sito.

## Provenienza dei contenuti

La biografia e i supervisori sono basati sul testo fornito direttamente da Isabella nella conversazione. Non sono presenti conteggi di citazioni o altre metriche che richiedano aggiornamenti automatici.

Fonti consultate il 15 novembre 2026:

- [LinkedIn](https://www.linkedin.com/in/isabella-carla-gonnella-225a92213/): informazioni pubbliche indicizzate su laurea magistrale e borse di studio. La sezione Informazioni non era accessibile direttamente; il testo è stato fornito da Isabella.
- [SISSA — programma di dottorato](https://www.math.sissa.it/content/mathematical-analysis-modelling-and-applications-0/): affiliazione e corso.
- [SISSA SIAM Chapter](https://mathematics.sissa.it/en/sissa-siam-chapter-mathematics) e [archivio](https://www.math.sissa.it/content/sissa-siam-student-chapter/index.html): ruoli 2025–2026 e 2024–2025.
- [Programma YMMOR 2025](https://mathlab.github.io/ymmor2025/useful_files/program_boa.pdf): titolo del talk e indirizzo `igonnell@sissa.it`.
- [arXiv:2607.17235](https://arxiv.org/abs/2607.17235), [arXiv:2605.31288](https://arxiv.org/abs/2605.31288): preprint.
- [Springer — articolo 2026](https://link.springer.com/article/10.1007/s10915-026-03338-0), [Springer — capitolo 2026](https://link.springer.com/chapter/10.1007/978-3-032-11527-0_9), [Elsevier — articolo 2023](https://www.sciencedirect.com/science/article/pii/S0898122123003711): versioni pubblicate e metadati.

L'elenco comprende cinque lavori verificati su queste fonti. Google Scholar non era leggibile direttamente e non è stato possibile verificare l'esaustività del profilo. I testi del sito sono modificabili nei file JSON; le informazioni storiche sulle attività riportano il relativo anno.

`design/` conserva le proposte preliminari e non viene inclusa nell'esportazione `_site/`. La foto utilizzata è quella originale già presente in `img/IMG_4990.JPG`.
