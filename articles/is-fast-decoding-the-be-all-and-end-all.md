# Is fast decoding the be all and end all?

*Four ways to serve GLM-5.3-Flash*

*Prose source of truth for `articles/is-fast-decoding-the-be-all-and-end-all.html`, which embeds the explorable benchmarks around this narrative. Keep the two in sync when editing.*

A high decode rate can be true and still tell you very little about how an agent feels to use. I have now served GLM-5.3-Flash four ways on the same two DGX Sparks and measured each one the same way, and the headline finding is a trade-off, not a winner: the recipe that answers fastest is not the one that generates fastest, and none of the four escapes some important constraints that matter for real agent work.

## What was compared

Four independently guarded serving recipes on the same hardware:

- **TensorFold EXL3** with IncoAI's DFlash2 drafter under two policies, `fc5:0.3` and `fnc7:0.3`
- **TensorFold MTP**, the only DFlash2-free recipe of the four
- **SparkGLM NVFP4** on its upstream 4×512k profile (which also uses DFlash2)

Each recipe was measured at one active request (C=1); fc5, fnc7 and SparkGLM also at four (C=4). MTP's fixed recipe supports C=1 only, and SparkGLM's C=4/256k cell was intentionally not run: four distinct 256k prompts unfortunately exceed its ~600k shared KV pool, I might revisit this and increase the KV pool but I was getting OOM errors when I first tried. In any case, that cell is unavailable, it's not zero, and nothing else was extrapolated from this. Every number in this piece is traceable to a raw condition in the [explorable report](https://evoclock.github.io/fieldnotes/articles/is-fast-decoding-the-be-all-and-end-all.html); the measurement families (sustained decode, prefill estimate, finite request, Tool Eval, 500k+ needle) are defined there and never mixed.

## The fastest answer is not the fastest generator

At 32k context, SparkGLM's client-observed prefill estimate was **2,508 prompt tokens/s** against roughly **1,780–1,810** for all three TensorFold recipes, and its first output token arrived at **13.1 s** versus about **17.4–17.8 s**. If your workload is "send a long prompt, get moving quickly," SparkGLM wins this setup.

But once decoding is under way, TensorFold pulls ahead. Sustained decode at 32k/C=1 measured **50.6–52.8 tok/s** for the TensorFold recipes against SparkGLM's **41.3**. At C=4 the gap widens: fc5 and fnc7 reached **162.8** and **182.6 aggregate tok/s** against SparkGLM's **71.3**, though those are timed active-generation windows, not completed-request throughput. On the same finite C=4 workload measured on a shared clock, the rates were far lower (**15.5 / 17.0 / 9.9 tok/s**) because the shared span includes staggered prefill and decode gaps. These numbers answer different questions, which is exactly why the report keeps the measurement families separate.

SparkGLM's whole-request wall times also look better partly because it frequently produced **shorter responses** (28 output tokens versus 259–339 in one 32k finite cell). A faster stop is less work, not faster completion of an equivalent answer.

## Speed did not buy correctness

The [69-scenario Tool Eval](https://github.com/SeraphimSerapis/tool-eval-bench) ranked the TensorFold recipes **93/94/93** (omitted/temperature 0/1) against SparkGLM's **88/88/87**. SparkGLM's higher numeric *deployability* composite comes from faster tool turns (median **1,403 ms** versus **2,757–2,964 ms**), not from better tool behaviour. And the finding that matters most: **all twelve C=1 runs failed TC-51's planning-order safety gate**, issuing a `send_email` before receiving the result of a dependent `create_calendar_event`. No recipe, drafter, or quantization escaped it.

The benchmark's own framing applies: it tests mock-tool scenarios; a passing score is not a safety qualification. The orchestrator must still enforce dependency order, validate schemas and required arguments, and gate consequential side effects behind approval. A benchmark score cannot, to my knowledge, easily do those jobs.

## Long context: everyone retrieved the needle, slowly

All four recipes retrieved an exact fresh code from a 500k+ prompt with zero cached tokens. But the first-token waits are the story: **225.9 s for SparkGLM** (on its shorter ~520k prompt, fitting its 524,288 limit) versus **419–439 s** for the TensorFold recipes on ~527k prompts. Speculative decoding improves generation, not cold prefill: a half-million-token cold prompt costs six to seven minutes before the first token regardless of drafter. No C=4 500k+ retrieval was measured, and none should be inferred.

## What this means for real work

For an interactive workload, the input length, output length, concurrency, and how often tool turns interrupt generation decide which recipe fits, and one bar cannot stand in for that workload. A fast-decoding recipe with a slow first token suits queued analysis and long generations. A fast-first-token recipe with lower throughput and shorter answers suits interactive probes. Neither is "the fastest"; they are fast at different things.

*Figure: the Jim Carrey "slow is smooth and smooth is fast is just something slow people say" meme, placed after this paragraph in the published page.*

**None of the four measured configurations simultaneously provides proven C=4 throughput, the stronger Tool Eval scores, and freedom from DFlash2 restrictions.** For an open-source, DFlash2-free project, TensorFold MTP is the best *research starting point*: it scores with fc5/fnc7 and avoids the drafter licence, but its fixed profile serves only C=1, and enabling concurrency needs implementation, validation, and rebenchmarking. SparkGLM's measured advantages do not solve the DFlash2 constraint (its engine is additionally AGPL-3.0-only), and no speed difference here isolates NVFP4 versus EXL3, because the checkpoints and runtimes differ too.

On licensing: DFlash2 is CC BY-NC-ND 4.0. The licensor's written reply to me covers individual personal experimentation at this stage, not products, hosted services, or company deployment. Audit runtime, checkpoint, drafter and dependency rights separately before any release or service. **Usual mandatory blurb**: This is not legal advice.

## Limits

One observation per cell, no randomization, no error bars, no matched answer-length controls. Finite replies may stop early or hit the 400-token cap; neither outcome measures answer quality. Temperature handling differs between the two APIs (omitted defaults are not guaranteed identical sampling pipelines). The full provenance, exceptions and metric contract are listed in the report and its analysis notes.

## How this report was composed

This report was composed with the help of the MTP quant, served by [Ash Hart's TensorFold](https://github.com/ashhart/TensorFold) engine.

## Credits

Everything measured on this page rests on other people's work. Per recipe:

**TensorFold EXL3, fc5:0.3 / fnc7:0.3 / MTP**

- Serving engine: [TensorFold](https://github.com/ashhart/TensorFold) by Ash Hart and contributors (Apache-2.0 from v0.6.0), which builds on [ExLlamaV3](https://github.com/turboderp-org/exllamav3) by turboderp, Hugging Face [transformers](https://github.com/huggingface/transformers), and [z-lab/dflash](https://github.com/z-lab/dflash).
- Model: [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) by Z.ai.
- Checkpoint: [Mia-AiLab/GLM-5.3-Flash-EXL3-4bpw-TensorFold](https://huggingface.co/Mia-AiLab/GLM-5.3-Flash-EXL3-4bpw-TensorFold), made with exllamav3 by turboderp; the recipe's earlier default was [brandonmusic/GLM-5.3-Flash-tr3-4bpw](https://huggingface.co/brandonmusic/GLM-5.3-Flash-tr3-4bpw) by Brandon M. Music (ShapleyMcg attribution required).
- DFlash2 drafter: [IncoAI](https://huggingface.co/incoai/GLM-5.3-Flash-DFlash2) (CC BY-NC-ND 4.0).
- Serving recipe: [MiaAI-Lab/GLM-5.3-Flash-EXL3-2x-DGX-Sparks-TensorFold](https://github.com/MiaAI-Lab/GLM-5.3-Flash-EXL3-2x-DGX-Sparks-TensorFold) by Mia's AI Lab and its contributors; it is not a solo recipe. The full contributor and prior-art list is in the repository's [CREDITS.md](https://github.com/MiaAI-Lab/GLM-5.3-Flash-EXL3-2x-DGX-Sparks-TensorFold/blob/main/CREDITS.md).

**SparkGLM NVFP4**

- Serving stack: [SparkGLM](https://github.com/Enntity/sparkglm) by Enntity (AGPL-3.0-only) on the Atlas engine, with FlashKDA (MIT), FlashInfer (Apache-2.0) and other components listed in its [licensing notes](https://github.com/Enntity/sparkglm/blob/main/docs/LICENSING.md).
- Checkpoint: [nvidia/GLM-5.3-Flash-NVFP4](https://huggingface.co/nvidia/GLM-5.3-Flash-NVFP4) (MIT).
- DFlash2 drafter: [IncoAI](https://huggingface.co/incoai/GLM-5.3-Flash-DFlash2) (CC BY-NC-ND 4.0).

**Benchmarks**

- Tool evaluation: [tool-eval-bench](https://github.com/SeraphimSerapis/tool-eval-bench) by SeraphimSerapis (MIT).
- Inference benchmark: [llm-inference-bench](https://github.com/local-inference-lab/llm-inference-bench) by local-inference-lab.
