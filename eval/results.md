# Evaluation results

Model: `llama3.2:3b` · Embeddings: `sentence-transformers/all-MiniLM-L6-v2` · MIN_SCORE: 0.22 · TOP_K: 4

Documents: `data/docs/sample_energy_notes.md` (short renewable-energy notes).

| Metric | Result |
|---|---|
| Overall pass rate | 19/20 (95%) |
| Routing accuracy | 20/20 (100%) |
| Retrieval hit rate (answerable questions) | 12/12 (100%) |
| Answer correctness (answerable questions) | 11/12 (92%) |
| Correct refusals (questions not in the documents) | 6/6 (100%) |
| Calculator correctness | 2/2 (100%) |
| Average latency (on a local laptop) | 0.3s |

Answer correctness is a keyword check against the expected fact, so it is a
lower bound: a correct answer phrased differently could be marked wrong.

## Per-question results

| | Type | Question | Answer (truncated) | Time |
|---|---|---|---|---|
| ✅ | docs | How does a photovoltaic cell generate electricity? | A photovoltaic (PV) cell generates electricity by converting sunlight into electricity through a process involving photo | 3.3s |
| ✅ | docs | What material are most solar cells made of? | [1] Most solar cells are made of silicon. | 0.1s |
| ✅ | docs | What efficiency do commercial silicon solar cells reach? | Typical commercial silicon cells reach 18–23% efficiency. [1] | 0.2s |
| ✅ | docs | How does temperature affect solar cell output? | Cell output falls as temperature rises. [1] | 0.1s |
| ✅ | docs | What is the Betz limit? | The Betz limit is the maximum fraction of wind energy that a turbine can capture, which is 16/27, or about 59.3%. [1] | 0.4s |
| ✅ | docs | How does wind power change if the wind speed doubles? | According to [1], doubling the wind speed gives eight times the power. | 0.3s |
| ✅ | docs | What efficiency do real wind turbines reach? | Real turbines reach roughly 35–45% [1, 2]. | 0.2s |
| ✅ | docs | What is biomass energy made from? | Biomass energy comes from organic material such as crop waste, wood, and animal manure. [1] | 0.4s |
| ✅ | docs | How is biogas produced? | Biogas is produced through anaerobic digestion, where organic material such as crop waste, wood, and animal manure is br | 0.4s |
| ✅ | docs | What liquid biofuel can biomass be turned into? | According to the context, biomass can be turned into liquid biofuels like ethanol. | 0.3s |
| ✅ | docs | How do geothermal power plants generate electricity? | [3] says: "Hot water or steam from underground reservoirs drives turbines." | 0.3s |
| ❌ | docs | What is a binary-cycle geothermal plant? | I don't know. | 0.1s |
| ✅ | refuse | Who won the 2018 FIFA World Cup? | I don't know. That isn't covered in your documents. | 0.1s |
| ✅ | refuse | What is the capital of France? | I don't know. That isn't covered in your documents. | 0.0s |
| ✅ | refuse | How do I bake sourdough bread? | I don't know. That isn't covered in your documents. | 0.0s |
| ✅ | refuse | Explain the quicksort algorithm. | I don't know. That isn't covered in your documents. | 0.0s |
| ✅ | refuse | How does a nuclear fusion reactor work? | I don't know. | 0.1s |
| ✅ | refuse | What is the price of Bitcoin today? | I don't know. That isn't covered in your documents. | 0.0s |
| ✅ | math | what is 17 * 23 + 5? | (17 * 23) + 5 = 396 | 0.2s |
| ✅ | math | calculate (120 - 45) / 3 | (120 - 45) / 3 = 25 | 0.1s |
