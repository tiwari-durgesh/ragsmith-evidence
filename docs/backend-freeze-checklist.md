# Backend freeze checklist — engineering inventory, not a study lock

Recorded after implementation commit `5d4c1a6`, before any new candidate-pool
access. This file is a new engineering checklist, not a preregistration amendment
or an edit to the public preregistration manifest. No selection is authorized by it.

## Two freezes required by the existing order

**Before source-pool/development selection:** lock the approved specification,
source-only inventory/exclusions/groups, complete question-only candidate pool,
code/dependencies/model/prompt/packing and deterministic allocation procedure.

**After locked development labels and dev-only calibration, before evaluation
materialization/run:** lock the chosen threshold receipt, predictions/candidate
cache/runtime identity and development provenance. A threshold cannot be fixed
before the development data needed to select it. The project threshold is still
unset. The private first-feasible evaluation reservation must not change because
of calibration outputs. None of these research input locks exists yet.

## Required private file inventory (not created by this checklist)

For each named file below record its exact path, byte count and SHA-256 in the
private study freeze; record a parent canonical-manifest hash as well. Hashes are
**pending/not frozen**, not invented or filled from pilot outputs.

| Required file/artifact | Required contents / current state |
|---|---|
| Trusted raw source | Only pinned `tatqa_dataset_train.json`, 12,845,647 bytes; SHA-256 `2df6e722cdbaaa37efcbfb280f5c9a15be29a6ec18f618ef936fe63cc6d07c69`. No dev/test split substitution. Byte check deferred to final source-only count. |
| Source projection and exclusion registry | Whole tables/paragraphs, normalized table hashes, nine pilot source matches, eight families/names, prior unresolved exclusions; exact source-projection/count tool hashes must be recorded at final feasibility step. |
| Graph and exclusion ledger | Every context/group, connectivity proof, source-backed names and scores, transitive quarantine; no labels or model outputs used to form groups. |
| Complete declared retrieval corpus | All whole excerpt snapshots, source versions, SQLite bytes, context/group map and scope map; never gold-selected cells or narrowed after outputs. |
| Candidate source-only pool | Human authorship, final questions/requirements, source anchors, adjudicable strata, units/entity/period and unique underlying fact IDs. Pilot-question duplicate screen is separate/private. No pool created now. |
| Joint reservation/development export | Canonical pool hash, seed/streams, 4/6 groups, five cases each, fixed mixes and first-feasible selection; evaluation IDs remain private/reserved. |
| Blank primary/reviewer templates | Identical source/questions/requirements, distinct independent returns, no conditions/other labels/model outputs. |
| Locked development labels | Template/input/source/selection hashes and immutable primary originals; unresolved gold blocks calibration. |
| Locked evaluation labels and reviewer originals | Source-based independent returns, pre-adjudication raw agreement/kappa, resolutions retained. All 30 require a second human before paper results. |
| Calibration inputs/result | All 20 dev predictions including failures, fixed grid/objective/ties, label/selection hashes and chosen threshold receipt; never evaluation or pilot calibration. None produced now. |
| Runtime/candidate cache | Pinned identity, prompt/chat format, tokenization/version hashes, shared candidates, immutable successes/failures/claims, full generation audit; real cache not produced now. |
| Final run/results | Ordered requests, complete denominator/failure records, byte-identical corpus/requirements/packed inputs across policies; no rerun/tuning to improve a case. |

## Runtime constants to verify before any authorized real run

The already approved fixed answerer is Qwen2.5-1.5B-Instruct Q4_K_M. These are prior
recorded artifact pins, not binaries re-downloaded or re-executed this session:

| Artifact / setting | Required value |
|---|---|
| Model SHA-256 | `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e` |
| Server SHA-256 / build | `f914f66e4886d3eb6dba76c0285a26d07b3943ac93152d72b470fe3d87ece41c` / `b6096-fd1234cb` |
| Tokenizer SHA-256 | `5126b4ed092a216b398d1487cbb3ae2a430bbce9e785f092b917719fcc06aa94` |
| Seed / temperature | 1729 / 0 |
| Context / input / output | 4096 / 3200 / 384 |
| Threads / slots / batch / microbatch | 6 / 1 / 128 / 128 |
| Confidence | exp(mean raw value-token log probability), no self-reported substitute |
| Threshold | **Unset**; only a later locked dev-only result or explicit always-abstain fallback is valid |

The older `app/runtime-manifest.json` is historical demo metadata and is not a
current research lock. Its demo 0.5 constant is not the runner threshold. Verify
all actual binaries, source artifacts and current code bytes at the real freeze.
Python 3.12.14 is tested; Python 3.11 remains unverified.

## Pre-run checklist

- Confirm authorization and genuine quota feasibility. If evaluation 9 partial/4
  conflict, development 6 partial/3 conflict, or joint group/cap/mix constraints
  cannot be certified, STOP for another amendment; do not weaken rules.
- Verify all protected document hashes and source/code inventory, including any
  later feasibility tool. Confirm `git diff --stat 1b0df45 HEAD -- src` is empty.
- Confirm approved exclusions, complete source scopes, no duplicated underlying
  facts, source-only authorship and fixed seed/priority/lexicographic ordering.
- Check each required private artifact above has a real hash and parent link;
  a pending field, mutable source, unreviewed label or stale code inventory blocks
  a research lock. Never treat content groups as independent report families.
- Validate and lock labels; keep primary and reviewer originals blinded until
  independent returns are locked. No LLM substitute for a second human.
- Calibrate only with all 20 locked development cases, fixed grid and tie breaks;
  freeze result and parent hashes before materializing reserved evaluation IDs.
- Confirm identical explicit decomposition, scope, packing and candidates across
  policies; exact model tokens in a real model run, no clipping, retries or repair.
- Preserve preparation/generation failures and missing candidates in denominators;
  keep confidence-not-run distinct from a successful abstention.
- Run the full tests, capture current commit/dependency/runtime hashes, and stop
  on a mismatch. Archive one descriptive result/failure set without tuning.
- Keep labels, raw data, model files and caches private/uncommitted. No push is
  authorized. No independence, generalization, superiority or performance claims.

## Current code/specification inventory

SHA-256 below is over **exact committed Git blob bytes**, avoiding Windows CRLF
checkout ambiguity. A future run must also hash the exact deployed working files
and record any line-ending normalization. This inventory excludes itself to avoid
self-reference; its final whole-file hash is recorded in the session log. It is
not valid for unrecorded later code changes. Tests are included for verification
provenance; presentation files are included so the demonstrated contract is fixed.

| File | SHA-256 of committed blob |
|---|---|
| `.gitignore` | `2718b353d212a642cc13dc6e44a27de6fcc7348dcf42dc645ab05f7a94708156` |
| `app/__init__.py` | `0a868b462a1977ca23ed8ad2e8c41e7bd958051ac1e4e1cfcd45d338c7fd32a8` |
| `app/checked_service.py` | `13d41a229213e84add7b093a4dc45269a0df6b256a53c31f2b87ff6220a435f0` |
| `app/contracts.py` | `931f32da7f98fb56de36743d8b96ba3215b8820c48a1f4d1731502c15eb0c45b` |
| `app/evaluation_runner.py` | `ef9f4ceba423c0237ffb146de05506387680943b442b575bf6011ac625095803` |
| `app/example-request.json` | `983fedc082fefc84d192622ad29c147ca183da3b90cd98de91d5ce022912c29a` |
| `app/frontend/__init__.py` | `3b4fdadc97aa545018a57174526d1e7bd13f1112d7123be375b7bbda213aa8e1` |
| `app/frontend/how_it_works.html` | `056c61ab4d8a5081f7ee0033078fe9c10f15a78f61fecfeb98d4fc18299d088a` |
| `app/frontend/requirements-lock.txt` | `04263f16cb3a92e28ee3903286398e50562d09cb1dface7d33c19617d84f24c8` |
| `app/frontend/requirements.txt` | `ffc2d10a0a1ceabbba8a5a5d4c54467e70dc387a96944c2474e3436a8e0e07de` |
| `app/frontend/streamlit_app.py` | `a3f514d252496ba803822c9ac9a7502138c733604de308c1b71b1456f708b608` |
| `app/frontend/theme.css` | `06f0e2fd313d7e4d22ec07e7db159a6bcd6381a21c1149c445249c918dc3322c` |
| `app/frontend/view.py` | `f80c7a595b0625c0322cb8a95055e20e47b913fae095f677d920271adeb973c1` |
| `app/main.py` | `8342dd5bf0e914eedd7f58766e76aa86da4fed6f03cb458785b941129108d36f` |
| `app/models.py` | `965b8569ff858f0d7954c308b30c3ec3d29ed0012ea6c006770d2a9bde8cc88d` |
| `app/prepare_samples.py` | `d1b429a5206685d83dee2e2a81116e408884fe7fb99b0603744792929a196e41` |
| `app/requirements-lock.txt` | `587baf237e5a973258987418f0cc9501adb8bc393485aed78127432a60c43281` |
| `app/requirements.txt` | `95bc44a621676f2d1985d9f7a184ec0a3bab2d358a02018c5714a7a3e680108e` |
| `app/research/__init__.py` | `b9de258a4953c86c3572c86f933970d5a3168e62f0640fe38800254404d07edb` |
| `app/research/calibration.py` | `906c42a36ad91a7b3e1f1ed2b36cc7e06b4cde0b79df4553f1c69a7f853d472b` |
| `app/research/corpus_runner.py` | `7af724c28d7d22b9a0024f61d3159193af268a56c3b2e7870fdfbda63739dc56` |
| `app/research/labels.py` | `c88f9d97b880f5ef0a628329b3b1276c54ef1081295907a3b934aa932c25f113` |
| `app/research/selection.py` | `c40d5649c67adb9e36f8046bda93a8ddd3e2f63ad741cbb939214f716affe68e` |
| `app/runtime-manifest.json` | `3da91ffb2fecb5e53bee61a17d958ea4346ba734dc4cdfca5f4c5a9ddaf27ed9` |
| `app/runtime.py` | `dc9c6c3a643562e78e0640030318334972fa104542148dec72f647f6308c535c` |
| `app/service.py` | `ac45096973640b2ee3e769bf0105ff7c05da3f9bf2b91616c8ab0e178290aee5` |
| `app/start_runtime.py` | `ae6c65ccf02e65e8cecf159cc8bef15b0482ba058e8f7b82398939fda2aa5392` |
| `configs/assertion_request.json` | `9cc2211af1e463ec5b67cf0db320a720a4bdd56040bb06608794c338a356bba3` |
| `configs/database_question.json` | `d80764a4490393add21e4b65ad879fbcc70a4b8228de211511bc49cdb8b90b73` |
| `configs/lookup-disabled.json` | `725fc4317d80fa91d836808611baaf3a7bd9408568d91b9423a72bae140e895f` |
| `configs/lookup-enabled.json` | `441baf12208741a0599a4ef58cf66fb687a42b25b60af1195d0ffc3b306600cf` |
| `configs/lookup_question.json` | `82af5081f5827d907d4c83867230dc535fd24be53e054a41d9d0fab50cadaff5` |
| `docs/first-real-evaluation-feasibility-amendment.md` | `7f415456e8a5e311c25be5b5551d7cd92cab48b33a5bd87f127944acab8a7316` |
| `docs/first-real-evaluation-preregistration.md` | `ea37f67d415a00ab4ec0c3997429dd50988c0d78dfeb3a03355bbdca2457acd6` |
| `docs/first-real-evaluation-selection-amendment.md` | `8344da17d4e4ed29bbafc71ca7f3e298c776eceeade9697f27e46ce727fdf629` |
| `docs/first-real-evaluation-smaller-model-amendment.md` | `982d85c29dc1c3e921d695ca5383c3e00314bc7c3d2b1bd6713cab45ea374c92` |
| `docs/option-c-excerpt-corpus-amendment.md` | `78eca0bab6ce0f21c4310dc44508b2f4f09cada0a48778ce17260ad79c56c3d2` |
| `docs/preregistration-public-manifest.json` | `bf433bc7dcb8ea572a45ab671f5ec1c7efa9c34b947b90938fc37137722dd023` |
| `docs/report-identity-trial-exclusions.json` | `dd40e35127e3c7d16c534693bcd7497d2e0ac4f6ce31afebfe51ed3bca790dec` |
| `docs/tatqa-scope-audit.json` | `a69acea76f18ceac9e8c351f0b42e2a12ebfee7d5afd22eb543fea00fd43f143` |
| `docs/thirty-question-reduced-scope-amendment.md` | `2e13cf2db8e8270c2830ea524b1e430f5b3b968d2b98ee48beed3651cc70807d` |
| `pyproject.toml` | `a92bf917e0cf82cf20f9a3cd306d228a7b4bfc86306c942dcd44519e507a1ed2` |
| `scripts/annotation_agreement.py` | `7a3ecfc898387a078dbc2c762bfedb63a7f293735d78b0fd1de72aa2372869e5` |
| `scripts/audit_tatqa.py` | `f20a77a9cc8e65d1da63cc5b2aee8fbca08996825191078eaf28cf9ec2262ea3` |
| `scripts/bind_tatqa_cells.py` | `87675f6f161825c4659579554377bfdb3ac7793aff7f43e0d9b80a2079b24483` |
| `scripts/build_pilot_families.py` | `1d803afd5c32c30100e02501bde20437c1c43c4047b0babb70ea08d0ed46c838` |
| `scripts/check_qwen15_logprobs.py` | `2d74d88eebc3fd34fa8de21c0c00bd60328fdd1d9f2b9a24cbd39a900f7e3db4` |
| `scripts/count_tatqa_feasibility.py` | `4e8e83ce7d87d3d4fd9ec80b8a0c88c253b256d4a4ca35b362b72d18880397f9` |
| `scripts/download_qwen15_smoke.py` | `b4cf114f4a3f308118138d1667a267de9afc39cff279b815748f69a1ca5d8934` |
| `scripts/download_smoke_assets.py` | `a2b2192904fc6bed9e32ef65f4a08f8d0db361258e9bdef29f2525aaba8b52cf` |
| `scripts/evaluate_synthetic.py` | `b8a3ebce84ecf0fabdfc1ffcbc9a442808824b9206ff957413f3585b086fd0b3` |
| `scripts/label_pilot36_llm.py` | `80ffdcc2be69b2d7cd08ac9a0f7acf2e583c986fa2632459145c14755b7eff26` |
| `scripts/measure_resources.py` | `16f72754315e0c90ef2a7fbd40113d1469ed63d07575570c149121dbdab04b1e` |
| `scripts/pilot36.py` | `5b0547068d1e2b3950ddbc8d989352e5504b243d0116901c1b32d6d179137d44` |
| `scripts/prepare_evaluation.py` | `f7b4acb3a90793301477771ab2701a308d81115efbb7e952c34767341c9e182b` |
| `scripts/prepare_minimal_pilot.py` | `544f47036cb1934109826f4525f6ef319d31e4db0235096cf93a9f690faad039` |
| `scripts/screen_tatqa.py` | `cb7d7c23e32e3c6ba84d0a655ccf7c056010077fabb6fb027c45a23e643cde6b` |
| `scripts/smoke_local_qwen.py` | `be7bdb37ab0f670efdf7dd28a8e7eacfe1f5ef571c07f408f7b1defc5677ad75` |
| `scripts/tatqa_excerpt_ingestion.py` | `194c38817c27cf58053f92d9d47cb61b0450d05a7c2ec0f95f5ca010b9f30e12` |
| `src/ragsmith/__init__.py` | `d229f2a2bb8cda74909e99ba55894ca3177de24e8b4cc28fe10c06f3e1780871` |
| `src/ragsmith/cli.py` | `1b409134f96761d88562845e4d99eb7247a8db9db9f745fee3f30b2ac6db730a` |
| `src/ragsmith/core.py` | `0753c3bea33a936bf29d56d1e1a4ab0a034fb683426ec7a0907c96757a1727e7` |
| `src/ragsmith/evaluation/__init__.py` | `929601d1e8c42fc0f7687d803f6309f7618343cd544f056fa30eb8fa3a05e56c` |
| `src/ragsmith/evaluation/agreement.py` | `2ca489db9828bd598d6bbd608bc6afa1e9e2e30bd961ffe64c28dbc8e8d225f2` |
| `src/ragsmith/evaluation/cell_bindings.py` | `5db69933e689cf54b1b97df5190fea33f79975159c896fb71d0276ec0ebf9269` |
| `src/ragsmith/evaluation/corpus_audit.py` | `c35434b8dc77efde99eada1a9f107bcf93876e193c6e71c4a99ca51c38d0cbec` |
| `src/ragsmith/evaluation/harness.py` | `de0c0640b20445e92016fa735f77caded98cba87ab16f5780e5eec6b372dabe0` |
| `src/ragsmith/evaluation/instrumentation.py` | `a1c96f685165c24009488eb8ba5e1e20c511094baf391f278699b6c306338cf6` |
| `src/ragsmith/evaluation/lineage.py` | `3f2cae1304d14860fc8e469d6fb2254cc81e038977212003105ae542b76d84ec` |
| `src/ragsmith/evaluation/pilot_families.py` | `13a5415497774cc606f79ce8d5c4aa0a2ecc0265b0a5e197e0c52e37b03507db` |
| `src/ragsmith/evaluation/preparation.py` | `712d51366b4540bfd2288077c9a879c3fbbb524fe7fd56ea77c50b517b367ba0` |
| `src/ragsmith/evaluation/records.py` | `e7dce8a29bfde6a853c909f1fd6e99882f9d60508b1a5a52e09e0784bd06740e` |
| `src/ragsmith/evaluation/resource_trials.py` | `79694012f60a7ac9a9e59a7d4b42516475a9149986302e4629b6c68d816f1f48` |
| `src/ragsmith/evaluation/retrieval_metrics.py` | `964f0a6929ed21fa0a5099ec59ddfec89e06b11a650396feee767ef3b9339593` |
| `src/ragsmith/evaluation/tatqa_adapter.py` | `60723bcd71bece9c73b2733ff1495c276bd168de00595f9939b8d4f67c6c58ae` |
| `src/ragsmith/evaluation/uncertainty.py` | `54ba69d997fd550c1ad374397dcb22485183e1bf6492df35b678c17ed9615fba` |
| `src/ragsmith/evidence/models.py` | `864da8129d3898635e05651f7071f595492d96f1d3a37051b4fe101bfc0ab78f` |
| `src/ragsmith/lookup_config.py` | `d9081eb99d887cdf8c094178420af4ba0c694e816ea550fb2645add56a950fc4` |
| `src/ragsmith/lookup_pipeline.py` | `e1044be0483c47be6bf0c852e807aa301ed454ddbb044890e3d94bd1bd329651` |
| `src/ragsmith/parsers/__init__.py` | `e31dc79f7ccd7d5654377355c16a39c7419abd0e6c68c42c8f90ae57e521458c` |
| `src/ragsmith/qa.py` | `52a0f04a627c534241d13100e96302a5711464dbcb8eaab6bbe0e028aecaf910` |
| `src/ragsmith/response.py` | `56dd60d459c6ef6c4457031a732c2f1fced37341dc8ac58f8552a4ba4b056932` |
| `src/ragsmith/retrieval.py` | `4a3e50b05d720be38f7cb18f9fac8b267d4192ec95a8ab3a0617728dbb77dd3c` |
| `src/ragsmith/sufficiency/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `src/ragsmith/sufficiency/aggregator.py` | `15176cf024cb8287260bacd28b51431e993deaa7893e1ee57d6a474026b8ee7d` |
| `src/ragsmith/sufficiency/assessment.py` | `7f4fa6972d72d02a42940b4a5bda0fe33791c20e4c6184cd00df567310ef84da` |
| `src/ragsmith/sufficiency/coverage.py` | `21a7300a76394cd8b5c20818f81886addc9a374d2a70882d3aa9c1ed99a3a312` |
| `src/ragsmith/sufficiency/decision.py` | `415e0602ac771c4c113f499ed5d25dba13809edad2a3616c9c25c4eba407ab05` |
| `src/ragsmith/sufficiency/evaluator.py` | `0bc18a2ef5ed3c461f429f8aa5b3513efe87eaa40f2014bf2f77f81d6db474d2` |
| `src/ragsmith/sufficiency/evidence_quality.py` | `581af1c994c71260d82a69d7266c9ba1f8f8fe878cd3ca4d252a4f572efeafcb` |
| `src/ragsmith/sufficiency/judgments.py` | `96187a93be1d8db81a7a269c900feeaeabcfa84c7040b751769510f456e0bd95` |
| `src/ragsmith/sufficiency/models.py` | `82bf47b93e734e2c2a5e046532797d6c95cb10193817321073808cfe51aa120e` |
| `src/ragsmith/sufficiency/numeric.py` | `ea525ccc1b0693be8fc4d7841b0a31a35dbfebf7d4b2205fff410c8e58247297` |
| `src/ragsmith/sufficiency/pipeline.py` | `0cc051ebec7cd2777f1abc4823cdca221da47c578a3373cce60c3beef6e19ea0` |
| `src/ragsmith/sufficiency/provenance.py` | `fae34c130ca54a2ca74ac9541eec36914afa8757c6a85cfcbda62bfffc9e4b37` |
| `src/ragsmith/sufficiency/provenance_validation.py` | `16a9f236dfe56b3e95b0ae54678ee8a2b7b97d945dd0656bff8606593c50adf8` |
| `src/ragsmith/sufficiency/quality_summary.py` | `a4f3d534ad8ca642f8dd12046119b555e5b8eb856afaad6bf8ad2ed8a33fbdfd` |
| `src/ragsmith/sufficiency/question_assessment.py` | `359b122116db746f71bfd5bd9a78cd76c4d739cda3b83918ece5900bf7083302` |
| `src/ragsmith/sufficiency/reporting.py` | `761bba079c9df4a4ae9084559795909d1d21cb2358a6936e15c0f4dbeb782486` |
| `src/ragsmith/sufficiency/requirement_quality.py` | `b9bd6fb63a4727595d51f604de50a3306e590d1e2a045317b24c3697e3c95559` |
| `src/ragsmith/sufficiency/results.py` | `8f4d2bde2a1569cb51704c40c7b3f5e8cfe2542fa95d67043eac0d1191db4089` |
| `src/ragsmith/sufficiency/structured_verifier.py` | `847b1b8113087bfa437c27dc37c2753654ea7989e8cf378df8480e6e8ccf6630` |
| `src/ragsmith/sufficiency/traceability.py` | `4f72a817665078b9fb9030eced9e5dd30c4ef2d034b774ac052c8025fcedf2d3` |
| `src/ragsmith/sufficiency/verification.py` | `a182219df5d30c93c9eab3a0492876bf2b18e5eff7b9403ea54fbba325193c47` |
| `src/ragsmith/supporting_citations.py` | `f226875dbcc80e7d4d8f3a8f7f5509401bd9fdfbd9a63a594e95268233e25569` |
| `src/ragsmith/value_lookup.py` | `238b6cca2c3a87bcd2efacf7220091a6817f8b4a04b51f392aa13f8a12df8321` |
| `tests/test_answerability_decision.py` | `99f37ca96acdd65e4a28bfb8888c87ad1515a732c6b7930e730ec10e6f5b3d89` |
| `tests/test_assessment.py` | `aefbc04c8024c3fba6cdc0fc8ab197f2dd97554e9a6d4a4af7d943ed6bb75ea4` |
| `tests/test_assessment_reporting.py` | `66234feef3d766528042ffd4163fe58b40fada8398f9649f591e2f90877ca5c3` |
| `tests/test_cell_bindings.py` | `790dc8a90c3eb4d41f71a38be8dfa71052879bc20cfbd487267848fa1c1095bf` |
| `tests/test_corpus_runner.py` | `5eab8915296ca2b51307ac9bf8b1a47371142ad4369aa2c283f1fe42bb1e3d7e` |
| `tests/test_coverage.py` | `f8817f98675e1b3c4a9781d45fd004dca514d87b36fc2866fd64e407911cba69` |
| `tests/test_demo_api.py` | `f3fd28adaccb881a4e5c88610bd5ceb6644d443cd0d7c6e7422d5d754a252cfc` |
| `tests/test_demo_runtime.py` | `2566ed99601f855ff9749a32ec85f5f11a964433ec1a993f0e39c1793c8a789f` |
| `tests/test_demo_runtime_cache.py` | `16a238952f801edc402774563dc6807651d857e0526f7c0bf465ca72e9efc24f` |
| `tests/test_evaluation_foundation.py` | `2da9622b1c8b0d0c68c43be13235c9d7fc8990894371f87660800535eda68044` |
| `tests/test_evaluation_lineage.py` | `d40ec0879e5ae1a0daeaef407e441a8c92330c6bda31f8ea3092f91ede1e084a` |
| `tests/test_evaluation_measurements.py` | `fb6e69b58f428e5a86d838316e80e83cd547070511bb50458aa7c6a8bcf543cc` |
| `tests/test_evaluation_preparation.py` | `60f044bbfc1e8827e93504f3abb59aadadd014e2a19fce60286547265d869526` |
| `tests/test_evaluation_runner.py` | `88a77398d799187c197f8dbbc01b0f538577cf1b7f91503cdd8c925006b171aa` |
| `tests/test_evidence_models.py` | `8302b5dfe2e864f8732c0e12ea332d1037874d294eda38b4accaaa339bea2252` |
| `tests/test_evidence_provenance.py` | `9d214deabcc0069cd3b94177ce2326f720d3b34f100539bbd910478a0f2a5d7b` |
| `tests/test_evidence_quality.py` | `9303b7b0c7c0f12322c252599cb3ecc5c3e124abed0a4ae56f16093f675fea70` |
| `tests/test_evidence_traceability.py` | `8d1903a1ff6d40b71fa3b0cda25c2d8d8294f8ef888ebd2ecf4aed0ffe16beb6` |
| `tests/test_evidence_verification.py` | `eca3b29fa21b05d69a8015f28b0fee1290545270ca84a15d1f657d9160564d30` |
| `tests/test_excerpt_ingestion_external.py` | `a56969f906f899cb07efc3adeab9c81afcd55ad629de83a03fe411e6023fbf09` |
| `tests/test_final_assessment_integration.py` | `256ae0a95e249853162bd34539a91f08368728889dc171c21d7edcace185c8f5` |
| `tests/test_frontend_app.py` | `6e0333c0bb1f0c615bee77ec3c3ea1335d2e6145e9c6c5bf2cb6c10b43230f22` |
| `tests/test_frontend_view.py` | `f6ad856192fae7fa56ac0747ed9ac199e066aa2ca28ba95d94e01b15ea28813e` |
| `tests/test_judgment_aggregator.py` | `e7f141d1114e5ae21fc79c4bafce3e7e526b767baa5031f87fc209eed59940aa` |
| `tests/test_lookup_pipeline.py` | `9c269b884c61c19d88a3fc1900cd327324dd9252b3bf411bbeea59f570f49227` |
| `tests/test_numeric.py` | `be113d9ca0d84708b47a3f43a435a11d11d09a6a1182825bcc11a6799bf7a3fd` |
| `tests/test_option_c_selection.py` | `61017c11cd710eaf6e1296aaca8cafc9f6a9638af9ee2d7c0d1ba64b930b6632` |
| `tests/test_pilot36_scripts.py` | `452862ba40452069b8a5da31c312c8c0e7e7f6ab7c4e774c8899e4289e6d2f11` |
| `tests/test_pilot_families.py` | `eed8ad76f0d9475998613fa2539e9617132fb3d601b37e9679145167cf135d9d` |
| `tests/test_pipeline.py` | `4fbb0a6300ecb35323534e9346283767f78522bf8e63c1f95416d77607ba3c8b` |
| `tests/test_provenance_validation.py` | `6cd033959e6c8e7ad92769edb7f1175fe7356fe271c77f41dc7e2c9aa29ac1b9` |
| `tests/test_quality_summary.py` | `82fbf7b6e2419ec9632ef98ff952bf73fd4d1efc2cdcf66850a6181bfca0406f` |
| `tests/test_question_assessment.py` | `6ecb91b914f75791ad91f1a6cdb3cf34a0ab6ac1e528f6b06cdda7ed8360cb14` |
| `tests/test_question_requests.py` | `30eacc75a392009959f5df3cf62401814cb4ca25eaad55994addd19972274d64` |
| `tests/test_requirement_models.py` | `b3bbd47c942b79e11573fd7077abf97ed5d01e7e092628dfda8d49a529562721` |
| `tests/test_requirement_quality.py` | `6fc0b9d706f56e8efbb5eae8c0febe3985bf2d320969ce8d4879a62f0e5a416d` |
| `tests/test_resource_trials.py` | `4a4e58f01ea187302a2bd32ebb70bceb6b6df71dffd4888499c7155eb7aa8922` |
| `tests/test_response.py` | `1097b49bd3b9915363cd745aee83341847afb9b3f8ca682f0853bdeab4c8e529` |
| `tests/test_retrieval_integration.py` | `fec495b5395d533553edf8ec49da10b38bdfac6202d111c11c2c2a409dc2501d` |
| `tests/test_shared_contract.py` | `2f4a82fb696949061dc58d918c16a84b00aeed3158fac0fd6751e13f59ffd34d` |
| `tests/test_structured_aggregation.py` | `4939f39c8fb1e378195bf0adf8ab69be0f9cb97e907563b248887d5c2e2e0ae3` |
| `tests/test_structured_verifier.py` | `21924ea3c0fe448bd465da9f20e2f6c855fe56de600f10522c9e28d5292db610` |
| `tests/test_study_labels_calibration.py` | `8daae7a84e52b43cc71b4eb4c4f20c93d7c26fa6be0a8009bd237fdd0dda45be` |
| `tests/test_sufficiency_evaluator.py` | `2afa22d5324718cf17cc2f590361d8ff78e451183fa3deb1c74f703212a20ae2` |
| `tests/test_sufficiency_pipeline.py` | `5078aac2b372a10914ca05f00fda979ddec74167ab14dbb7308e8f8d8a843e2f` |
| `tests/test_sufficiency_results.py` | `d8cacd33aa535921fdedb513cc65b0f85b9b02bd9ffa2719520c3b7d2008c191` |
| `tests/test_support_judgments.py` | `1f1309dc84df3b2f0b2471bbd4af083cda82d8b0370347f9ced60b00208b2a91` |
| `tests/test_tatqa_adapter.py` | `a2fc272891995b67dd78479d7dd023ea8fff96b39417443559d56610e3d73128` |
| `tests/test_value_lookup.py` | `b72e44c4f6daf8a908c69cca0ef4019262ea40ab5a53d20d2ce97e0d205bdca4` |
